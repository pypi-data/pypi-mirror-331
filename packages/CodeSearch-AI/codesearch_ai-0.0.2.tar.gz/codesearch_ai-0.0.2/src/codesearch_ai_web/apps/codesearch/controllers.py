from py4web import action, request, response, abort, redirect, URL
from yatl.helpers import A, DIV, XML
from .common import db, session, T, cache, logger
import os
import json
from codesearch_ai.cli.start import start
from codesearch_ai.cli.config import load_config, get_file_path, CONFIG_DEFAULTS
from codesearch_ai.assistant.index import create_file_index, process_file
from codesearch_ai.assistant.llama_cpp_embed import LlamaCppEmbed
from codesearch_ai.assistant.llama_cpp_assistant import LlamaCppAssistant
import argparse
import io
import sys
import subprocess
import numpy as np
from faiss import IndexFlatL2
from codesearch_ai.cli.models import MODELS_DEFAULT_EMBED, MODELS_DEFAULT_LLM
from py4web.utils.factories import ActionFactory
from functools import partial
import time
import mimetypes
import datetime

# Add new imports
from codesearch_ai.cli.models import MODELS_DEFAULT_EMBED, MODELS_DEFAULT_LLM

# Define available models based on CONFIG_DEFAULTS
AVAILABLE_MODELS = {
    'llm': [
        {
            'id': 'qwq-lcot',
            'name': 'QwQ-LCoT-7B-Instruct-Q4_0.gguf',
            'description': 'QwQ LCoT 7B Instruct (4-bit quantization)',
            'repo_id': 'bartowski/QwQ-LCoT-7B-Instruct-GGUF',
            'filename': 'QwQ-LCoT-7B-Instruct-Q4_0.gguf'
        },
        {
            'id': 'qwq-q4',
            'name': 'QwQ-R1-Distill-7B-CoT.Q4_K_M.gguf',
            'description': 'QwQ R1 Distill 7B CoT (4-bit quantization, smaller size)',
            'repo_id': 'mradermacher/QwQ-R1-Distill-7B-CoT-GGUF',
            'filename': 'QwQ-R1-Distill-7B-CoT.Q4_K_M.gguf'
        },
        {
            'id': 'qwen-2.5b',
            'name': 'qwen-2.5-3b-evol-cot-v2-iq4_nl-imat.gguf',
            'description': 'Qwen 2.5B Evol CoT (4-bit quantization, smallest size)',
            'repo_id': 'bunnycore/Qwen-2.5-3b-Evol-CoT-v2-IQ4_NL-GGUF',
            'filename': 'qwen-2.5-3b-evol-cot-v2-iq4_nl-imat.gguf'
        }
    ],
    'embedding': [
        {
            'id': 'default',
            'name': CONFIG_DEFAULTS['EMBED_MODEL'],
            'description': 'Default embedding model (nomic-embed-text-v1.5)',
            'repo_id': 'nomic-ai/nomic-embed-text-v1.5-GGUF',
            'filename': CONFIG_DEFAULTS['EMBED_MODEL']
        }
    ]
}

class Args:
    """Mock args object for dir-assistant compatibility"""
    def __init__(self, directory):
        self.i__ignore = None
        self.d__dirs = [directory]
        self.mode = None

@action('/')
@action.uses(session)
def default_page():
    """
    Redirect root URL to codesearch page
    """
    redirect(URL('index'))

@action('index')
@action.uses('layout.html', 'index.html', session, db)
def index():
    """
    Main page with directory selection, chat interface, and codebase browser
    """
    # Check if we have a directory in session and initialize assistant if needed
    if session.get('current_directory') and current_assistant is None:
        directory = session.get('current_directory')
        config = session.get('config')
        success, error = initialize_assistant(directory, config)
        if not success:
            # If initialization fails, clear the session
            del session['current_directory']
            if 'config' in session:
                del session['config']
            if 'index_info' in session:
                del session['index_info']
            logger.error(f"Failed to initialize assistant on startup: {error}")
    
    # Get all conversations for the current directory if it exists
    conversations = []
    if session.get('current_directory'):
        # Get conversations that have at least one assistant message
        conversations = db(
            (db.conversations.directory_path == session['current_directory']) &
            (db.conversations.id.belongs(
                db(db.messages.role == 'assistant')._select(db.messages.conversation_id)
            ))
        ).select(
            orderby=~db.conversations.updated_at,
            limitby=(0, 10)  # Limit to 10 most recent conversations
        ).as_list()
        
        # Only create a new conversation if there are no conversations at all
        if not conversations:
            conversation_id = db.conversations.insert(
                title='New Conversation',
                directory_path=session['current_directory']
            )
            session['current_conversation_id'] = conversation_id
            
            # Add system message if assistant is initialized
            if current_assistant and hasattr(current_assistant, 'system_instructions'):
                db.messages.insert(
                    conversation_id=conversation_id,
                    role='system',
                    content=current_assistant.system_instructions
                )
            
            # Add the new conversation to the list
            conversations.insert(0, {
                'id': conversation_id,
                'title': 'New Conversation',
                'created_at': datetime.datetime.now().isoformat(),
                'updated_at': datetime.datetime.now().isoformat()
            })
        # If we have conversations but no current_conversation_id, set it to the most recent one
        elif not session.get('current_conversation_id'):
            session['current_conversation_id'] = conversations[0]['id']
    
    return dict(
        load_codebase_url=URL('load_codebase'),
        send_message_url=URL('send_message'),
        get_file_tree_url=URL('get_file_tree'),
        view_file_url=URL('view_file'),
        validate_directory_url=URL('validate_directory'),
        get_chat_history_url=URL('get_chat_history'),
        get_model_info_url=URL('get_model_info'),
        download_model_url=URL('download_model'),
        conversations=conversations,
        session=session  # Pass the session object to the template
    )

@action('load_codebase', method=['POST'])
@action.uses(session)  # Explicitly use session middleware
def load_codebase():
    """
    Initialize dir-assistant with selected directory
    """
    try:
        directory = request.json.get('directory')
        ignore_patterns = request.json.get('ignore_patterns', [])
        
        if not directory or not os.path.isdir(directory):
            return json.dumps({'error': 'Invalid directory'})
        
        # Convert to absolute path and clean it
        directory = os.path.realpath(os.path.normpath(directory))
        logger.info(f"Loading codebase from directory: {directory}")
        logger.info(f"Using ignore patterns: {ignore_patterns}")
        
        # Clear current conversation ID when switching directories
        if 'current_conversation_id' in session:
            del session['current_conversation_id']
        
        # Store the original working directory
        original_cwd = os.getcwd()
        
        try:
            # Change to the selected directory
            os.chdir(directory)  # Now we're in the exact directory the user selected
            
            # Try to load dir-assistant configuration, use defaults if not found
            try:
                config_dict = load_config()
                config = config_dict.get('CODESEARCH_AI', {})
            except Exception as e:
                logger.warning(f"Could not load config, using defaults: {str(e)}")
                config = {}
                config_dict = {'CODESEARCH_AI': {}}
            
            # Start with CONFIG_DEFAULTS
            config = CONFIG_DEFAULTS.copy()
            
            # Update with any existing config values from config_dict
            if 'CODESEARCH_AI' in config_dict:
                for key, value in config_dict['CODESEARCH_AI'].items():
                    if isinstance(value, dict) and isinstance(config.get(key), dict):
                        # Deep merge for nested dictionaries
                        config[key].update(value)
                    else:
                        config[key] = value
            
            # Always update ignore patterns if provided
            if ignore_patterns:
                config['GLOBAL_IGNORES'] = ignore_patterns
            
            # Save the updated config
            config_dict['CODESEARCH_AI'] = config
            from codesearch_ai.cli.config import save_config
            save_config(config_dict)
            
            # Get model paths - use absolute paths
            models_path = os.path.expanduser(config['MODELS_PATH'])
            llm_model_file = get_file_path(models_path, config['LLM_MODEL'])
            embed_model_file = get_file_path(models_path, config['EMBED_MODEL'])
            
            if not os.path.exists(llm_model_file):
                return json.dumps({'error': 'LLM model not found. Please run "codesearch-ai models download-llm" first.'})
            
            if not os.path.exists(embed_model_file):
                return json.dumps({'error': 'Embedding model not found. Please run "codesearch-ai models download-embed" first.'})
            
            logger.info("Initializing embedding model...")
            # Initialize embedding model
            embed = LlamaCppEmbed(
                model_path=embed_model_file,
                embed_options=config['LLAMA_CPP_EMBED_OPTIONS']
            )
            
            logger.info("Creating file index...")
            try:
                # Use create_file_index which handles caching
                index, chunks = create_file_index(
                    embed=embed,
                    ignore_paths=config['GLOBAL_IGNORES'],
                    embed_chunk_size=embed.get_chunk_size(),
                    extra_dirs=[]
                )
                
                logger.info("Initializing assistant...")
                # Initialize the assistant
                try:
                    assistant = LlamaCppAssistant(
                        model_path=llm_model_file,
                        llama_cpp_options=config['LLAMA_CPP_OPTIONS'],
                        system_instructions=config['SYSTEM_INSTRUCTIONS'],
                        embed=embed,
                        index=index,
                        chunks=chunks,
                        context_file_ratio=config['CONTEXT_FILE_RATIO'],
                        output_acceptance_retries=config['OUTPUT_ACCEPTANCE_RETRIES'],
                        use_cgrag=config['USE_CGRAG'],
                        print_cgrag=config['PRINT_CGRAG'],
                        commit_to_git=config['COMMIT_TO_GIT'],
                        completion_options=config['LLAMA_CPP_COMPLETION_OPTIONS']
                    )
                    assistant.initialize_history()  # Initialize chat history
                except Exception as e:
                    logger.error(f"Error initializing assistant: {str(e)}")
                    return json.dumps({'error': f'Failed to initialize assistant: {str(e)}'})
                
                # Store only serializable data in session
                session['current_directory'] = directory
                session['config'] = config
                session['index_info'] = {
                    'num_chunks': len(chunks),
                    'model_path': llm_model_file,
                    'embed_model_path': embed_model_file
                }
                
                # Store the assistant in a global variable
                global current_assistant
                current_assistant = assistant
                
                # Create a new conversation for the directory
                conversation_id = db.conversations.insert(
                    title='New Conversation',
                    directory_path=directory
                )
                session['current_conversation_id'] = conversation_id
                
                # Add system message if it exists
                if hasattr(current_assistant, 'system_instructions'):
                    db.messages.insert(
                        conversation_id=conversation_id,
                        role='system',
                        content=current_assistant.system_instructions
                    )
                
                # Get recent conversations for this directory
                conversations = db(
                    (db.conversations.directory_path == directory) &
                    (db.conversations.id.belongs(
                        db(db.messages.role == 'assistant')._select(db.messages.conversation_id)
                    ))
                ).select(
                    orderby=~db.conversations.updated_at,
                    limitby=(0, 10)
                ).as_list()
                
                # Convert datetime objects to ISO format strings
                for conv in conversations:
                    if 'created_at' in conv:
                        conv['created_at'] = conv['created_at'].isoformat()
                    if 'updated_at' in conv:
                        conv['updated_at'] = conv['updated_at'].isoformat()
                
                logger.info("Successfully initialized codebase and assistant")
                return json.dumps({
                    'success': True,
                    'current_conversation_id': conversation_id,
                    'conversations': conversations
                })
                
            except Exception as e:
                logger.error(f"Error during file indexing: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return json.dumps({'error': f'Failed to index files: {str(e)}. Please check if the directory contains valid text files.'})
            
        finally:
            # Always restore the original working directory
            os.chdir(original_cwd)
            
    except Exception as e:
        logger.error(f"Error initializing dir-assistant: {str(e)}")
        return json.dumps({'error': str(e)})

# Global variable to store the current assistant
current_assistant = None

@action('send_message', method=['POST'])
@action.uses(db, session)
def send_message():
    """
    Send a message to dir-assistant and get response
    """
    try:
        logger.info("Received message request")
        
        if not session.get('current_directory'):
            logger.error("No directory selected in session")
            return json.dumps({'error': 'No directory selected'})
        
        if current_assistant is None:
            logger.error("Assistant not initialized")
            return json.dumps({'error': 'Assistant not initialized. Please reload the directory.'})
        
        message = request.json.get('message')
        if not message:
            logger.error("Empty message received")
            return json.dumps({'error': 'No message provided'})
        
        # Process message with assistant first to ensure we get a response
        try:
            response_text = current_assistant.run_stream_processes(message, write_to_stdout=False)
            logger.info(f"Got response (first 100 chars): {response_text[:100]}...")
        except Exception as e:
            logger.error(f"Error in run_stream_processes: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
        # Only create/save conversation if we got a successful response
        conversation_id = session.get('current_conversation_id')
        if not conversation_id:
            conversation_id = db.conversations.insert(
                title=message[:50] + ('...' if len(message) > 50 else ''),
                directory_path=session['current_directory']
            )
            session['current_conversation_id'] = conversation_id
            
            # Add system message if it exists
            if hasattr(current_assistant, 'system_instructions'):
                db.messages.insert(
                    conversation_id=conversation_id,
                    role='system',
                    content=current_assistant.system_instructions
                )
        else:
            # If this is the first user message, update the conversation title
            user_messages = db((db.messages.conversation_id == conversation_id) & 
                            (db.messages.role == 'user')).count()
            if user_messages == 0:
                db.conversations[conversation_id].update_record(
                    title=message[:50] + ('...' if len(message) > 50 else '')
                )
        
        # Save user message to database
        db.messages.insert(
            conversation_id=conversation_id,
            role='user',
            content=message
        )
        
        # Save assistant response to database
        db.messages.insert(
            conversation_id=conversation_id,
            role='assistant',
            content=response_text
        )
        
        # Update conversation timestamp
        db.conversations[conversation_id].update_record()
        
        logger.info("Successfully completed message processing")
        return json.dumps({
            'message': response_text
        })
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return json.dumps({'error': str(e)})

@action('get_file_tree')
@action.uses(session)
def get_file_tree():
    """
    Get the directory structure for the codebase browser
    """
    try:
        if not session.get('current_directory'):
            return json.dumps({'error': 'No directory selected'})
        
        file_tree = build_file_tree(session.get('current_directory'))
        return json.dumps(file_tree)
    except Exception as e:
        logger.error(f"Error building file tree: {str(e)}")
        return json.dumps({'error': str(e)})

@action('view_file')
@action.uses(session)
def view_file():
    """
    Get contents of a specific file
    """
    try:
        filepath = request.params.get('path')
        if not filepath or not session.get('current_directory'):
            logger.error("Invalid request: missing filepath or current_directory")
            return json.dumps({'error': 'Invalid request'})
        
        # Clean and normalize the paths
        base_dir = os.path.realpath(session.get('current_directory'))
        requested_path = os.path.normpath(filepath)  # Normalize the requested path
        full_path = os.path.realpath(os.path.join(base_dir, requested_path))
        
        logger.info(f"Attempting to view file:")
        logger.info(f"  Base directory: {base_dir}")
        logger.info(f"  Requested path: {requested_path}")
        logger.info(f"  Full path: {full_path}")
        
        # Security check - make sure the file is within the base directory
        if not full_path.startswith(base_dir):
            logger.error(f"Security error: Attempted to access file outside base directory")
            logger.error(f"  Base dir: {base_dir}")
            logger.error(f"  Full path: {full_path}")
            return json.dumps({'error': 'Access denied'})
            
        if not os.path.exists(full_path):
            logger.error(f"Path does not exist: {full_path}")
            return json.dumps({'error': 'File not found'})
            
        if not os.path.isfile(full_path):
            logger.error(f"Path is not a file: {full_path}")
            return json.dumps({'error': 'Not a file'})
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Successfully read file: {full_path}")
            return json.dumps({'content': content})
        except UnicodeDecodeError:
            logger.warning(f"Binary file detected: {full_path}")
            return json.dumps({'error': 'Cannot display binary file'})
        except Exception as e:
            logger.error(f"Error reading file {full_path}: {str(e)}")
            return json.dumps({'error': f'Error reading file: {str(e)}'})
            
    except Exception as e:
        logger.error(f"Error in view_file: {str(e)}")
        return json.dumps({'error': str(e)})

def build_file_tree(directory):
    """
    Helper function to build a tree structure of the directory
    """
    tree = []
    try:
        # Get the absolute path of the directory
        abs_directory = os.path.realpath(directory)
        logger.info(f"Building file tree for directory: {abs_directory}")
        
        # Get ignore patterns from session config
        config = session.get('config', {})
        ignore_patterns = config.get('GLOBAL_IGNORES', [
            '.git', 'node_modules', '__pycache__', '*.pyc',
            'venv', 'env', '.env', '.venv',
            'dist', 'build', '*.egg-info',
            '.DS_Store', 'Thumbs.db'
        ])
        logger.info(f"Using ignore patterns for file tree: {ignore_patterns}")
        
        def _build_tree(current_dir):
            items = []
            try:
                for item in os.listdir(current_dir):
                    # Skip items matching ignore patterns
                    skip = False
                    for pattern in ignore_patterns:
                        if pattern.startswith('*'):
                            if item.endswith(pattern[1:]):
                                skip = True
                                break
                        elif pattern in os.path.join(current_dir, item):
                            skip = True
                            break
                    if skip:
                        continue
                        
                    abs_path = os.path.join(current_dir, item)
                    # Get path relative to the root directory
                    rel_path = os.path.relpath(abs_path, abs_directory)
                    
                    if os.path.isfile(abs_path):
                        items.append({
                            'name': item,
                            'type': 'file',
                            'path': rel_path
                        })
                        logger.debug(f"Added file to tree: {rel_path}")
                    elif os.path.isdir(abs_path):
                        children = _build_tree(abs_path)
                        if children:  # Only add directory if it has viewable contents
                            items.append({
                                'name': item,
                                'type': 'directory',
                                'path': rel_path,
                                'children': children
                            })
                            logger.debug(f"Added directory to tree: {rel_path}")
                return items
            except Exception as e:
                logger.error(f"Error building tree for {current_dir}: {str(e)}")
                return []
        
        tree = _build_tree(abs_directory)
        return tree
    except Exception as e:
        logger.error(f"Error building file tree: {str(e)}")
        return []

@action('validate_directory', method=['POST'])
@action.uses(session)
def validate_directory():
    """
    Validate a directory path and return its absolute path
    """
    try:
        directory = request.json.get('directory', '')
        
        # If no directory provided or it's '.', use the session's current_directory
        if not directory or directory == '.':
            directory = session.get('current_directory')
            if not directory:
                return json.dumps({'error': 'No directory provided'})
        
        logger.info(f"Validating directory: {directory}")
        
        # Clean up the path - remove any extra slashes and resolve symlinks
        try:
            clean_path = os.path.realpath(os.path.normpath(directory))
            
            if os.path.exists(clean_path) and os.path.isdir(clean_path):
                logger.info(f"Found valid directory at: {clean_path}")
                return json.dumps({'path': clean_path})
            else:
                logger.error(f"Directory not found: {clean_path}")
                return json.dumps({'error': 'Could not find the directory'})
        
        except Exception as e:
            logger.error(f"Error validating path: {str(e)}")
            return json.dumps({'error': f'Error validating directory path: {str(e)}'})
            
    except Exception as e:
        logger.error(f"Error validating directory: {str(e)}")
        return json.dumps({'error': f'Error validating directory: {str(e)}'})

@action('get_chat_history')
@action.uses(session)
def get_chat_history():
    """
    Get the chat history from the current assistant
    """
    try:
        if not session.get('current_directory'):
            return json.dumps({'error': 'No directory selected'})
        
        if current_assistant is None:
            return json.dumps({'error': 'Assistant not initialized'})
        
        # Get chat history excluding system message
        history = current_assistant.chat_history[1:] if current_assistant.chat_history else []
        
        return json.dumps({
            'history': [
                {
                    'role': msg['role'],
                    'content': msg['content']
                }
                for msg in history
            ]
        })
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        return json.dumps({'error': str(e)})

def initialize_assistant(directory, config=None):
    """
    Initialize dir-assistant with the given directory and config
    Returns (success, error_message)
    """
    try:
        # Convert to absolute path and clean it
        directory = os.path.realpath(os.path.normpath(directory))
        logger.info(f"Initializing assistant for directory: {directory}")
        
        # Store the original working directory
        original_cwd = os.getcwd()
        
        try:
            # Change to the selected directory
            os.chdir(directory)
            
            # Try to load dir-assistant configuration, use defaults if not found
            if config is None:
                try:
                    config_dict = load_config()
                    config = config_dict.get('CODESEARCH_AI', {})
                except Exception as e:
                    logger.warning(f"Could not load config, using defaults: {str(e)}")
                    config = {}
            
            # Use CONFIG_DEFAULTS for default configuration
            default_config = CONFIG_DEFAULTS.copy()
            
            # Merge default config with loaded config
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
                elif isinstance(value, dict) and isinstance(config[key], dict):
                    for k, v in value.items():
                        if k not in config[key]:
                            config[key][k] = v
            
            # Get model paths
            models_path = os.path.expanduser(config['MODELS_PATH'])
            llm_model_file = get_file_path(models_path, config['LLM_MODEL'])
            embed_model_file = get_file_path(models_path, config['EMBED_MODEL'])
            
            if not os.path.exists(llm_model_file):
                return False, 'LLM model not found. Please run "codesearch-ai models download-llm" first.'
            
            if not os.path.exists(embed_model_file):
                return False, 'Embedding model not found. Please run "codesearch-ai models download-embed" first.'
            
            logger.info("Initializing embedding model...")
            embed = LlamaCppEmbed(
                model_path=embed_model_file,
                embed_options=config['LLAMA_CPP_EMBED_OPTIONS']
            )
            
            logger.info("Creating file index...")
            try:
                # Use create_file_index which handles caching
                index, chunks = create_file_index(
                    embed=embed,
                    ignore_paths=config['GLOBAL_IGNORES'],
                    embed_chunk_size=embed.get_chunk_size(),
                    extra_dirs=[]
                )
                
                logger.info("Initializing assistant...")
                global current_assistant
                current_assistant = LlamaCppAssistant(
                    model_path=llm_model_file,
                    llama_cpp_options=config['LLAMA_CPP_OPTIONS'],
                    system_instructions=config['SYSTEM_INSTRUCTIONS'],
                    embed=embed,
                    index=index,
                    chunks=chunks,
                    context_file_ratio=config['CONTEXT_FILE_RATIO'],
                    output_acceptance_retries=config['OUTPUT_ACCEPTANCE_RETRIES'],
                    use_cgrag=config['USE_CGRAG'],
                    print_cgrag=config['PRINT_CGRAG'],
                    commit_to_git=config['COMMIT_TO_GIT'],
                    completion_options=config['LLAMA_CPP_COMPLETION_OPTIONS']
                )
                current_assistant.initialize_history()
                
                return True, None
                
            except Exception as e:
                logger.error(f"Error creating index: {str(e)}")
                return False, str(e)
            
        finally:
            # Restore the original working directory
            os.chdir(original_cwd)
            
    except Exception as e:
        logger.error(f"Error initializing dir-assistant: {str(e)}")
        return False, str(e)

@action('get_model_info')
@action.uses(session)
def get_model_info():
    """Get information about currently loaded models and available models for download"""
    try:
        config_dict = load_config()
        config = config_dict.get('CODESEARCH_AI', {})
        models_path = os.path.expanduser(config.get('MODELS_PATH', '~/.local/share/codesearch_ai/models'))
        
        # Get list of actually installed model files
        installed_model_files = []
        if os.path.exists(models_path):
            installed_model_files = [f for f in os.listdir(models_path) if f.endswith('.gguf')]
        
        # Get current model information
        current_models = {
            'llm': {
                'name': config.get('LLM_MODEL', ''),
                'is_local': config.get('ACTIVE_MODEL_IS_LOCAL', False),
                'path': get_file_path(models_path, config.get('LLM_MODEL', '')),
                'exists': False  # Will be updated below
            },
            'embedding': {
                'name': config.get('EMBED_MODEL', ''),
                'is_local': config.get('ACTIVE_EMBED_IS_LOCAL', False),
                'path': get_file_path(models_path, config.get('EMBED_MODEL', '')),
                'exists': False  # Will be updated below
            }
        }
        
        # Check existence of all available models and update their status
        for model_type in ['llm', 'embedding']:
            # First check if the configured model exists in installed files
            if current_models[model_type]['name'] in installed_model_files:
                current_models[model_type]['exists'] = True
            
            # Update available models list with installation status
            for model in AVAILABLE_MODELS[model_type]:
                # Check if this model file exists in installed files
                model['exists'] = model['filename'] in installed_model_files
                
                # If this is the current model and it exists, update current model info
                if model['filename'] == current_models[model_type]['name'] and model['exists']:
                    current_models[model_type].update({
                        'exists': True,
                        'is_local': True,
                        'path': os.path.join(models_path, model['filename'])
                    })
        
        return json.dumps({
            'current_models': current_models,
            'available_models': AVAILABLE_MODELS,
            'models_path': models_path
        })
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        return json.dumps({'error': str(e)})

@action('download_model', method=['POST'])
@action.uses(session)
def download_model():
    """Download a model"""
    try:
        model_type = request.json.get('model_type')  # 'llm' or 'embedding'
        model_id = request.json.get('model_id', 'default')  # 'default' or 'qwq'
        
        if not model_type or model_type not in ['llm', 'embedding']:
            return json.dumps({'error': 'Invalid model type'})
            
        # Find the selected model
        selected_model = None
        for model in AVAILABLE_MODELS[model_type]:
            if model['id'] == model_id:
                selected_model = model
                break
                
        if not selected_model:
            return json.dumps({'error': 'Invalid model ID'})
            
        config_dict = load_config()
        models_path = os.path.expanduser(config_dict.get('CODESEARCH_AI', {}).get('MODELS_PATH', '~/.local/share/codesearch_ai/models'))
        os.makedirs(models_path, exist_ok=True)
        
        # Download the model using wget
        model_url = f"https://huggingface.co/{selected_model['repo_id']}/resolve/main/{selected_model['filename']}?download=true"
        output_path = os.path.join(models_path, selected_model['filename'])
        
        # Download the model
        subprocess.run(['wget', '-O', output_path, model_url], check=True)
        
        # Update config if this is the default model
        if model_id == 'default':
            if model_type == 'llm':
                config_dict['CODESEARCH_AI']['ACTIVE_MODEL_IS_LOCAL'] = True
                config_dict['CODESEARCH_AI']['LLM_MODEL'] = selected_model['filename']
            else:
                config_dict['CODESEARCH_AI']['ACTIVE_EMBED_IS_LOCAL'] = True
                config_dict['CODESEARCH_AI']['EMBED_MODEL'] = selected_model['filename']
            from codesearch_ai.cli.config import save_config
            save_config(config_dict)
        
        return json.dumps({'success': True})
    except Exception as e:
        logger.error(f"Error downloading model: {str(e)}")
        return json.dumps({'error': str(e)})

@action('switch_model', method=['POST'])
@action.uses(session)
def switch_model():
    """Switch to a different model"""
    global current_assistant
    
    try:
        model_type = request.json.get('model_type')  # 'llm' or 'embedding'
        model_id = request.json.get('model_id')
        
        logger.info(f"Switching {model_type} model to {model_id}")
        
        if not model_type or model_type not in ['llm', 'embedding']:
            return json.dumps({'error': 'Invalid model type'})
        
        # Find the selected model
        selected_model = None
        for model in AVAILABLE_MODELS[model_type]:
            if model['id'] == model_id:
                selected_model = model
                break
                
        if not selected_model:
            return json.dumps({'error': 'Invalid model ID'})
        
        # Load current config
        try:
            config_dict = load_config()
            logger.info(f"Current config: {config_dict}")
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return json.dumps({'error': f'Failed to load config: {str(e)}'})
        
        # Initialize CODESEARCH_AI section if it doesn't exist
        if 'CODESEARCH_AI' not in config_dict:
            config_dict['CODESEARCH_AI'] = CONFIG_DEFAULTS.copy()
        
        # Get models path
        models_path = os.path.expanduser(config_dict['CODESEARCH_AI'].get('MODELS_PATH', '~/.local/share/codesearch_ai/models'))
        model_path = os.path.join(models_path, selected_model['filename'])
        
        if not os.path.exists(model_path):
            return json.dumps({'error': 'Model not found. Please download it first.'})
        
        # Update config with new model
        if model_type == 'llm':
            logger.info(f"Updating LLM model to: {selected_model['filename']}")
            config_dict['CODESEARCH_AI']['ACTIVE_MODEL_IS_LOCAL'] = True
            config_dict['CODESEARCH_AI']['LLM_MODEL'] = selected_model['filename']
        else:
            logger.info(f"Updating embedding model to: {selected_model['filename']}")
            config_dict['CODESEARCH_AI']['ACTIVE_EMBED_IS_LOCAL'] = True
            config_dict['CODESEARCH_AI']['EMBED_MODEL'] = selected_model['filename']
        
        # Save the updated config
        try:
            from codesearch_ai.cli.config import save_config
            save_config(config_dict)
            logger.info("Successfully saved updated config")
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")
            return json.dumps({'error': f'Failed to save config: {str(e)}'})
        
        # Update session config
        if 'config' not in session:
            session['config'] = config_dict['CODESEARCH_AI']
        else:
            if model_type == 'llm':
                session['config']['LLM_MODEL'] = selected_model['filename']
                session['config']['ACTIVE_MODEL_IS_LOCAL'] = True
            else:
                session['config']['EMBED_MODEL'] = selected_model['filename']
                session['config']['ACTIVE_EMBED_IS_LOCAL'] = True
        
        # Only reinitialize if we have a current directory and assistant
        if session.get('current_directory') and current_assistant:
            logger.info("Reinitializing components with new model")
            try:
                if model_type == 'llm':
                    # Store current state
                    old_embed = current_assistant.embed
                    old_index = current_assistant.index
                    old_chunks = current_assistant.chunks
                    old_chat_history = getattr(current_assistant, 'chat_history', None)
                    
                    # Create a new LlamaCppAssistant with the same parameters but new LLM model
                    current_assistant = LlamaCppAssistant(
                        model_path=model_path,
                        llama_cpp_options=config_dict['CODESEARCH_AI']['LLAMA_CPP_OPTIONS'],
                        system_instructions=config_dict['CODESEARCH_AI']['SYSTEM_INSTRUCTIONS'],
                        embed=old_embed,  # Reuse existing embedding model
                        index=old_index,  # Reuse existing index
                        chunks=old_chunks,  # Reuse existing chunks
                        context_file_ratio=config_dict['CODESEARCH_AI']['CONTEXT_FILE_RATIO'],
                        output_acceptance_retries=config_dict['CODESEARCH_AI']['OUTPUT_ACCEPTANCE_RETRIES'],
                        use_cgrag=config_dict['CODESEARCH_AI']['USE_CGRAG'],
                        print_cgrag=config_dict['CODESEARCH_AI']['PRINT_CGRAG'],
                        commit_to_git=config_dict['CODESEARCH_AI']['COMMIT_TO_GIT'],
                        completion_options=config_dict['CODESEARCH_AI']['LLAMA_CPP_COMPLETION_OPTIONS']
                    )
                    
                    # Initialize history before restoring old history
                    current_assistant.initialize_history()
                    
                    # Restore chat history if it existed
                    if old_chat_history is not None:
                        current_assistant.chat_history = old_chat_history
                else:
                    # For embedding model switch, we need to recreate the embeddings
                    embed = LlamaCppEmbed(
                        model_path=model_path,
                        embed_options=config_dict['CODESEARCH_AI']['LLAMA_CPP_EMBED_OPTIONS']
                    )
                    current_assistant.embed = embed
                    
                    # Create new index with existing files
                    logger.info("Creating new embeddings with updated model...")
                    index, chunks = create_file_index(
                        embed=embed,
                        ignore_paths=config_dict['CODESEARCH_AI']['GLOBAL_IGNORES'],
                        embed_chunk_size=embed.get_chunk_size(),
                        extra_dirs=[]
                    )
                    current_assistant.index = index
                    current_assistant.chunks = chunks
                    
                    # Update session index info
                    session['index_info'] = {
                        'num_chunks': len(chunks),
                        'model_path': get_file_path(models_path, config_dict['CODESEARCH_AI']['LLM_MODEL']),
                        'embed_model_path': model_path
                    }
                
                logger.info("Successfully reinitialized components")
            except Exception as e:
                logger.error(f"Error reinitializing components: {str(e)}")
                return json.dumps({'error': f'Failed to initialize new model: {str(e)}'})
        
        return json.dumps({'success': True})
    except Exception as e:
        logger.error(f"Error switching model: {str(e)}")
        return json.dumps({'error': str(e)})

# Add new global variable to store indexing progress
indexing_progress = {
    'current_file': None,
    'processed_files': set(),
    'pending_files': set(),
    'clients': set()
}

@action('indexing_progress')
@action.uses(session)
def get_indexing_progress():
    """SSE endpoint for real-time indexing progress updates"""
    def generate():
        client_id = time.time()  # Use timestamp as client ID
        indexing_progress['clients'].add(client_id)
        try:
            while True:
                if client_id in indexing_progress['clients']:
                    current = indexing_progress['current_file']
                    processed = list(indexing_progress['processed_files'])
                    pending = list(indexing_progress['pending_files'])
                    
                    data = {
                        'current': current,
                        'processed': processed,
                        'pending': pending
                    }
                    
                    yield f"data: {json.dumps(data)}\n\n"
                    time.sleep(0.5)  # Send updates every 500ms
                else:
                    break
        finally:
            if client_id in indexing_progress['clients']:
                indexing_progress['clients'].remove(client_id)
    
    response.headers['Content-Type'] = 'text/event-stream'
    response.headers['Cache-Control'] = 'no-cache'
    return generate()

def update_indexing_progress(filepath, status):
    """Update indexing progress and notify all connected clients"""
    if status == 'current':
        indexing_progress['current_file'] = filepath
    elif status == 'processed':
        if filepath in indexing_progress['pending_files']:
            indexing_progress['pending_files'].remove(filepath)
        indexing_progress['processed_files'].add(filepath)
    elif status == 'pending':
        indexing_progress['pending_files'].add(filepath)

def _matches_ignore_pattern(file_path, pattern):
    """Helper function to check if a file path matches an ignore pattern"""
    if pattern.endswith('/'):
        # Directory pattern - check if file_path contains this directory
        dir_pattern = pattern.rstrip('/')
        return dir_pattern in file_path.split(os.sep)
    elif pattern.startswith('*'):
        # Extension/wildcard pattern
        return file_path.endswith(pattern[1:])
    else:
        # Exact match or substring
        return pattern in file_path

@action('reindex_codebase', method=['POST'])
@action.uses(session)
def reindex_codebase():
    """
    Clear the index cache and regenerate embeddings for the current directory
    """
    try:
        # Reset indexing progress
        indexing_progress['current_file'] = None
        indexing_progress['processed_files'].clear()
        indexing_progress['pending_files'].clear()
        
        # Get directory from request or session
        directory = request.json.get('directory')
        if not directory:
            directory = session.get('current_directory')
            
        if not directory or not os.path.isdir(directory):
            return json.dumps({'error': 'Invalid directory'})
            
        # Convert to absolute path and clean it
        directory = os.path.realpath(os.path.normpath(directory))
        logger.info(f"Reindexing codebase in directory: {directory}")
        
        # Get ignore patterns from request or session config
        ignore_patterns = request.json.get('ignore_patterns')
        if ignore_patterns is None:
            # If not provided in request, use patterns from session config
            config = session.get('config', {})
            ignore_patterns = config.get('GLOBAL_IGNORES', CONFIG_DEFAULTS['GLOBAL_IGNORES'])
        
        # Clean up ignore patterns - ensure they're in the correct format
        ignore_patterns = [p.strip() for p in ignore_patterns if p.strip()]
        
        # Format ignore patterns consistently for both cache clearing and indexing
        formatted_ignore_patterns = []
        for pattern in ignore_patterns:
            if pattern.endswith('/'):
                formatted_ignore_patterns.append(pattern[:-1])
            else:
                formatted_ignore_patterns.append(pattern)
        
        logger.info(f"Using ignore patterns: {formatted_ignore_patterns}")
        
        # Get current config from session or load defaults
        config = session.get('config', CONFIG_DEFAULTS.copy())
        
        # Update ignore patterns in config with formatted patterns
        config['GLOBAL_IGNORES'] = formatted_ignore_patterns
        
        # Update and save the config file
        config_dict = {'CODESEARCH_AI': config}
        from codesearch_ai.cli.config import save_config
        save_config(config_dict)
        
        # Create args object with the correct directory
        args = Args(directory)
        
        # Store the original working directory and change to target directory
        original_cwd = os.getcwd()
        logger.info(f"Original working directory: {original_cwd}")
        
        try:
            # Change to the target directory
            os.chdir(directory)
            logger.info(f"Changed to directory: {directory}")
            
            # Clear the index cache with formatted patterns
            from codesearch_ai.assistant.index import clear
            clear(args, config_dict)
            
            # Initialize embedding model
            embed = LlamaCppEmbed(
                model_path=get_file_path(config['MODELS_PATH'], config['EMBED_MODEL']),
                embed_options=config['LLAMA_CPP_EMBED_OPTIONS']
            )
            
            # First collect all files to be indexed using relative paths
            files_to_index = []
            for root, _, files in os.walk('.'):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, '.')
                    logger.info(f"Checking file: {rel_path}")
                    
                    # Skip files matching ignore patterns
                    skip = False
                    for pattern in formatted_ignore_patterns:
                        if _matches_ignore_pattern(rel_path, pattern):
                            logger.info(f"Ignoring file {rel_path} due to pattern {pattern}")
                            skip = True
                            break
                    
                    if skip:
                        continue
                    
                    try:
                        # Try to read the file to check if it's text
                        with open(file_path, 'r', encoding='utf-8') as f:
                            f.read(1024)  # Just try to read first 1KB
                        files_to_index.append(rel_path)
                        update_indexing_progress(rel_path, 'pending')
                        logger.info(f"Added file to index: {rel_path}")
                    except (UnicodeDecodeError, IOError) as e:
                        logger.info(f"Skipping non-text file: {rel_path}")
                        continue
            
            if not files_to_index:
                raise ValueError("No text files found to index")
            
            logger.info(f"Found {len(files_to_index)} files to index")
            
            # Process each file
            chunks = []
            embeddings = []
            
            for filepath in files_to_index:
                try:
                    update_indexing_progress(filepath, 'current')
                    logger.info(f"Processing file: {filepath}")
                    with open(filepath, 'r', encoding='utf-8') as f:
                        contents = f.read()
                    file_chunks, file_embeddings = process_file(
                        embed, filepath, contents, embed.get_chunk_size()
                    )
                    chunks.extend(file_chunks)
                    embeddings.extend(file_embeddings)
                    update_indexing_progress(filepath, 'processed')
                    logger.info(f"Successfully processed file: {filepath}")
                except Exception as e:
                    logger.error(f"Error processing file {filepath}: {str(e)}")
                    continue
            
            if not chunks or not embeddings:
                raise ValueError("No files were successfully processed")
            
            # Create the index from all embeddings
            embeddings_array = np.array(embeddings)
            index = IndexFlatL2(embeddings_array.shape[1])
            index.add(embeddings_array)
            
            # Initialize new assistant with the updated index
            global current_assistant
            current_assistant = LlamaCppAssistant(
                model_path=get_file_path(config['MODELS_PATH'], config['LLM_MODEL']),
                llama_cpp_options=config['LLAMA_CPP_OPTIONS'],
                system_instructions=config['SYSTEM_INSTRUCTIONS'],
                embed=embed,
                index=index,
                chunks=chunks,
                context_file_ratio=config['CONTEXT_FILE_RATIO'],
                output_acceptance_retries=config['OUTPUT_ACCEPTANCE_RETRIES'],
                use_cgrag=config['USE_CGRAG'],
                print_cgrag=config['PRINT_CGRAG'],
                commit_to_git=config['COMMIT_TO_GIT'],
                completion_options=config['LLAMA_CPP_COMPLETION_OPTIONS']
            )
            
            # Store updated info in session
            session['index_info'] = {
                'num_chunks': len(chunks),
                'model_path': get_file_path(config['MODELS_PATH'], config['LLM_MODEL']),
                'embed_model_path': get_file_path(config['MODELS_PATH'], config['EMBED_MODEL'])
            }
            
        except Exception as e:
            logger.error(f"Error creating index: {str(e)}")
            raise
        
        # Save updated config to session
        session['config'] = config
        
        return json.dumps({'success': True})
            
    except Exception as e:
        logger.error(f"Error in reindex_codebase: {str(e)}")
        return json.dumps({'error': str(e)})

@action('get_conversations')
@action.uses(db, session)
def get_conversations():
    """Get all conversations for the current directory, limited to 10 most recent"""
    try:
        if not session.get('current_directory'):
            return json.dumps({'error': 'No directory selected'})
        
        # Get conversations that have at least one assistant message
        conversations = db(
            (db.conversations.directory_path == session['current_directory']) &
            (db.conversations.id.belongs(
                db(db.messages.role == 'assistant')._select(db.messages.conversation_id)
            ))
        ).select(
            orderby=~db.conversations.updated_at,
            limitby=(0, 10)  # Limit to 10 most recent conversations
        )
        
        return json.dumps({
            'conversations': [{
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat()
            } for conv in conversations]
        })
    except Exception as e:
        logger.error(f"Error getting conversations: {str(e)}")
        return json.dumps({'error': str(e)})

@action('create_conversation', method=['POST'])
@action.uses(db, session)
def create_conversation():
    """Create a new conversation"""
    try:
        if not session.get('current_directory'):
            return json.dumps({'error': 'No directory selected'})
        
        # Create with a temporary title
        conversation_id = db.conversations.insert(
            title='New Conversation',
            directory_path=session['current_directory']
        )
        
        # Add system message if it exists
        if current_assistant and hasattr(current_assistant, 'system_instructions'):
            db.messages.insert(
                conversation_id=conversation_id,
                role='system',
                content=current_assistant.system_instructions
            )
        
        # Set as current conversation
        session['current_conversation_id'] = conversation_id
        
        return json.dumps({
            'id': conversation_id,
            'title': 'New Conversation'
        })
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        return json.dumps({'error': str(e)})

@action('load_conversation', method=['POST'])
@action.uses(db, session)
def load_conversation():
    """Load a conversation"""
    try:
        conversation_id = request.json.get('conversation_id')
        if not conversation_id:
            return json.dumps({'error': 'No conversation ID provided'})
        
        conversation = db.conversations[conversation_id]
        if not conversation:
            return json.dumps({'error': 'Conversation not found'})
        
        # Get all messages for this conversation
        messages = db(db.messages.conversation_id == conversation_id).select(
            orderby=db.messages.created_at
        )
        
        # Update current conversation in session
        session['current_conversation_id'] = conversation_id
        
        # Update assistant's chat history
        if current_assistant:
            current_assistant.chat_history = [{
                'role': msg.role,
                'content': msg.content
            } for msg in messages]
        
        return json.dumps({
            'conversation': {
                'id': conversation.id,
                'title': conversation.title,
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat()
            },
            'messages': [{
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.created_at.isoformat()
            } for msg in messages]
        })
    except Exception as e:
        logger.error(f"Error loading conversation: {str(e)}")
        return json.dumps({'error': str(e)})

@action('update_conversation', method=['POST'])
@action.uses(db, session)
def update_conversation():
    """Update a conversation's title"""
    try:
        conversation_id = request.json.get('conversation_id')
        title = request.json.get('title')
        
        if not conversation_id or not title:
            return json.dumps({'error': 'Missing required fields'})
        
        conversation = db.conversations[conversation_id]
        if not conversation:
            return json.dumps({'error': 'Conversation not found'})
        
        conversation.update_record(title=title)
        
        return json.dumps({
            'success': True,
            'id': conversation_id,
            'title': title
        })
    except Exception as e:
        logger.error(f"Error updating conversation: {str(e)}")
        return json.dumps({'error': str(e)})

@action('delete_conversation', method=['POST'])
@action.uses(db, session)
def delete_conversation():
    """Delete a conversation and all its messages"""
    try:
        conversation_id = request.json.get('conversation_id')
        if not conversation_id:
            return json.dumps({'error': 'No conversation ID provided'})
        
        # Delete all messages first
        db(db.messages.conversation_id == conversation_id).delete()
        
        # Then delete the conversation
        db(db.conversations.id == conversation_id).delete()
        
        # If this was the current conversation, clear it from session
        if session.get('current_conversation_id') == conversation_id:
            del session['current_conversation_id']
        
        return json.dumps({'success': True})
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        return json.dumps({'error': str(e)})

@action('export_conversation', method=['POST'])
@action.uses(db, session)
def export_conversation():
    """Export a conversation as JSON"""
    try:
        conversation_id = request.json.get('conversation_id')
        if not conversation_id:
            return json.dumps({'error': 'No conversation ID provided'})
        
        conversation = db.conversations[conversation_id]
        if not conversation:
            return json.dumps({'error': 'Conversation not found'})
        
        messages = db(db.messages.conversation_id == conversation_id).select(
            orderby=db.messages.created_at
        )
        
        export_data = {
            'conversation': {
                'title': conversation.title,
                'directory_path': conversation.directory_path,
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat()
            },
            'messages': [{
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.created_at.isoformat()
            } for msg in messages]
        }
        
        return json.dumps(export_data)
    except Exception as e:
        logger.error(f"Error exporting conversation: {str(e)}")
        return json.dumps({'error': str(e)})

@action('import_conversation', method=['POST'])
@action.uses(db, session)
def import_conversation():
    """Import a conversation from JSON"""
    try:
        import_data = request.json.get('conversation_data')
        if not import_data:
            return json.dumps({'error': 'No conversation data provided'})
        
        # Find first user message to use as title
        title = 'Imported Conversation'
        for msg in import_data['messages']:
            if msg['role'] == 'user':
                title = msg['content'][:50] + ('...' if len(msg['content']) > 50 else '')
                break
        
        # Create the conversation
        conversation_id = db.conversations.insert(
            title=title,
            directory_path=import_data['conversation']['directory_path'],
            created_at=datetime.datetime.fromisoformat(import_data['conversation']['created_at']),
            updated_at=datetime.datetime.fromisoformat(import_data['conversation']['updated_at'])
        )
        
        # Import all messages
        for msg in import_data['messages']:
            db.messages.insert(
                conversation_id=conversation_id,
                role=msg['role'],
                content=msg['content'],
                created_at=datetime.datetime.fromisoformat(msg['created_at'])
            )
        
        return json.dumps({
            'success': True,
            'conversation_id': conversation_id
        })
    except Exception as e:
        logger.error(f"Error importing conversation: {str(e)}")
        return json.dumps({'error': str(e)})