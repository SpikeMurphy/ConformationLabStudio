# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ConformationLabStudio.py'],
    pathex=[],
    binaries=[],
    datas=[
	('ABOUT.md', '.'),
	('DISCLAIMER.md', '.'),
	('conflab_env.tar.gz', '.'),
	('ConformationLabLogo.png', '.'),
	('LICENSE_ConformationLabStudio.md', '.'),
	('LICENSE_ColabFold.md', '.'),
	('LICENSE_AlphaFold2.md', '.'),
	('THIRD_PARTY_LICENSES.md', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz_a = PYZ(a.pure)

exe = EXE(
    pyz_a,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ConformationLabStudio',
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
    icon=['ConformationLabIcon.icns'],
    onefile=True,
)

b = Analysis(
    ['run_molstar_v1.0.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz_b = PYZ(b.pure)

exe2 = EXE(
    pyz_b,
    b.scripts,
    b.binaries,
    b.datas,
    [],
    name='run_molstar_v1.0',
    console=False,
    onefile=False,
)

app = BUNDLE(
    exe,
    exe2,
    name='ConformationLabStudio.app',
    icon='ConformationLabIcon.icns',
    bundle_identifier='org.configurationlab.studio',
    info_plist={
        'CFBundleName': 'ConformationLabStudio',
        'CFBundleDisplayName': 'ConformationLabStudio',
        'CFBundleShortVersionString': '1.12.1',
        'CFBundleVersion': '20260306',
        'CFBundleExecutable': 'ConformationLabStudio',
        'CFBundleIconFile': 'ConformationLabIcon',
        'NSHumanReadableCopyright': '© 2025 Spike Murphy Müller · Code MIT License · Content & Design: All Rights Reserved · Powered by Colabfold & AlphaFold2',
        'CFBundleGetInfoString': 'ConformationLab Studio v1.12.1 – Developed by Spike Murphy Müller',
    },
)
