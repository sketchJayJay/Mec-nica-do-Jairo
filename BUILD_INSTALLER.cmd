@echo off
setlocal enabledelayedexpansion
set ISS=Oficina_Installer_USERPATH.iss

rem Local padrão de instalação do Inno Setup 6
set ISCC="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
  echo [ERRO] Inno Setup 6 nao encontrado. Baixe em: https://jrsoftware.org/isdl.php
  exit /b 1
)

echo === Compilando instalador ===
%ISCC% "%ISS%"
if errorlevel 1 (
  echo [FALHA] Verifique as mensagens do compilador.
  exit /b 1
) else (
  echo [OK] Instalador gerado com sucesso.
  for %%F in (Oficina-Setup-v*.exe) do set OUT=%%~fF
  if defined OUT echo Arquivo: !OUT!
)