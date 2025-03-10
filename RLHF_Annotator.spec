# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['rlhf_annotator.py'],
    pathex=[],
    binaries=[],
    datas=[('checkpoints', 'checkpoints'), ('conversation_logs', 'conversation_logs'), ('rlhf_exports', 'rlhf_exports')],
    hiddenimports=[],
    hookspath=[],
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
    name='RLHF_Annotator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
