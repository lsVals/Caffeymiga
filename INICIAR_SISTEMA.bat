@echo off
title Caffè & Miga - Sistema de Ventas
color 0A

echo.
echo  ===================================================
echo   ☕ CAFFÈ ^& MIGA - SISTEMA DE VENTAS ☕
echo  ===================================================
echo.

REM Verificar si existe el entorno virtual
if exist ".venv\Scripts\python.exe" (
    echo ✅ Entorno virtual encontrado
    echo 🚀 Iniciando sistema...
    echo.
    ".venv\Scripts\python.exe" launcher.py
) else (
    echo ❌ Entorno virtual no encontrado
    echo 🚀 Iniciando con Python del sistema...
    echo.
    python launcher.py
)

if errorlevel 1 (
    echo.
    echo ❌ Error al ejecutar el sistema
    echo 💡 Asegúrate de tener Python instalado
    pause
) else (
    echo.
    echo ✅ Sistema cerrado correctamente
)

pause
