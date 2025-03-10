# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
from PyInstaller.building.build_main import Tree
import os

block_cipher = None

# Define the data files to include
added_files = [
    ('config.json', '.'),                  # Include the config file
    ('icon.ico', '.'),                     # Include the icon file
]

# Collect all necessary packages
langchain_datas, langchain_binaries, langchain_hiddenimports = collect_all('langchain')
langchain_openai_datas, langchain_openai_binaries, langchain_openai_hiddenimports = collect_all('langchain_openai')
openai_datas, openai_binaries, openai_hiddenimports = collect_all('openai')
pydantic_datas, pydantic_binaries, pydantic_hiddenimports = collect_all('pydantic')

a = Analysis(
    ['main.py'],                           # Main entry point
    pathex=[],
    binaries=[],
    datas=added_files + langchain_datas + langchain_openai_datas + openai_datas + pydantic_datas,
    hiddenimports=[
        'langchain',
        'langchain.memory',
        'langchain.chains.conversation.base',
        'langchain_openai',
        'langchain.prompts',
        'langchain_core',
        'openai',
        'pyaudio',
        'sounddevice',
        'soundfile',
        'wave',
        'tempfile',
        'dotenv',
        'python-dotenv',
        'numpy',
        'pydantic',
        'pydantic_core',
        'typing_extensions',
    ] + langchain_hiddenimports + langchain_openai_hiddenimports + openai_hiddenimports + pydantic_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Include conversation_logs directory if it exists
if os.path.exists('conversation_logs'):
    a.datas += Tree('conversation_logs', prefix='conversation_logs')

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Coaching_Assistant',
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
    icon='icon.ico',
) 