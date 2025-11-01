# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['Curve.py'],
    pathex=[],
    binaries=[('classes\\Plot.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_constructors.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_discrim_curv.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_get_discriminator.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_loadOrCreateSettings.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_mlt_well_df.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_mtp_well_df.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_multipleWellCrossPlot.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_multipleWellHistograms.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_multipleWellThreeDPlot.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_multipleWellZPlots.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_multiWellCrossPlot.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_multiWellHistogram.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_multiWellThreeDPlot.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_multiWellZplot.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_newSettingsMenu.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_pickettPlot.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_pickettPlotOnClick.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_plotOnBaseKey.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_plotOnClick.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_plotOnKey.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_plotScales.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_singleWellCrossPlot.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_singleWellHistogram.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_singleWellThreeDPlot.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_singleWellZPlot.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\_staticMethodExample.cp310-win_amd64.pyd', 'lib'), ('classes\\Plot\\__init__.cp310-win_amd64.pyd', 'lib')],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5'],
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
    name='Curve',
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
