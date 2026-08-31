@echo off
setlocal

set ISS_FILE=installer.iss
set EXE_DIR=dist\OficinaMecanica
set EXE_FILE=dist\OficinaMecanica\OficinaMecanica.exe

if not exist %EXE_FILE% (
    echo [INFO] Executavel nao encontrado. Rodando build-pyinstaller.bat primeiro...
    call build-pyinstaller.bat
    if errorlevel 1 exit /b 1
)

REM Tenta encontrar o ISCC automaticamente (Inno Setup Compiler)
set ISCC=ISCC.exe
where %ISCC% >nul 2>nul
if errorlevel 1 (
    echo.
    echo [ERRO] Inno Setup (ISCC.exe) nao encontrado no PATH.
    echo Abra o arquivo %ISS_FILE% no Inno Setup e clique em "Compile".
    pause
    exit /b 1
)

%ISCC% %ISS_FILE%
if errorlevel 1 (
    echo [ERRO] Falha ao compilar o instalador.
    exit /b 1
)

echo.
echo === Instalador gerado em .\dist\OficinaMecanica-Setup-0.5.0.exe ===
pause
