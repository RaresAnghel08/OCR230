# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Colectează toate modulele scipy
scipy_hiddenimports = collect_submodules('scipy')
easyocr_hiddenimports = collect_submodules('easyocr')
cv2_hiddenimports = collect_submodules('cv2')

# Colectează fișierele de date
scipy_datas = collect_data_files('scipy', include_py_files=True)
easyocr_datas = collect_data_files('easyocr', include_py_files=True)
cv2_datas = collect_data_files('cv2', include_py_files=True)

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=scipy_datas + easyocr_datas + cv2_datas + [
        ('Assets', 'Assets'),
        ('src/ui/assets', 'src/ui/assets'),
    ],
    hiddenimports=[
        'scipy._lib.messagestream',
        'scipy._cyutility',
        'scipy.special._ufuncs_cxx',
        'scipy.linalg.cython_blas',
        'scipy.linalg.cython_lapack',
        'scipy.linalg._cythonized_array_utils',
        'scipy.integrate._ode',
        'scipy.integrate._dop',
        'scipy.integrate.lsoda',
        'scipy.integrate.vode',
        'scipy.ndimage._nd_image',
        'scipy.ndimage._ni_support',
        'scipy.special._comb',
        'easyocr',
        'easyocr.easyocr',
        'easyocr.utils',
        'easyocr.recognition',
        'easyocr.detection',
        'cv2',
        'numpy',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'pdf2image',
        'threading',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
    ] + scipy_hiddenimports + easyocr_hiddenimports + cv2_hiddenimports,
    hookspath=['hooks'],
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
    name='F230-OCR',
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
    icon='Assets\\favicon.ico'  # Adaugă iconul dacă există
)
