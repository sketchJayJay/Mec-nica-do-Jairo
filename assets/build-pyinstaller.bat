@echo off
setlocal enabledelayedexpansion

REM ==== CONFIG ====
set APP_NAME=Oficina Mecânica
set EXE_NAME=OficinaMecanica
set VERSION=0.5.0
set MAIN_PY=OFICINA_HOME_CARDS_COLOR_v4_SAFE_BUSCA_DESC_PREMIUM_v3_PATCH2.py
set ICON_PATH=assets\logo.ico
set ASSETS_DIR=assets

REM Python expected on PATH. If using py -3, uncomment next line:
REM set PY=py -3
set PY=python

echo.
echo === 1/4: Criando venv (se nao existir) ===
if not exist .venv (
    %PY% -m venv .venv
)
call .venv\Scripts\activate

echo.
echo === 2/4: Instalando dependencias ===
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

echo.
echo === 3/4: Rodando PyInstaller ===
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM Inclui a pasta assets (se existir) no executavel
set ADD_DATA=
if exist "%ASSETS_DIR%" (
    set ADD_DATA=--add-data "%ASSETS_DIR%;assets"
)

REM Icone opcional
set ICON=
if exist "%ICON_PATH%" (
    set ICON=--icon "%ICON_PATH%"
)

pyinstaller ^
  --noconfirm ^
  --clean ^
  --name "%EXE_NAME%" ^
  --windowed ^
  %ICON% ^
  --hidden-import imageio_ffmpeg ^
  %ADD_DATA% ^
  "%MAIN_PY%"

if errorlevel 1 (
    echo [ERRO] PyInstaller falhou.
    exit /b 1
)

echo.
echo === 4/4: Pronto! Executavel em .\dist\%EXE_NAME%\%EXE_NAME%.exe ===
echo Opcional: rode 'build-installer.bat' para gerar um instalador .exe via Inno Setup.
pause
