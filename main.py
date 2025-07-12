# Servidor Backend para Caffe & Miga - Mercado Pago Integration
# Python Flask Backend

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import mercadopago
import os
from datetime import datetime
import logging
from dotenv import load_dotenv
from firebase_config import firebase_manager

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación Flask con soporte para archivos estáticos
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Permitir requests desde el frontend

# Configuración de Mercado Pago - Leer desde .env
PROD_ACCESS_TOKEN = os.getenv('PROD_ACCESS_TOKEN')
TEST_ACCESS_TOKEN = os.getenv('TEST_ACCESS_TOKEN', 'TEST-8414674373408503-071123-82b03c16c0be00421b1f1c9ad6e8958d-1016726005')

# Usar modo de prueba para desarrollo
USE_TEST_MODE = os.getenv('USE_TEST_MODE', 'True').lower() == 'true'
ACCESS_TOKEN = TEST_ACCESS_TOKEN if USE_TEST_MODE else PROD_ACCESS_TOKEN

if not ACCESS_TOKEN:
    logger.error("❌ ACCESS TOKEN no encontrado")
    logger.error("❌ Asegúrate de que existe el archivo .env con PROD_ACCESS_TOKEN=tu_token")
else:
    mode = "TEST" if USE_TEST_MODE else "PRODUCCIÓN"
    logger.info(f"✅ Access Token cargado ({mode}): {ACCESS_TOKEN[:20]}...")

# Datos de tu aplicación (ya los tienes):
# User ID: 1016726005
# Número de aplicación: 660730758522573
# Integración: CheckoutPro
# Modelo: Marketplace, BilleteraMercadopago

# Inicializar SDK de Mercado Pago
try:
    sdk = mercadopago.SDK(ACCESS_TOKEN)
    logger.info("✅ SDK de Mercado Pago inicializado correctamente")
except Exception as e:
    logger.error(f"❌ Error inicializando SDK: {e}")
    sdk = None

# Configuración del servidor
PORT = int(os.getenv('PORT', 3000))
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

@app.route('/', methods=['GET'])
def serve_index():
    """Servir la página principal"""
    return send_file('index.html')

@app.route('/health', methods=['GET'])
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
        
        # Procesar items y asegurar que tengan currency_id
        processed_items = []
        for item in data['items']:
            processed_item = {
                "id": item.get('id', 'item'),
                "title": item.get('title', 'Producto'),
                "currency_id": "MXN",  # Moneda de México
                "picture_url": item.get('picture_url', ''),
                "description": item.get('description', ''),
                "category_id": item.get('category_id', 'food'),
                "quantity": int(item.get('quantity', 1)),
                "unit_price": float(item.get('unit_price', 0))
            }
            processed_items.append(processed_item)
        
        # Calcular total para validación
        total = sum(item['unit_price'] * item['quantity'] for item in processed_items)
        logger.info(f"💰 Total del pedido: ${total}")
        
        # Configurar preferencia
        preference_data = {
            "items": processed_items,
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
                "success": "http://localhost:8000/success.html",
                "failure": "http://localhost:8000/failure.html",
                "pending": "http://localhost:8000/pending.html"
            },
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
            
            # 🔥 GUARDAR PEDIDO EN FIREBASE 🔥
            order_data = {
                "preference_id": preference["id"],
                "external_reference": preference.get("external_reference"),
                "customer": {
                    "name": data.get('payer', {}).get('name', ''),
                    "email": data.get('payer', {}).get('email', ''),
                    "phone": data.get('payer', {}).get('phone', {}).get('number', ''),
                    "payment_method": data.get('payment_method', 'tarjeta')
                },
                "items": processed_items,
                "total": total,
                "currency": "MXN",
                "payment_status": "pending",
                "metadata": data.get('metadata', {}),
                "notes": data.get('notes', ''),
                "source": "web_ecommerce"
            }
            
            # Guardar en Firebase
            order_id = firebase_manager.save_order(order_data)
            if order_id:
                logger.info(f"🔥 Pedido guardado en Firebase: {order_id}")
            else:
                logger.warning("⚠️ No se pudo guardar en Firebase, continuando...")
            
            return jsonify({
                "id": preference["id"],
                "init_point": preference["init_point"],
                "sandbox_init_point": preference.get("sandbox_init_point"),
                "status": "success",
                "external_reference": preference.get("external_reference"),
                "total": total,
                "firebase_order_id": order_id
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
                    
                    # 🔥 ACTUALIZAR ESTADO EN FIREBASE 🔥
                    payment_data = {
                        'status': status,
                        'payment_id': payment_id,
                        'external_reference': external_reference,
                        'payment_method': payment.get('payment_method_id'),
                        'amount': payment.get('transaction_amount')
                    }
                    
                    # Buscar el pedido por external_reference y actualizar
                    # (En una implementación más robusta, almacenarías la relación preference_id -> firebase_order_id)
                    
                    # Aquí puedes procesar según el estado del pago
                    if status == 'approved':
                        logger.info(f"✅ Pago aprobado: {external_reference}")
                        logger.info(f"🔥 Pedido listo para preparar en el POS!")
                        # Firebase automáticamente notificará al POS
                        
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

# 🔥 ENDPOINTS PARA EL SISTEMA POS 🔥

@app.route('/pos/orders', methods=['GET', 'POST'])
def handle_pos_orders():
    """Manejar pedidos del POS - GET para obtener, POST para crear"""
    if request.method == 'GET':
        # Obtener pedidos pendientes para el POS
        try:
            orders = firebase_manager.get_pending_orders()
            return jsonify({
                "orders": orders,
                "count": len(orders),
                "status": "success"
            })
        except Exception as e:
            logger.error(f"❌ Error obteniendo pedidos POS: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'POST':
        # Crear nuevo pedido directo al sistema POS
        try:
            data = request.get_json()
            logger.info(f"📦 Recibiendo pedido directo para POS: {data.get('payer', {}).get('name', 'Sin nombre')}")
            
            # Validar datos requeridos
            if not data or 'items' not in data or 'payer' not in data:
                return jsonify({"error": "Datos incompletos"}), 400
            
            # Preparar datos del pedido para Firebase
            order_data = {
                "customer_info": {
                    "name": data['payer']['name'],
                    "phone": data['payer']['phone']['number'],
                    "email": data['payer'].get('email', f"{data['payer']['phone']['number']}@caffeymiga.com")
                },
                "items": data['items'],
                "payment_method": data.get('payment_method', 'efectivo'),
                "notes": data.get('notes', ''),
                "metadata": data.get('metadata', {}),
                "status": "pendiente",
                "pos_ready": True,  # Marca que está listo para el POS
                "created_at": datetime.now().isoformat(),
                "source": "web_direct_pos"
            }
            
            # Guardar en Firebase
            order_id = firebase_manager.save_order(order_data)
            
            logger.info(f"🔥 Pedido directo guardado en Firebase: {order_id}")
            
            return jsonify({
                "message": "Pedido enviado al sistema POS",
                "order_id": order_id,
                "status": "success"
            })
            
        except Exception as e:
            logger.error(f"❌ Error procesando pedido directo: {str(e)}")
            return jsonify({"error": f"Error interno: {str(e)}"}), 500

@app.route('/pos/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Actualizar estado de un pedido desde el POS"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        # Estados válidos: preparando, listo, entregado, cancelado
        valid_statuses = ['preparando', 'listo', 'entregado', 'cancelado']
        if new_status not in valid_statuses:
            return jsonify({"error": "Estado inválido"}), 400
        
        success = firebase_manager.update_order_status(order_id, new_status)
        
        if success:
            return jsonify({
                "message": f"Estado actualizado a: {new_status}",
                "order_id": order_id,
                "status": "success"
            })
        else:
            return jsonify({"error": "No se pudo actualizar el estado"}), 500
            
    except Exception as e:
        logger.error(f"❌ Error actualizando estado: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/pos/dashboard', methods=['GET'])
def pos_dashboard():
    """Dashboard simple para ver el estado del POS"""
    try:
        orders = firebase_manager.get_pending_orders()
        
        # Contar por estados
        stats = {
            'total': len(orders),
            'listo_para_preparar': 0,
            'preparando': 0,
            'listo': 0
        }
        
        for order in orders:
            status = order.get('pos_status', 'listo_para_preparar')
            if status in stats:
                stats[status] += 1
        
        return jsonify({
            "statistics": stats,
            "recent_orders": orders[:10],  # Últimos 10 pedidos
            "firebase_status": "connected" if firebase_manager.db else "disconnected"
        })
        
    except Exception as e:
        logger.error(f"❌ Error en dashboard POS: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

# Rutas para servir archivos estáticos
@app.route('/<path:filename>')
def serve_static_files(filename):
    """Servir archivos estáticos (CSS, JS, imágenes, etc.)"""
    return send_from_directory('.', filename)

@app.route('/img/<path:filename>')
def serve_images(filename):
    """Servir imágenes desde la carpeta img"""
    return send_from_directory('img', filename)

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
