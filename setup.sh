#!/bin/bash
# Script de instalación y ejecución para Caffe & Miga Backend

echo "🚀 Configurando backend de Caffe & Miga..."

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Por favor instala Python 3.8 o superior."
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "⚙️  Creando archivo .env..."
    cp .env.example .env
    echo "🔑 Por favor edita el archivo .env y agrega tu PROD_ACCESS_TOKEN"
fi

echo ""
echo "✅ Instalación completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Edita el archivo .env y agrega tu Access Token"
echo "2. Ejecuta: python main.py"
echo ""
echo "🔗 Tu Access Token está en: https://developers.mercadopago.com"
