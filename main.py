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

# ===============================
# 🔥 SISTEMA POS INTEGRADO 🔥
# ===============================

@app.route('/pos/orders', methods=['GET', 'POST'])
def pos_orders():
    """Obtener todos los pedidos para el sistema POS o crear un pedido nuevo (efectivo/terminal)"""
    
    if request.method == 'POST':
        # Crear pedido en efectivo o terminal
        try:
            data = request.get_json()
            logger.info(f"📦 Procesando pedido {data.get('payment_method', 'efectivo')}: {data.get('payer', {}).get('name', 'Sin nombre')}")
            
            # Validar datos requeridos
            if not data.get('items') or len(data['items']) == 0:
                return jsonify({"error": "No se encontraron items en el pedido"}), 400
            
            # Calcular total
            total = sum(item.get('unit_price', 0) * item.get('quantity', 1) for item in data['items'])
            
            # Crear ID único para el pedido
            order_id = f"efectivo_{int(datetime.now().timestamp())}"
            
            # Estructura del pedido para Firebase
            order_data = {
                'id': order_id,
                'preference_id': order_id,
                'firebase_id': order_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'pending',
                'payment_status': 'pending_cash' if data.get('payment_method') == 'efectivo' else 'pending_terminal',
                'pos_status': 'nuevo',
                'total': total,
                'customer': {
                    'name': data.get('payer', {}).get('name', ''),
                    'phone': data.get('payer', {}).get('phone', {}).get('number', ''),
                    'email': data.get('payer', {}).get('email', ''),
                    'payment_method': data.get('payment_method', 'efectivo')
                },
                'items': data.get('items', []),
                'metadata': data.get('metadata', {}),
                'notes': data.get('notes', ''),
                'source': 'web_cash_order'
            }
            
            # Guardar en Firebase
            firebase_result = firebase_manager.save_order(order_data)
            
            if firebase_result:
                logger.info(f"✅ Pedido {data.get('payment_method')} guardado: {order_id}")
                
                return jsonify({
                    "success": True,
                    "message": f"Pedido {data.get('payment_method')} procesado correctamente",
                    "order_id": order_id,
                    "total": total,
                    "payment_method": data.get('payment_method'),
                    "customer_name": data.get('payer', {}).get('name', ''),
                    "pickup_time": data.get('metadata', {}).get('pickup_time', '')
                })
            else:
                return jsonify({"error": "Error guardando el pedido"}), 500
                
        except Exception as e:
            logger.error(f"❌ Error procesando pedido efectivo/terminal: {str(e)}")
            return jsonify({"error": f"Error al procesar el pedido: {str(e)}"}), 500
    
    # Si es GET, continuar con la lógica original
    try:
        orders = firebase_manager.get_all_orders()
        
        # Formatear pedidos para el POS
        formatted_orders = []
        for order in orders:
            # Extraer información del cliente
            customer = order.get('customer', {})
            items = order.get('items', [])
            
            # Formatear para compatibilidad con el POS
            formatted_order = {
                'id': order.get('id', ''),
                'firebase_id': order.get('firebase_id', ''),
                'preference_id': order.get('preference_id', ''),
                'cliente': {
                    'nombre': customer.get('name', 'Cliente Web'),
                    'telefono': customer.get('phone', 'N/A'),
                    'email': customer.get('email', 'N/A')
                },
                'productos': [],
                'total': order.get('total', 0),
                'metodo_pago': customer.get('payment_method', 'Tarjeta'),
                'estado': order.get('status', 'pending'),
                'pos_status': order.get('pos_status', 'nuevo'),
                'fecha': order.get('timestamp', datetime.now().isoformat()),
                'payment_status': order.get('payment_status', 'pending')
            }
            
            # Formatear productos
            for item in items:
                formatted_order['productos'].append({
                    'nombre': item.get('title', 'Producto'),
                    'cantidad': item.get('quantity', 1),
                    'precio': item.get('unit_price', 0),
                    'descripcion': item.get('description', '')
                })
            
            formatted_orders.append(formatted_order)
        
        logger.info(f"📋 Enviando {len(formatted_orders)} pedidos al POS")
        
        return jsonify({
            "status": "success",
            "orders": formatted_orders,
            "count": len(formatted_orders),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo pedidos POS: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "orders": []
        }), 500

@app.route('/pos/order/<order_id>/status', methods=['PUT'])
def update_pos_order_status(order_id):
    """Actualizar estado de pedido desde el POS"""
    try:
        data = request.get_json()
        new_status = data.get('status', 'nuevo')
        
        # Estados válidos para el POS
        valid_statuses = ['nuevo', 'preparando', 'listo', 'entregado', 'cancelado']
        
        if new_status not in valid_statuses:
            return jsonify({
                "error": f"Estado inválido. Debe ser uno de: {valid_statuses}"
            }), 400
        
        # Actualizar en Firebase
        success = firebase_manager.update_order_status(order_id, {
            'pos_status': new_status,
            'last_updated': datetime.now().isoformat()
        })
        
        if success:
            logger.info(f"✅ Estado del pedido {order_id} actualizado a: {new_status}")
            return jsonify({
                "status": "success",
                "message": f"Pedido actualizado a {new_status}",
                "order_id": order_id,
                "new_status": new_status
            })
        else:
            return jsonify({"error": "No se pudo actualizar el pedido"}), 500
            
    except Exception as e:
        logger.error(f"❌ Error actualizando estado POS: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/pos/sync', methods=['POST'])
def sync_pos_orders():
    """Sincronizar pedidos entre web y POS"""
    try:
        # Obtener pedidos nuevos desde Firebase
        orders = firebase_manager.get_orders_by_status('approved')
        
        # Filtrar solo pedidos no procesados por el POS
        new_orders = []
        for order in orders:
            if order.get('pos_status', 'nuevo') == 'nuevo':
                new_orders.append(order)
        
        logger.info(f"🔄 Sincronizando {len(new_orders)} pedidos nuevos")
        
        return jsonify({
            "status": "success",
            "new_orders": len(new_orders),
            "orders": new_orders,
            "message": f"Sincronización completada: {len(new_orders)} pedidos nuevos"
        })
        
    except Exception as e:
        logger.error(f"❌ Error en sincronización POS: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/pos/stats', methods=['GET'])
def get_pos_stats():
    """Obtener estadísticas para el POS"""
    try:
        orders = firebase_manager.get_all_orders()
        
        # Calcular estadísticas
        stats = {
            'total_orders': len(orders),
            'pending_orders': 0,
            'completed_orders': 0,
            'total_revenue': 0,
            'orders_by_status': {
                'nuevo': 0,
                'preparando': 0,
                'listo': 0,
                'entregado': 0,
                'cancelado': 0
            },
            'orders_today': 0
        }
        
        today = datetime.now().date()
        
        for order in orders:
            # Contar por estado POS
            pos_status = order.get('pos_status', 'nuevo')
            if pos_status in stats['orders_by_status']:
                stats['orders_by_status'][pos_status] += 1
            
            # Contar pagos aprobados
            if order.get('payment_status') == 'approved':
                stats['completed_orders'] += 1
                stats['total_revenue'] += order.get('total', 0)
            else:
                stats['pending_orders'] += 1
            
            # Contar pedidos de hoy
            try:
                order_date = datetime.fromisoformat(order.get('timestamp', '')).date()
                if order_date == today:
                    stats['orders_today'] += 1
            except:
                pass
        
        return jsonify({
            "status": "success",
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas POS: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/pos/test', methods=['GET'])
def test_pos_connection():
    """Probar conexión del POS"""
    try:
        # Verificar conexión a Firebase
        firebase_status = "connected" if firebase_manager.db else "disconnected"
        
        # Contar pedidos
        orders = firebase_manager.get_all_orders()
        order_count = len(orders)
        
        return jsonify({
            "status": "success",
            "message": "Conexión POS exitosa",
            "firebase_status": firebase_status,
            "order_count": order_count,
            "server_time": datetime.now().isoformat(),
            "endpoints": {
                "get_orders": "/pos/orders",
                "update_status": "/pos/order/<id>/status",
                "sync": "/pos/sync",
                "stats": "/pos/stats"
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error en test POS: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

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
