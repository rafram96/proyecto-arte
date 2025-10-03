@echo off
REM Script de inicio rápido para Windows
REM Pintura Interactiva con Gestos - Transgresión Digital

echo ========================================
echo  Pintura con Gestos - Transgresion Digital
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo Por favor, instala Python 3.8 o superior desde https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python detectado
echo.

REM Verificar si las dependencias están instaladas
echo Verificando dependencias...
python -c "import cv2, mediapipe, numpy" >nul 2>&1
if errorlevel 1 (
    echo [ADVERTENCIA] Algunas dependencias no estan instaladas
    echo.
    echo Deseas instalarlas ahora? (S/N)
    set /p install="Respuesta: "
    if /i "%install%"=="S" (
        echo.
        echo Instalando dependencias...
        python -m pip install -r requirements.txt
        if errorlevel 1 (
            echo [ERROR] Fallo la instalacion de dependencias
            pause
            exit /b 1
        )
        echo [OK] Dependencias instaladas correctamente
    ) else (
        echo Por favor, instala las dependencias manualmente:
        echo   pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo [OK] Dependencias verificadas
echo.

REM Preguntar qué hacer
echo Que deseas hacer?
echo   1. Ejecutar la aplicacion principal
echo   2. Ejecutar demo de diagnostico
echo   3. Ejecutar tests
echo   4. Ver ayuda
echo   5. Salir
echo.
set /p choice="Elige una opcion (1-5): "

if "%choice%"=="1" (
    echo.
    echo Iniciando aplicacion principal...
    echo Presiona 'q' para salir
    echo.
    python src/main.py
) else if "%choice%"=="2" (
    echo.
    echo Ejecutando demo de diagnostico...
    echo.
    python scripts/demo.py
) else if "%choice%"=="3" (
    echo.
    echo Ejecutando tests...
    echo.
    python -m pytest tests/ -v
) else if "%choice%"=="4" (
    echo.
    echo ========================================
    echo AYUDA - PINTURA CON GESTOS
    echo ========================================
    echo.
    echo CONTROLES DE TECLADO:
    echo   q - Salir del programa
    echo   c - Borrar lienzo
    echo   1, 2, 3, 4 - Cambiar color
    echo   t - Cambiar tipo de pincel
    echo   s - Cambiar tamano de pincel
    echo.
    echo GESTO DE DIBUJO:
    echo   - Extiende SOLO el dedo indice
    echo   - Mantén los demas dedos flexionados
    echo   - Observa el feedback visual
    echo.
    echo DOCUMENTACION:
    echo   README.md - Documentacion principal
    echo   ARCHITECTURE.md - Arquitectura del sistema
    echo   CONTRIBUTING.md - Guia de contribucion
    echo.
    pause
) else if "%choice%"=="5" (
    echo Saliendo...
    exit /b 0
) else (
    echo Opcion invalida
    pause
    exit /b 1
)

echo.
pause
