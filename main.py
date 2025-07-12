# Servidor Backend para Caffe & Miga - Mercado Pago Integration
# Python Flask Backend

from flask import Flask, request, jsonify
from flask_cors import CORS
import mercadopago
import os
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)
CORS(app)  # Permitir requests desde el frontend

# Configuración de Mercado Pago
# IMPORTANTE: Reemplaza "PROD_ACCESS_TOKEN" con tu Access Token real
# El Access Token se ve así: "APP_USR-1234567890123456-070112-abcdef1234567890abcdef1234567890-123456789"
PROD_ACCESS_TOKEN = "PROD_ACCESS_TOKEN"  # ← CAMBIAR POR TU ACCESS TOKEN REAL

# Datos de tu aplicación (ya los tienes):
# User ID: 1016726005
# Número de aplicación: 660730758522573
# Integración: CheckoutPro
# Modelo: Marketplace, BilleteraMercadopago

# Inicializar SDK de Mercado Pago
try:
    sdk = mercadopago.SDK(PROD_ACCESS_TOKEN)
    logger.info("✅ SDK de Mercado Pago inicializado correctamente")
except Exception as e:
    logger.error(f"❌ Error inicializando SDK: {e}")
    sdk = None

# Configuración del servidor
PORT = int(os.getenv('PORT', 3000))
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

@app.route('/', methods=['GET'])
def health_check():
    """Verificar que el servidor esté funcionando"""
    return jsonify({
        "status": "ok",
        "message": "Servidor Caffe & Miga funcionando",
        "timestamp": datetime.now().isoformat(),
        "mercadopago_status": "connected" if sdk else "error"
    })

@app.route('/create_preference', methods=['POST'])
def create_preference():
    """Crear preferencia de pago para Mercado Pago"""
    try:
        if not sdk:
            raise Exception("SDK de Mercado Pago no inicializado")
        
        # Obtener datos del request
        data = request.get_json()
        logger.info(f"📦 Creando preferencia para: {data.get('payer', {}).get('name', 'Cliente sin nombre')}")
        
        # Validar datos requeridos
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({"error": "No se encontraron items en el pedido"}), 400
        
        # Calcular total para validación
        total = sum(item['unit_price'] * item['quantity'] for item in data['items'])
        logger.info(f"💰 Total del pedido: ${total}")
        
        # Configurar preferencia
        preference_data = {
            "items": data['items'],
            "payer": {
                "name": data.get('payer', {}).get('name', ''),
                "surname": "",
                "email": data.get('payer', {}).get('email', ''),
                "phone": {
                    "area_code": data.get('payer', {}).get('phone', {}).get('area_code', '502'),
                    "number": data.get('payer', {}).get('phone', {}).get('number', '')
                }
            },
            "back_urls": {
                "success": data.get('back_urls', {}).get('success', 'http://localhost:8000/success.html'),
                "failure": data.get('back_urls', {}).get('failure', 'http://localhost:8000/failure.html'),
                "pending": data.get('back_urls', {}).get('pending', 'http://localhost:8000/pending.html')
            },
            "auto_return": "approved",
            "payment_methods": {
                "excluded_payment_methods": [],
                "excluded_payment_types": [],
                "installments": 12  # Máximo 12 cuotas
            },
            "notification_url": f"http://localhost:{PORT}/webhook",  # URL para webhooks
            "statement_descriptor": "CAFFE&MIGA",
            "external_reference": data.get('external_reference', f"caffeymiga_{int(datetime.now().timestamp())}"),
            "expires": False,
            "metadata": data.get('metadata', {})
        }
        
        # Crear preferencia en Mercado Pago
        preference_response = sdk.preference().create(preference_data)
        
        if preference_response["status"] == 201:
            preference = preference_response["response"]
            logger.info(f"✅ Preferencia creada: {preference['id']}")
            
            return jsonify({
                "id": preference["id"],
                "init_point": preference["init_point"],
                "sandbox_init_point": preference.get("sandbox_init_point"),
                "status": "success",
                "external_reference": preference.get("external_reference"),
                "total": total
            })
        else:
            logger.error(f"❌ Error creando preferencia: {preference_response}")
            return jsonify({
                "error": "Error al crear preferencia de pago",
                "details": preference_response
            }), 400
            
    except Exception as e:
        logger.error(f"❌ Error en create_preference: {str(e)}")
        return jsonify({
            "error": "Error interno del servidor",
            "message": str(e)
        }), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recibir notificaciones de Mercado Pago"""
    try:
        data = request.get_json()
        logger.info(f"🔔 Webhook recibido: {data}")
        
        # Verificar tipo de notificación
        if data.get('type') == 'payment':
            payment_id = data.get('data', {}).get('id')
            
            if payment_id:
                # Obtener información del pago
                payment_info = sdk.payment().get(payment_id)
                
                if payment_info["status"] == 200:
                    payment = payment_info["response"]
                    status = payment.get('status')
                    external_reference = payment.get('external_reference')
                    
                    logger.info(f"💳 Pago {payment_id}: {status}")
                    
                    # Aquí puedes procesar según el estado del pago
                    if status == 'approved':
                        logger.info(f"✅ Pago aprobado: {external_reference}")
                        # Aquí podrías enviar WhatsApp automático, guardar en BD, etc.
                        
                    elif status == 'rejected':
                        logger.info(f"❌ Pago rechazado: {external_reference}")
                        
                    elif status == 'pending':
                        logger.info(f"⏳ Pago pendiente: {external_reference}")
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"❌ Error en webhook: {str(e)}")
        return jsonify({"error": "Error procesando webhook"}), 500

@app.route('/payment_status/<payment_id>', methods=['GET'])
def get_payment_status(payment_id):
    """Obtener estado de un pago específico"""
    try:
        if not sdk:
            raise Exception("SDK no inicializado")
        
        payment_info = sdk.payment().get(payment_id)
        
        if payment_info["status"] == 200:
            payment = payment_info["response"]
            return jsonify({
                "id": payment["id"],
                "status": payment["status"],
                "status_detail": payment.get("status_detail"),
                "external_reference": payment.get("external_reference"),
                "transaction_amount": payment.get("transaction_amount"),
                "currency_id": payment.get("currency_id"),
                "date_created": payment.get("date_created"),
                "date_approved": payment.get("date_approved")
            })
        else:
            return jsonify({"error": "Pago no encontrado"}), 404
            
    except Exception as e:
        logger.error(f"❌ Error obteniendo estado del pago: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Iniciando servidor Caffe & Miga")
    print(f"📍 Puerto: {PORT}")
    print(f"🔧 Debug: {DEBUG}")
    print(f"💳 Mercado Pago: {'✅ Conectado' if sdk else '❌ Error'}")
    print("="*50 + "\n")
    
    if not sdk:
        print("⚠️  ADVERTENCIA: Configura tu PROD_ACCESS_TOKEN en la línea 19")
        print("💡 Tu Access Token se ve así: APP_USR-xxxxxxxxx-xxxxxx-xxxxxxxxxxxxx-xxxxxxxxx")
        print()
    
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
