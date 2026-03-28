@echo off
REM ================================================================
REM Script de compilación para WiFi Planner Pro v3.0
REM ================================================================

echo.
echo ================================================================
echo  WiFi Planner Pro v3.0 - PROFESSIONAL EDITION
echo  Compilador automatico
echo ================================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no instalado
    pause
    exit /b 1
)

echo [OK] Python detectado
echo.

REM Verificar archivos
if not exist "wifi_planner_v3.py" (
    echo [ERROR] No se encuentra wifi_planner_v3.py
    pause
    exit /b 1
)

if not exist "wifi_planner_v3.html" (
    echo [ERROR] No se encuentra wifi_planner_v3.html
    pause
    exit /b 1
)

echo [OK] Archivos fuente encontrados
echo.

REM Instalar dependencias
echo ================================================================
echo  Instalando dependencias...
echo ================================================================
echo.

pip install pywebview pymupdf pillow psutil pyinstaller
if errorlevel 1 (
    echo [ERROR] Fallo instalacion de dependencias
    pause
    exit /b 1
)

echo.
echo [OK] Dependencias instaladas
echo.

REM Limpiar
echo ================================================================
echo  Limpiando compilaciones anteriores...
echo ================================================================
echo.

if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del /q *.spec

echo [OK] Limpieza completada
echo.

REM Compilar
echo ================================================================
echo  Compilando WiFi Planner Pro v3.0...
echo ================================================================
echo.
echo Esto puede tomar 3-7 minutos. Por favor espera...
echo.

pyinstaller ^
  --onefile ^
  --noconsole ^
  --name "WiFi_Planner_Pro_v3" ^
  --add-data "wifi_planner_v3.html;." ^
  --hidden-import "fitz" ^
  --hidden-import "PIL" ^
  --hidden-import "psutil" ^
  --optimize=2 ^
  --noupx ^
  --clean ^
  wifi_planner_v3.py

if errorlevel 1 (
    echo.
    echo [ERROR] Compilacion fallida
    pause
    exit /b 1
)

echo.
echo ================================================================
echo  COMPILACION EXITOSA!
echo ================================================================
echo.
echo Ejecutable: dist\WiFi_Planner_Pro_v3.exe
echo.

if exist "dist\WiFi_Planner_Pro_v3.exe" (
    for %%A in ("dist\WiFi_Planner_Pro_v3.exe") do (
        set size=%%~zA
    )
    
    echo [OK] Tamaño: %size% bytes (~35-45 MB)
    echo.
    echo ================================================================
    echo  CARACTERISTICAS v3.0:
    echo ================================================================
    echo.
    echo  - Soporte PDF nativo (carga PDFs directamente)
    echo  - Optimizacion multi-core (50+ APs sin lag)
    echo  - Herramientas avanzadas dibujo (linea/rectangulo/poligono)
    echo  - Gestion completa proyectos (Nuevo/Guardar/Cargar)
    echo  - Deteccion automatica recursos del sistema
    echo  - Renderizado asincronico optimizado
    echo.
    echo ================================================================
    echo  USO:
    echo ================================================================
    echo.
    echo  1. Copiar WiFi_Planner_Pro_v3.exe a cualquier ubicacion
    echo  2. Ejecutar directamente (doble clic)
    echo  3. No requiere Python en PC destino
    echo  4. Portable - no requiere instalacion
    echo.
    
    choice /C SN /M "Abrir carpeta dist?"
    if errorlevel 2 goto :end
    if errorlevel 1 start "" "dist"
) else (
    echo [ERROR] Ejecutable no encontrado
    echo.
)

:end
echo.
pause
