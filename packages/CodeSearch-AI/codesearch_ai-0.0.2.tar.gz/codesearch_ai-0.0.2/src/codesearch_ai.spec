# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files, collect_all

block_cipher = None

def collect_directory_data(source_dir, dest_dir):
    """Recursively collect all files from a directory."""
    data_files = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            source_path = os.path.join(root, file)
            # Get the relative path from source_dir
            rel_path = os.path.relpath(source_path, source_dir)
            # Create the destination path
            dest_path = os.path.join(dest_dir, os.path.dirname(rel_path))
            data_files.append((source_path, dest_path))
    return data_files

# Collect tiktoken data files
tiktoken_datas = collect_data_files('tiktoken', include_py_files=True)

# Collect litellm data files
litellm_binaries, litellm_datas, litellm_hiddenimports = collect_all('litellm')

# Collect llama_cpp data files
llama_cpp_binaries, llama_cpp_datas, llama_cpp_hiddenimports = collect_all('llama_cpp')

# Collect py4web data files and all its modules
py4web_binaries, py4web_datas, py4web_hiddenimports = collect_all('py4web')

# Add web service directory - using absolute path and recursive collection
web_dir = os.path.abspath('codesearch_ai_web')
if not os.path.exists(web_dir):
    raise FileNotFoundError(f"Web service directory not found at {web_dir}")
web_datas = collect_directory_data(web_dir, 'codesearch_ai_web')

# Combine all data files and binaries
all_datas = tiktoken_datas + litellm_datas + llama_cpp_datas + py4web_datas + web_datas
all_binaries = litellm_binaries + llama_cpp_binaries + py4web_binaries
all_hiddenimports = [
    'tiktoken_ext.openai_public',
    'tiktoken_ext',
    'py4web',
    'py4web.utils',
    'py4web.utils.form',
    'py4web.utils.factories',
    'py4web.utils.tags',
    'pydal',
    'pydal.restapi',
    'pydal.tools',
    'pydal.tools.scheduler',
    'pydal.tools.tags',
    'waitress',
] + litellm_hiddenimports + llama_cpp_hiddenimports + py4web_hiddenimports

# Add llama_cpp library explicitly
llama_lib_path = '.venv/lib/python3.11/site-packages/llama_cpp/lib/libllama.dylib'
all_binaries.append((llama_lib_path, 'llama_cpp/lib'))

a = Analysis(
    ['codesearch_ai/main.py'],
    pathex=[],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='codesearch_ai',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
