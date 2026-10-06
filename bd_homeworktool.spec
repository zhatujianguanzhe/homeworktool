# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['homeworktool.py'],
    pathex=[],
    binaries=[],
    datas=[('.\\resource\\*','.\\resource'),('.\\laotaoui\\libresource\\*', 'laotaoui/libresource')],
    excludes=['pygame','PyQt5'],
    hiddenimports=['ctypes','laotaoui'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    #excludes=[],
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
    name='homeworktool',
    excludes=['pygame'],
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
    icon=['resource/icon.ico'],
    version='homeworktool_version.txt',  # ← 加上这一行
)
