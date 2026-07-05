@echo off
setlocal enabledelayedexpansion

:: Mantener ventana abierta siempre (auto-reinicio dentro de cmd /k)
if "%1"=="" (
    cmd /k "%~f0" RUN
    exit /b
)

title WiFi Planner Pro v3.3

:: Rutas del proyecto
set "BASE=%~dp0"
if "%BASE:~-1%"=="\" set "BASE=%BASE:~0,-1%"
set "PY_SCRIPT=%BASE%\wifi_planner_v3.py"
set "HTML_FILE=%BASE%\wifi_planner_v3.html"

cls
echo.
echo  ====================================================
echo    WiFi Planner Pro v3.3  -  Lanzador
echo  ====================================================
echo.
echo  Directorio: %BASE%
echo.

:: ============================================================
:: PASO 1 - Encontrar Python
:: ============================================================
echo  [1/4] Buscando Python...
set "PCMD="

python --version >nul 2>&1
if !ERRORLEVEL! EQU 0 set "PCMD=python"

if "!PCMD!"=="" (
    py --version >nul 2>&1
    if !ERRORLEVEL! EQU 0 set "PCMD=py"
)

if "!PCMD!"=="" (
    echo.
    echo  [!] Python no encontrado en PATH.
    goto :BROWSER_OPT
)

for /f "tokens=*" %%v in ('!PCMD! --version 2^>^&1') do set "PVER=%%v"
echo  [OK] !PVER! encontrado.
echo.

:: ============================================================
:: PASO 2 - Usar directamente Python del sistema (sin venv)
:: ============================================================
echo  [2/4] Usando Python del sistema...
echo  [OK] No se necesita entorno virtual.
echo.

:: ============================================================
:: PASO 3 - Verificar e instalar dependencias
:: ============================================================
echo  [3/4] Verificando dependencias...
echo.

:: --- pywebview (requerido) ---
!PCMD! -c "import webview" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo  [OK] pywebview ya instalado.
) else (
    echo  Instalando pywebview...
    !PCMD! -m pip install pywebview --quiet --no-warn-script-location
    if !ERRORLEVEL! NEQ 0 (
        echo.
        echo  [!] No se pudo instalar pywebview.
        echo  Abriendo la app en el navegador...
        timeout /t 3 /nobreak >nul
        goto :BROWSER
    )
    echo  [OK] pywebview instalado.
)

:: --- pymupdf (opcional, soporte PDF) ---
!PCMD! -c "import fitz" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo  [OK] pymupdf ya instalado.
) else (
    echo  Instalando pymupdf (soporte PDF)...
    !PCMD! -m pip install pymupdf --quiet --no-warn-script-location 2>nul
    !PCMD! -c "import fitz" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo  [OK] pymupdf instalado.
    ) else (
        echo  [--] pymupdf no disponible (PDF deshabilitado, no es critico).
    )
)

:: --- pillow (opcional, optimizacion de imagenes) ---
!PCMD! -c "from PIL import Image" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo  [OK] pillow ya instalado.
) else (
    echo  Instalando pillow...
    !PCMD! -m pip install pillow --quiet --no-warn-script-location 2>nul
    !PCMD! -c "from PIL import Image" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo  [OK] pillow instalado.
    ) else (
        echo  [--] pillow no disponible (no es critico).
    )
)

:: --- psutil (opcional, deteccion de hardware) ---
!PCMD! -c "import psutil" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo  [OK] psutil ya instalado.
) else (
    echo  Instalando psutil...
    !PCMD! -m pip install psutil --quiet --no-warn-script-location 2>nul
    !PCMD! -c "import psutil" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo  [OK] psutil instalado.
    ) else (
        echo  [--] psutil no disponible (no es critico).
    )
)

echo.
echo  Dependencias verificadas.
echo.

:: ============================================================
:: PASO 4 - Lanzar la app
:: ============================================================
:LAUNCH
echo  [4/4] Iniciando WiFi Planner Pro...
echo.

if not exist "%PY_SCRIPT%" (
    echo  [!] No se encontro: %PY_SCRIPT%
    echo  Abriendo en el navegador...
    timeout /t 2 /nobreak >nul
    goto :BROWSER
)

!PCMD! "%PY_SCRIPT%"
set "EC=!ERRORLEVEL!"

if !EC! NEQ 0 (
    echo.
    echo  [!] La app cerro con codigo de error: !EC!
    echo  Abriendo en el navegador como alternativa...
    timeout /t 3 /nobreak >nul
    goto :BROWSER
)

echo.
echo  App cerrada correctamente.
pause
exit /b 0

:: ============================================================
:: Sin Python - preguntar al usuario
:: ============================================================
:BROWSER_OPT
echo.
echo  Opciones:
echo    A - Abrir la app en el navegador (funciona sin Python)
echo    B - Abrir pagina de descarga de Python
echo    C - Salir
echo.
choice /C ABC /N /M "  Elige una opcion [A/B/C]: "
if !ERRORLEVEL! EQU 1 goto :BROWSER
if !ERRORLEVEL! EQU 2 (
    start https://www.python.org/downloads/
    echo.
    echo  Instala Python y vuelve a ejecutar este archivo.
    echo.
    pause
    exit /b 0
)
exit /b 0

:: ============================================================
:: Fallback - navegador
:: ============================================================
:BROWSER
if not exist "%HTML_FILE%" (
    echo.
    echo  [ERROR] No se encontro: %HTML_FILE%
    echo.
    echo  Archivos .html en %BASE%:
    dir "%BASE%\*.html" /b 2>nul || echo  (ninguno encontrado)
    echo.
    pause
    exit /b 1
)

echo  Abriendo en el navegador...
start "" "%HTML_FILE%"

echo.
echo  ====================================================
echo    App abierta en el navegador.
echo.
echo    NOTA: Sin pywebview estas funciones no funcionan:
echo      - Cargar PDF directamente
echo      - Guardado automatico de proyectos
echo      - Deteccion de hardware
echo  ====================================================
echo.
pause
exit /b 0
