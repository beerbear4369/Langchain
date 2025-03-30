# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
from PyInstaller.building.build_main import Tree
import os
import site
import glob
import tiktoken
import sys

# Define paths directly without using __file__
root_dir = os.path.abspath(os.path.join(os.getcwd(), os.path.pardir if os.path.basename(os.getcwd()) == 'build_scripts' else '.'))
script_dir = os.path.join(root_dir, 'build_scripts')

# Find the tiktoken encoding files
tiktoken_cache_dir = os.path.join(os.path.dirname(tiktoken.__file__), "*.tiktoken")
tiktoken_files = glob.glob(tiktoken_cache_dir)
tiktoken_datas = [(file, os.path.join("tiktoken", os.path.basename(file))) for file in tiktoken_files]

# Find any cl100k_base files in the current directory or build_scripts (created by extract_cl100k.py)
local_cl100k_files = glob.glob(os.path.join(script_dir, "cl100k_base*.tiktoken"))
for file in local_cl100k_files:
    tiktoken_datas.append((file, '.'))
    tiktoken_datas.append((file, 'tiktoken'))
    tiktoken_datas.append((file, 'tiktoken_ext'))
    tiktoken_datas.append((file, os.path.join('tiktoken_ext', 'openai_public')))

# Find the cl100k_base.tiktoken file specifically in site-packages
site_packages = site.getsitepackages()[0]
cl100k_path = os.path.join(site_packages, "tiktoken_ext")
if os.path.exists(cl100k_path):
    cl100k_files = glob.glob(os.path.join(cl100k_path, "*.tiktoken"))
    for file in cl100k_files:
        tiktoken_datas.append((file, os.path.join("tiktoken_ext", os.path.basename(file))))

# Get more paths from sys.path
additional_paths = [path for path in sys.path if 'site-packages' in path or 'dist-packages' in path]

# Look in all possible paths for cl100k files
for path in additional_paths:
    ext_path = os.path.join(path, "tiktoken_ext")
    if os.path.exists(ext_path):
        pattern = os.path.join(ext_path, "*cl100k*")
        cl100k_files = glob.glob(pattern)
        for file in cl100k_files:
            tiktoken_datas.append((file, os.path.join("tiktoken_ext", os.path.basename(file))))
            
        # Also look in openai_public if it exists
        openai_path = os.path.join(ext_path, "openai_public")
        if os.path.exists(openai_path):
            pattern = os.path.join(openai_path, "*cl100k*")
            openai_files = glob.glob(pattern)
            for file in openai_files:
                tiktoken_datas.append((file, os.path.join("tiktoken_ext", "openai_public", os.path.basename(file))))

# Include our fix_imports.py helper module
fix_imports_path = os.path.join(script_dir, 'fix_imports.py')
if os.path.exists(fix_imports_path):
    datas = [(fix_imports_path, '.')]
else:
    print(f"Warning: Could not find fix_imports.py at {fix_imports_path}")
    datas = []

# Update paths for config.json and icon.ico to use paths relative to root
config_path = os.path.join(root_dir, 'config.json')
icon_path = os.path.join(root_dir, 'icon.ico')
datas.extend([(config_path, '.'), (icon_path, '.')])
datas.extend(tiktoken_datas)

# Create a hooks directory path relative to root
hooks_dir = os.path.join(root_dir, "hooks")
if os.path.exists(hooks_dir):
    print(f"Using hooks directory: {hooks_dir}")

binaries = []
hiddenimports = ['langchain', 'langchain.memory', 'langchain.chains.conversation.base', 'langchain_openai', 
                'langchain.prompts', 'langchain_core', 'openai', 'pyaudio', 'sounddevice', 'soundfile', 
                'wave', 'tempfile', 'dotenv', 'numpy', 'pydantic', 'pydantic.deprecated', 
                'pydantic.deprecated.decorator', 'pydantic_core', 'typing_extensions', 'json', 
                'tiktoken', 'tiktoken_ext', 'tiktoken_ext.openai_public', 'regex']

# Collect all necessary packages
tmp_ret = collect_all('pydantic')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pydantic_core')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('langchain')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('langchain_core')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('langchain_openai')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('openai')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('typing_extensions')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('tiktoken')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('tiktoken_ext')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Path to main.py should be relative to root directory
main_path = os.path.join(root_dir, 'main.py')

# Include conversation_logs directory if it exists (relative to root)
conversation_logs_dir = os.path.join(root_dir, 'conversation_logs')
if os.path.exists(conversation_logs_dir):
    datas += [(os.path.join(conversation_logs_dir, file), os.path.join('conversation_logs', file)) 
              for file in os.listdir(conversation_logs_dir) if os.path.isfile(os.path.join(conversation_logs_dir, file))]

# Ensure conversation_logs directory exists in the package even if empty
if not os.path.exists(conversation_logs_dir):
    os.makedirs(conversation_logs_dir, exist_ok=True)
    datas.append((conversation_logs_dir, 'conversation_logs'))

a = Analysis(
    [main_path],
    pathex=[root_dir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[hooks_dir] if os.path.exists(hooks_dir) else [],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AI coach B',
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
    icon=[icon_path],
) 