# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_dynamic_libs
import os

# Set the PYTHONIOENCODING environment variable
os.environ['PYTHONIOENCODING'] = 'utf-8'

datas = [
    ('templates', 'templates')
]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
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
    name='Serendib Color Formular',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon="/Users/charangan/Documents/Work/Benjamin/arun/assets/logo.ico",
    disable_windowed_traceback=True,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    environ=os.environ,  # Add this line to include the environment
)