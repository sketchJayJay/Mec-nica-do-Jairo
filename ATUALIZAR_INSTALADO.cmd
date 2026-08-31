@echo off
set SRC="C:\Users\elian\Desktop\Não esquentais a cabeça\Jairo programa final\dist\Oficina"
set DEST="C:\Program Files\MecanicaDoJairo\Oficina"

if not exist %SRC% (
  echo [ERRO] Origem nao encontrada: %SRC%
  exit /b 1
)
if not exist %DEST% (
  echo [ERRO] Destino nao encontrado: %DEST%
  exit /b 1
)

echo Encerrando app...
taskkill /IM "Oficina.exe" /F >nul 2>nul

echo Copiando arquivos (preservando .db/.sqlite e logs do cliente)...
robocopy %SRC% %DEST% /E /R:1 /W:1 /XO /MT:8 /XD "__pycache__" /XF *.db *.sqlite last_error.log

set RC=%ERRORLEVEL%
if %RC% LSS 8 (
  echo [OK] Atualizacao concluida.
  start "" "%DEST%\Oficina.exe"
  exit /b 0
) else (
  echo [ERRO] Robocopy falhou. Codigo: %RC%
  exit /b %RC%
)
