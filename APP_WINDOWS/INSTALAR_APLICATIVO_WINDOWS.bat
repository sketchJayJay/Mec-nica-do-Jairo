@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Instalar Mecânica do Jairo

echo ============================================================
echo          MECANICA DO JAIRO - INSTALADOR WINDOWS
echo ============================================================
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    set "PY=py"
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set "PY=python"
    ) else (
        echo Python nao foi encontrado neste computador.
        pause
        exit /b 1
    )
)

echo Instalando componente da janela do aplicativo...
%PY% -m pip install --user pywebview
if errorlevel 1 (
    echo.
    echo Nao foi possivel instalar pywebview.
    pause
    exit /b 1
)

if not exist "%~dp0url_oficina.txt" call "%~dp0CONFIGURAR_ENDERECO.bat"
if not exist "%~dp0url_oficina.txt" exit /b 1

for /f "delims=" %%P in ('%PY% -c "import sys; print(sys.executable)"') do set "PYEXE=%%P"
for %%F in ("%PYEXE%") do set "PYDIR=%%~dpF"
set "PYW=%PYDIR%pythonw.exe"
if not exist "%PYW%" set "PYW=%PYEXE%"

set "DESKTOP=%USERPROFILE%\Desktop"
set "SCRIPT=%~dp0mecanica_jairo_app.py"
set "ICON=%~dp0Mecanica_do_Jairo.ico"
set "LINK=%DESKTOP%\Mecanica do Jairo.lnk"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$ws=New-Object -ComObject WScript.Shell;" ^
 "$s=$ws.CreateShortcut('%LINK%');" ^
 "$s.TargetPath='%PYW%';" ^
 "$s.Arguments='\"%SCRIPT%\"';" ^
 "$s.WorkingDirectory='%~dp0';" ^
 "$s.IconLocation='%ICON%,0';" ^
 "$s.WindowStyle=7;" ^
 "$s.Description='Mecânica do Jairo';" ^
 "$s.Save()"

echo.
echo PRONTO.
echo Foi criado no Desktop o atalho "Mecanica do Jairo".
echo Abra por ele. O X vermelho dentro do sistema fecha o programa inteiro.
echo.
pause
