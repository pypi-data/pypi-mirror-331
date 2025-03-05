# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['apps/codesearch/__init__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('apps/codesearch/templates', 'apps/codesearch/templates'),
        ('apps/codesearch/static', 'apps/codesearch/static'),
    ],
    hiddenimports=[
        'py4web',
        'dir_assistant',
        'llama_cpp_python',
        'faiss_cpu',
        'colorama',
        'sqlitedict',
        'prompt_toolkit',
        'watchdog',
        'dynaconf',
        'toml',
    ],
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
    name='codesearch',
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