@echo off
setlocal
cd /d "%~dp0"
title Configurar endereco - Mecanica do Jairo

echo ============================================================
echo        CONFIGURAR ENDERECO DA MECANICA DO JAIRO
echo ============================================================
echo.
echo Cole o endereco completo do sistema no Coolify.
echo Exemplo: https://oficina.seudominio.com.br
echo.
set /p "SITE=Endereco: "
if "%SITE%"=="" exit /b 1
>"%~dp0url_oficina.txt" echo %SITE%
echo.
echo Endereco salvo.
echo.
pause
