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
import sqlite3
import json

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
@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de diagnóstico para verificar el estado del servidor"""
    try:
        # Verificar Firebase
        firebase_status = "OK"
        firebase_error = None
        try:
            if firebase_manager.db:
                # Intentar una consulta simple
                firebase_manager.db.collection('test').limit(1).get()
                firebase_status = "Connected"
            else:
                firebase_status = "Not initialized"
        except Exception as e:
            firebase_status = "Error"
            firebase_error = str(e)
        
        # Verificar Mercado Pago
        mp_status = "OK" if sdk else "Not initialized"
        
        # Verificar SQLite (solo en desarrollo)
        sqlite_status = "N/A (Production)"
        if os.getenv('ENVIRONMENT', 'development') == 'development':
            try:
                db_path = "cafeteria_sistema/pos_pedidos.db"
                if os.path.exists(db_path):
                    import sqlite3
                    conn = sqlite3.connect(db_path)
                    conn.close()
                    sqlite_status = "Connected"
                else:
                    sqlite_status = "Database not found"
            except Exception as e:
                sqlite_status = f"Error: {str(e)}"
        
        health_data = {
            "status": "OK",
            "timestamp": datetime.now().isoformat(),
            "environment": os.getenv('ENVIRONMENT', 'development'),
            "services": {
                "firebase": {
                    "status": firebase_status,
                    "error": firebase_error
                },
                "mercado_pago": {
                    "status": mp_status,
                    "mode": "TEST" if USE_TEST_MODE else "PRODUCTION"
                },
                "sqlite": {
                    "status": sqlite_status
                }
            }
        }
        
        return jsonify(health_data)
        
    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

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
                "currency_id": "MXN",  # Moneda de México (Peso mexicano)
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
                    "area_code": data.get('payer', {}).get('phone', {}).get('area_code', '52'),
                    "number": data.get('payer', {}).get('phone', {}).get('number', '')
                }
            },
            "back_urls": {
                "success": "https://lsvals.github.io/caffeymiga/success.html",
                "failure": "https://lsvals.github.io/caffeymiga/failure.html",
                "pending": "https://lsvals.github.io/caffeymiga/pending.html"
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
            
            # Guardar también en SQLite local
            save_order_to_sqlite(order_data)
            
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
            
            # Calcular total - soportar tanto 'price' como 'unit_price'
            total = 0
            for item in data['items']:
                price = item.get('unit_price', item.get('price', 0))
                quantity = item.get('quantity', 1)
                total += price * quantity
            
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
            
            # Intentar guardar en Firebase primero
            firebase_result = firebase_manager.save_order(order_data)
            
            if firebase_result:
                logger.info(f"✅ Pedido {data.get('payment_method')} guardado en Firebase: {order_id}")
                
                # Guardar también en SQLite local para sincronización con POS
                sqlite_result = save_order_to_sqlite(order_data)
                if sqlite_result:
                    logger.info(f"✅ Pedido {order_id} también guardado en SQLite local")
                else:
                    logger.warning(f"⚠️ Pedido {order_id} guardado en Firebase pero falló SQLite")
                
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
                # Si Firebase falla, intentar guardar solo localmente en SQLite
                logger.warning(f"⚠️ Firebase falló para pedido {order_id}, intentando solo SQLite")
                sqlite_result = save_order_to_sqlite(order_data)
                
                if sqlite_result:
                    logger.info(f"✅ Pedido {order_id} guardado solo en SQLite (Firebase no disponible)")
                    return jsonify({
                        "success": True,
                        "message": f"Pedido {data.get('payment_method')} procesado correctamente (solo local)",
                        "order_id": order_id,
                        "total": total,
                        "payment_method": data.get('payment_method'),
                        "customer_name": data.get('payer', {}).get('name', ''),
                        "pickup_time": data.get('metadata', {}).get('pickup_time', ''),
                        "warning": "Firebase no disponible - pedido guardado solo localmente"
                    })
                else:
                    return jsonify({"error": "Error guardando el pedido en Firebase y SQLite"}), 500
                
        except Exception as e:
            logger.error(f"❌ Error procesando pedido efectivo/terminal: {str(e)}")
            return jsonify({"error": f"Error al procesar el pedido: {str(e)}"}), 500
    
    # Si es GET, continuar con la lógica original
    try:
        # Obtener órdenes de Firebase
        firebase_orders = firebase_manager.get_all_orders()
        
        # Obtener órdenes pendientes en memoria
        pending_orders = getattr(app, 'pending_orders', [])
        
        # Combinar ambas fuentes
        all_orders = list(firebase_orders) + list(pending_orders)
        
        # Formatear pedidos para el POS
        formatted_orders = []
        for order in all_orders:
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

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Endpoint de prueba simple"""
    return jsonify({"message": "Servidor funcionando", "timestamp": datetime.now().isoformat()})

@app.route('/test/firebase', methods=['GET'])
def test_firebase():
    """Probar solo Firebase"""
    try:
        if firebase_manager.db:
            return jsonify({"firebase": "OK", "status": "connected"})
        else:
            return jsonify({"firebase": "ERROR", "status": "not_initialized"}), 500
    except Exception as e:
        return jsonify({"firebase": "ERROR", "error": str(e)}), 500

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

def save_order_to_sqlite(order_data):
    """Guardar pedido también en SQLite local para sincronización con POS"""
    try:
        # En producción (Render), guardar en memoria para sincronización
        if os.getenv('ENVIRONMENT') == 'production':
            logger.info("🌐 Entorno de producción - guardando en memoria para sincronización")
            
            # Crear estructura para sincronización
            order_for_sync = {
                'id': order_data.get('id', f"web_{int(datetime.now().timestamp())}"),
                'cliente': {
                    'nombre': order_data.get('customer', {}).get('name', 'Cliente Web'),
                    'telefono': order_data.get('customer', {}).get('phone', 'N/A'),
                    'email': order_data.get('customer', {}).get('email', 'N/A')
                },
                'productos': [],
                'total': order_data.get('total', 0),
                'metodo_pago': order_data.get('customer', {}).get('payment_method', 'efectivo'),
                'estado': 'pending',
                'pos_status': 'nuevo',
                'fecha': order_data.get('timestamp', datetime.now().isoformat()),
                'metadata': order_data.get('metadata', {}),
                'payment_status': order_data.get('payment_status', 'pending')
            }
            
            # Formatear productos
            for item in order_data.get('items', []):
                order_for_sync['productos'].append({
                    'nombre': item.get('title', 'Producto'),
                    'cantidad': item.get('quantity', 1),
                    'precio': item.get('unit_price', item.get('price', 0)),
                    'descripcion': item.get('description', '')
                })
            
            # Guardar en variable global para endpoint
            if not hasattr(app, 'pending_orders'):
                app.pending_orders = []
            
            app.pending_orders.append(order_for_sync)
            
            # Mantener solo los últimos 50 pedidos en memoria
            if len(app.pending_orders) > 50:
                app.pending_orders = app.pending_orders[-50:]
            
            logger.info(f"✅ Pedido guardado en memoria para sincronización: {order_for_sync['id']}")
            return True
        
        # En desarrollo local, usar SQLite
        db_path = "pos_pedidos.db"  # Usar la base de datos en el directorio raíz
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Generar ID único para el pedido
        order_id = order_data.get('external_reference', f"web_{int(datetime.now().timestamp())}")
        customer = order_data.get('customer', {})
        items = order_data.get('items', [])
        metadata = order_data.get('metadata', {})
        
        # Formatear items con nombres de productos reales
        formatted_items = []
        for item in items:
            formatted_items.append({
                "name": item.get('title', 'Producto'),
                "price": item.get('unit_price', 0),
                "quantity": item.get('quantity', 1),
                "description": item.get('description', '')
            })
        
        items_json = json.dumps(formatted_items, ensure_ascii=False)
        
        # Insertar en la tabla pedidos
        c.execute("""
            INSERT INTO pedidos (id, cliente_nombre, cliente_telefono, hora_recogida, 
                               items, total, estado, metodo_pago, fecha_creacion, fecha_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_id,
            customer.get('name', ''),
            customer.get('phone', ''),
            metadata.get('pickup_time', ''),
            items_json,
            order_data.get('total', 0),
            'pendiente',
            customer.get('payment_method', 'mercado_pago'),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Pedido guardado en SQLite: {order_id}")
        logger.info(f"📱 Cliente: {customer.get('name', '')}")
        logger.info(f"💰 Total: ${order_data.get('total', 0)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error guardando en SQLite: {e}")
        return False
        return False

@app.route('/pos/orders/simple', methods=['POST'])
def pos_orders_simple():
    """Endpoint simplificado para crear pedidos y guardar en SQLite"""
    try:
        data = request.get_json()
        customer_name = data.get('customer_name', data.get('payer', {}).get('name', 'Sin nombre'))
        logger.info(f"📦 Procesando pedido simple: {customer_name}")
        
        # Validar datos requeridos
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({"error": "No se encontraron items en el pedido"}), 400
        
        # Calcular total
        total = sum(item.get('price', 0) * item.get('quantity', 1) for item in data['items'])
        
        # Crear ID único para el pedido
        order_id = f"simple_{int(datetime.now().timestamp())}"
        
        # Preparar datos para SQLite
        order_data = {
            'id': order_id,
            'cliente_nombre': customer_name,
            'cliente_telefono': data.get('customer_phone', ''),
            'hora_recogida': data.get('pickup_time', ''),
            'items': json.dumps(data.get('items', []), ensure_ascii=False),
            'total': total,
            'estado': 'pendiente',
            'metodo_pago': data.get('payment_method', 'efectivo'),
            'fecha_creacion': datetime.now().isoformat(),
            'fecha_actualizacion': datetime.now().isoformat()
        }
        
        # Guardar en SQLite
        try:
            save_order_to_sqlite(order_data)
            logger.info(f"✅ Pedido guardado en SQLite: {order_id}")
        except Exception as sqlite_error:
            logger.error(f"❌ Error guardando en SQLite: {sqlite_error}")
        
        logger.info(f"✅ Pedido simple procesado: {order_id} - Total: ${total}")
        
        return jsonify({
            "success": True,
            "message": "Pedido procesado correctamente (modo simple)",
            "order_id": order_id,
            "total": total,
            "payment_method": data.get('payment_method', 'efectivo'),
            "customer_name": customer_name,
            "pickup_time": data.get('pickup_time', '')
        })
        
    except Exception as e:
        logger.error(f"❌ Error procesando pedido simple: {str(e)}")
        return jsonify({"error": f"Error al procesar el pedido: {str(e)}"}), 500

@app.route('/pos/orders/basic', methods=['POST'])
def pos_orders_basic():
    """Endpoint básico para crear pedidos - solo respuesta exitosa"""
    try:
        data = request.get_json()
        logger.info(f"📦 Procesando pedido básico: {data.get('payer', {}).get('name', 'Sin nombre')}")
        
        # Validar datos requeridos
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({"error": "No se encontraron items en el pedido"}), 400
        
        # Calcular total
        total = sum(item.get('price', 0) * item.get('quantity', 1) for item in data['items'])
        
        # Crear ID único para el pedido
        order_id = f"basic_{int(datetime.now().timestamp())}"
        
        logger.info(f"✅ Pedido básico procesado: {order_id} - Total: ${total}")
        
        return jsonify({
            "success": True,
            "message": f"Pedido {data.get('payment_method')} procesado correctamente (modo básico)",
            "order_id": order_id,
            "total": total,
            "payment_method": data.get('payment_method', 'efectivo'),
            "customer_name": data.get('payer', {}).get('name', ''),
            "pickup_time": data.get('metadata', {}).get('pickup_time', '')
        })
        
    except Exception as e:
        logger.error(f"❌ Error procesando pedido básico: {str(e)}")
        return jsonify({"error": f"Error al procesar el pedido: {str(e)}"}), 500

@app.route('/test/mercadopago', methods=['GET', 'POST'])
def test_mercadopago():
    """Endpoint de prueba para verificar Mercado Pago"""
    try:
        if not sdk:
            return jsonify({
                "status": "error",
                "message": "SDK de Mercado Pago no inicializado",
                "access_token_configured": bool(ACCESS_TOKEN),
                "test_mode": USE_TEST_MODE
            }), 500
        
        # Crear una preferencia de prueba simple
        test_preference = {
            "items": [
                {
                    "id": "test_item",
                    "title": "Producto de Prueba",
                    "currency_id": "MXN",  # Moneda de México
                    "quantity": 1,
                    "unit_price": 50.0
                }
            ],
            "payer": {
                "name": "Cliente de Prueba",
                "surname": "",
                "email": "test@caffeymiga.com"
            },
            "back_urls": {
                "success": "http://localhost:3000/success.html",
                "failure": "http://localhost:3000/failure.html",
                "pending": "http://localhost:3000/pending.html"
            },
            "external_reference": f"test_{int(datetime.now().timestamp())}"
        }
        
        # Intentar crear preferencia
        response = sdk.preference().create(test_preference)
        
        return jsonify({
            "status": "success",
            "sdk_status": "connected",
            "test_mode": USE_TEST_MODE,
            "response_status": response.get("status"),
            "preference_created": response.get("status") == 201,
            "preference_id": response.get("response", {}).get("id") if response.get("status") == 201 else None,
            "error": response if response.get("status") != 201 else None
        })
        
    except Exception as e:
        logger.error(f"❌ Error en test Mercado Pago: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "sdk_initialized": bool(sdk),
            "access_token_configured": bool(ACCESS_TOKEN)
        }), 500

@app.route('/api/orders/save', methods=['POST'])
def save_order_for_sync():
    """Guardar pedido para sincronización automática"""
    try:
        data = request.get_json()
        logger.info(f"📝 Guardando pedido para sincronización: {data.get('customer', {}).get('name', 'Sin nombre')}")
        
        # Crear estructura del pedido para sincronización
        order_for_sync = {
            'id': data.get('external_reference', f"sync_{int(datetime.now().timestamp())}"),
            'cliente_nombre': data.get('customer', {}).get('name', ''),
            'cliente_telefono': data.get('customer', {}).get('phone', ''),
            'hora_recogida': data.get('metadata', {}).get('pickup_time', ''),
            'productos': [],
            'total': data.get('total', 0),
            'metodo_pago': data.get('customer', {}).get('payment_method', 'mercado_pago'),
            'fecha': datetime.now().isoformat(),
            'estado': 'pendiente',
            'source': 'web_mobile'
        }
        
        # Formatear productos
        for item in data.get('items', []):
            order_for_sync['productos'].append({
                'nombre': item.get('title', 'Producto'),
                'precio': item.get('unit_price', 0),
                'cantidad': item.get('quantity', 1),
                'descripcion': item.get('description', '')
            })
        
        # Guardar en Firebase con estructura para sincronización
        firebase_order_id = firebase_manager.save_order(order_for_sync)
        
        # También guardar en variable global para endpoint
        if not hasattr(app, 'pending_orders'):
            app.pending_orders = []
        
        app.pending_orders.append(order_for_sync)
        
        # Mantener solo los últimos 50 pedidos en memoria
        if len(app.pending_orders) > 50:
            app.pending_orders = app.pending_orders[-50:]
        
        logger.info(f"✅ Pedido guardado para sincronización: {order_for_sync['id']}")
        
        return jsonify({
            "status": "success",
            "order_id": order_for_sync['id'],
            "firebase_id": firebase_order_id,
            "message": "Pedido guardado para sincronización"
        })
        
    except Exception as e:
        logger.error(f"❌ Error guardando pedido para sync: {e}")
        return jsonify({"error": str(e)}), 500

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
