# Firebase Configuration para Caffe & Miga
# Sistema de gestión de pedidos en tiempo real

import firebase_admin
from firebase_admin import credentials, firestore
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FirebaseManager:
    def __init__(self):
        self.db = None
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Inicializar Firebase con credenciales"""
        try:
            # Si ya está inicializado, obtener la instancia
            if firebase_admin._apps:
                app = firebase_admin.get_app()
                self.db = firestore.client(app)
                logger.info("✅ Firebase ya inicializado - usando instancia existente")
                return
            
            # Verificar si existe el archivo de credenciales o usar variables de entorno
            import os
            
            if os.getenv('ENVIRONMENT') == 'production':
                # En producción, usar variables de entorno
                firebase_key = os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n')
                
                cred_dict = {
                    "type": "service_account",
                    "project_id": "caffeymigapedidos",
                    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID', '171d1d626b0e55518e44a2ea4c912d587e03ba31'),
                    "private_key": firebase_key,
                    "client_email": "firebase-adminsdk-fbsvc@caffeymigapedidos.iam.gserviceaccount.com",
                    "client_id": "100510796799572602499",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40caffeymigapedidos.iam.gserviceaccount.com",
                    "universe_domain": "googleapis.com"
                }
                cred = credentials.Certificate(cred_dict)
            else:
                # En desarrollo local, usar archivo JSON
                try:
                    cred = credentials.Certificate("firebase-credentials.json")
                    logger.info("📁 Usando credenciales de Firebase desde archivo local")
                except FileNotFoundError:
                    logger.warning("⚠️ Archivo firebase-credentials.json no encontrado")
                    cred = credentials.ApplicationDefault()
                    logger.info("🔄 Usando credenciales por defecto de Firebase")
            
            try:
                firebase_admin.initialize_app(cred)
                logger.info("✅ Firebase inicializado con credenciales")
            except Exception as init_error:
                logger.error(f"❌ Error inicializando Firebase: {init_error}")
                # Intentar con credenciales por defecto como fallback
                try:
                    cred = credentials.ApplicationDefault()
                    firebase_admin.initialize_app(cred, {
                        'projectId': 'caffeymigapedidos'
                    })
                    logger.info("✅ Firebase inicializado con credenciales por defecto")
                except Exception as fallback_error:
                    logger.error(f"❌ Error con credenciales por defecto: {fallback_error}")
                    self.db = None
                    return
            
            self.db = firestore.client()
            
        except Exception as e:
            logger.error(f"❌ Error inicializando Firebase: {e}")
            self.db = None
    
    def save_order(self, order_data):
        """Guardar pedido en Firestore"""
        try:
            if not self.db:
                raise Exception("Firebase no inicializado")
            
            # Agregar timestamp
            order_data['created_at'] = datetime.now()
            order_data['status'] = 'nuevo'
            order_data['pos_status'] = 'pendiente'
            
            # Guardar en colección 'orders'
            doc_ref = self.db.collection('orders').add(order_data)
            order_id = doc_ref[1].id
            
            logger.info(f"✅ Pedido guardado en Firebase: {order_id}")
            return order_id
            
        except Exception as e:
            logger.error(f"❌ Error guardando pedido: {e}")
            return None
    
    def update_payment_status(self, order_id, payment_data):
        """Actualizar estado del pago"""
        try:
            if not self.db:
                return False
            
            update_data = {
                'payment_status': payment_data.get('status'),
                'payment_id': payment_data.get('payment_id'),
                'payment_updated_at': datetime.now()
            }
            
            # Si el pago fue aprobado
            if payment_data.get('status') == 'approved':
                update_data['status'] = 'pagado'
                update_data['pos_status'] = 'listo_para_preparar'
            
            self.db.collection('orders').document(order_id).update(update_data)
            logger.info(f"✅ Estado de pago actualizado: {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error actualizando pago: {e}")
            return False
    
    def get_pending_orders(self):
        """Obtener pedidos pendientes para el POS"""
        try:
            if not self.db:
                return []
            
            orders = self.db.collection('orders')\
                           .where('pos_status', '==', 'listo_para_preparar')\
                           .order_by('created_at')\
                           .stream()
            
            order_list = []
            for order in orders:
                order_data = order.to_dict()
                order_data['id'] = order.id
                order_list.append(order_data)
            
            return order_list
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo pedidos: {e}")
            return []
    
    def update_order_status(self, order_id, new_status):
        """Actualizar estado del pedido desde el POS"""
        try:
            if not self.db:
                return False
            
            update_data = {
                'pos_status': new_status,
                'status_updated_at': datetime.now()
            }
            
            self.db.collection('orders').document(order_id).update(update_data)
            logger.info(f"✅ Estado actualizado: {order_id} -> {new_status}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error actualizando estado: {e}")
            return False
        
    def get_all_orders(self):
        """Obtener todos los pedidos de Firebase"""
        try:
            if not self.db:
                logger.warning("⚠️ Firebase no inicializado")
                return []
            
            orders = self.db.collection('orders')\
                           .order_by('created_at', direction=firestore.Query.DESCENDING)\
                           .limit(50)\
                           .stream()
            
            order_list = []
            for order in orders:
                order_data = order.to_dict()
                order_data['id'] = order.id
                order_list.append(order_data)
            
            logger.info(f"✅ Obtenidos {len(order_list)} pedidos de Firebase")
            return order_list
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo todos los pedidos: {e}")
            return []

# Instancia global
firebase_manager = FirebaseManager()
