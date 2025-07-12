@echo off
REM Script de instalación para Caffe & Miga Backend - Windows

echo 🚀 Configurando backend de Caffe & Miga...

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado. Por favor instala Python 3.8 o superior.
    pause
    exit /b 1
)

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo 📦 Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
echo 🔧 Activando entorno virtual...
call venv\Scripts\activate

REM Instalar dependencias
echo 📚 Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Crear archivo .env si no existe
if not exist ".env" (
    echo ⚙️  Creando archivo .env...
    copy .env.example .env
    echo 🔑 Por favor edita el archivo .env y agrega tu PROD_ACCESS_TOKEN
)

echo.
echo ✅ Instalación completada!
echo.
echo 📋 Próximos pasos:
echo 1. Edita el archivo .env y agrega tu Access Token
echo 2. Ejecuta: python main.py
echo.
echo 🔗 Tu Access Token está en: https://developers.mercadopago.com
pause
