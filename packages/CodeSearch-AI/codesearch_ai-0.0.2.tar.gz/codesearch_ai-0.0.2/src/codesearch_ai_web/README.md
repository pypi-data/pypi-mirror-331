# CodeSearch AI Web Interface

A web-based interface for dir-assistant, allowing you to chat with your codebase using a local LLM.

## Prerequisites

1. Python 3.6 or higher
2. dir-assistant package
3. Local LLM and embedding models

## Setup

1. First, install dir-assistant and download the required models:
```bash
pip install dir-assistant
dir-assistant models download-embed
dir-assistant models download-llm
```

2. Install the web application dependencies:
```bash
cd codesearch_ai_web
pip install -r requirements.txt
```

3. Initialize py4web:
```bash
py4web setup apps
py4web set-password
```

## Running the Application

1. Start the web server:
```bash
cd codesearch_ai_web
py4web run apps
```

2. Open your browser and navigate to:
```
http://localhost:8000/codesearch
```

3. In the web interface:
   - Click "Select Directory" and enter the path to your codebase
   - Wait for the models to load and index your files
   - Start chatting!

## Features

- Modern web interface with three-panel layout:
  - File browser
  - Chat interface
  - File preview
- Real-time file indexing and search
- Local LLM-powered code understanding
- File content preview
- Support for large codebases

## Configuration

The application uses the same configuration as dir-assistant. You can modify the settings using:

```bash
dir-assistant config open
```

Key settings:
- `LLM_MODEL`: The local LLM model to use
- `EMBED_MODEL`: The local embedding model to use
- `CONTEXT_FILE_RATIO`: Ratio of context to use for file content
- `USE_CGRAG`: Whether to use CGRAG for better context selection

## Troubleshooting

1. If you see "Model not found" errors:
   - Make sure you've run the model download commands
   - Check that the models exist in `~/.local/share/dir-assistant/models/`

2. If the chat is slow:
   - Adjust the `LLAMA_CPP_OPTIONS` in the config
   - Consider using a smaller model
   - Try reducing the context size

3. For memory issues:
   - Reduce the `n_ctx` parameter in `LLAMA_CPP_OPTIONS`
   - Use quantized models (Q4_K_M or similar)

## Notes

- The application uses local models only, no API keys required
- All processing happens on your machine
- Chat history is maintained per session
- File indexing is done once per directory load 