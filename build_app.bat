@echo off
echo Building F230-OCR with PyInstaller...

REM Curăță directoarele anterioare
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Instalează dependențele necesare pentru PyInstaller
pip install --upgrade pyinstaller
pip install --upgrade scipy
pip install --upgrade easyocr
pip install --upgrade opencv-python
pip install --upgrade pillow
pip install --upgrade pdf2image

echo.
echo Building executable...

REM Construiește cu fișierul spec
pyinstaller main.spec

REM Sau alternativ, folosește comanda directă cu mai multe opțiuni
REM pyinstaller --onefile --windowed --name "F230-OCR" ^
REM --hidden-import=scipy._lib.messagestream ^
REM --hidden-import=scipy._cyutility ^
REM --hidden-import=scipy.special._ufuncs_cxx ^
REM --hidden-import=scipy.linalg.cython_blas ^
REM --hidden-import=scipy.linalg.cython_lapack ^
REM --hidden-import=scipy.ndimage._nd_image ^
REM --hidden-import=easyocr ^
REM --hidden-import=easyocr.easyocr ^
REM --hidden-import=easyocr.utils ^
REM --hidden-import=easyocr.recognition ^
REM --hidden-import=easyocr.detection ^
REM --hidden-import=cv2 ^
REM --add-data "Assets;Assets" ^
REM --add-data "src/ui/assets;src/ui/assets" ^
REM --icon="Assets/favicon.ico" ^
REM main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build completed successfully!
    echo Executable can be found in: dist\F230-OCR.exe
) else (
    echo.
    echo Build failed with error code %ERRORLEVEL%
)

pause
