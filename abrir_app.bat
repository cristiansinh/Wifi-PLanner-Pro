@echo off
title WiFi Planner Pro v3.3

set "BASE=%~dp0"
if "%BASE:~-1%"=="\" set "BASE=%BASE:~0,-1%"

echo.
echo  WiFi Planner Pro v3.3
echo  ================================
echo.

:: Buscar Python
set "PCMD="
python --version >nul 2>&1 && set "PCMD=python"
if "%PCMD%"=="" (
    py --version >nul 2>&1 && set "PCMD=py"
)

if "%PCMD%"=="" (
    echo  [ERROR] Python no encontrado. Instala Python desde:
    echo  https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Verificar pywebview (unico requerido)
%PCMD% -c "import webview" >nul 2>&1
if errorlevel 1 (
    echo  Instalando pywebview...
    %PCMD% -m pip install pywebview
    if errorlevel 1 (
        echo  [ERROR] No se pudo instalar pywebview.
        pause
        exit /b 1
    )
)

:: Lanzar app
echo  Iniciando aplicacion...
echo.
%PCMD% "%BASE%\wifi_planner_v3.py"

if errorlevel 1 (
    echo.
    echo  [ERROR] La app cerro con un error.
    pause
)
