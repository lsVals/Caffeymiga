# Cliente POS para Caffe & Miga - Integración SQLite
# Sistema de gestión de pedidos con base de datos SQLite

import requests
import sqlite3
import json
import time
from datetime import datetime, timezone
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CaffeYMigaSQLiteClient:
    def __init__(self, server_url="http://127.0.0.1:3000", db_path="pos_pedidos.db"):
        """
        Cliente POS para integrar con SQLite
        
        Args:
            server_url: URL del servidor de Caffe & Miga
            db_path: Ruta de la base de datos SQLite
        """
        self.server_url = server_url.rstrip('/')
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializar base de datos SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Crear tabla de pedidos si no existe
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pedidos (
                    id TEXT PRIMARY KEY,
                    firebase_id TEXT UNIQUE,
                    cliente_nombre TEXT NOT NULL,
                    cliente_email TEXT,
                    cliente_telefono TEXT,
                    metodo_pago TEXT,
                    total REAL NOT NULL,
                    moneda TEXT DEFAULT 'MXN',
                    items_json TEXT NOT NULL,
                    estado_pago TEXT DEFAULT 'pendiente',
                    estado_pos TEXT DEFAULT 'nuevo',
                    notas TEXT,
                    fecha_creacion TEXT NOT NULL,
                    fecha_actualizacion TEXT,
                    sincronizado INTEGER DEFAULT 0
                )
            ''')
            
            # Crear tabla de items (opcional, para mejor organización)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pedido_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pedido_id TEXT NOT NULL,
                    item_id TEXT,
                    nombre TEXT NOT NULL,
                    cantidad INTEGER NOT NULL,
                    precio_unitario REAL NOT NULL,
                    precio_total REAL NOT NULL,
                    FOREIGN KEY (pedido_id) REFERENCES pedidos (id)
                )
            ''')
            
            # Crear tabla de historial de estados
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS estado_historial (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pedido_id TEXT NOT NULL,
                    estado_anterior TEXT,
                    estado_nuevo TEXT NOT NULL,
                    fecha_cambio TEXT NOT NULL,
                    usuario TEXT,
                    FOREIGN KEY (pedido_id) REFERENCES pedidos (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Base de datos SQLite inicializada correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")
    
    def obtener_pedidos_nuevos(self):
        """Obtener pedidos nuevos desde Firebase y guardarlos en SQLite"""
        try:
            # Obtener desde el servidor
            response = requests.get(f"{self.server_url}/pos/orders", timeout=10)
            
            if response.status_code != 200:
                logger.error(f"❌ Error obteniendo pedidos: {response.status_code}")
                return []
            
            data = response.json()
            pedidos_firebase = data.get('orders', [])
            
            if not pedidos_firebase:
                logger.info("📭 No hay pedidos nuevos")
                return []
            
            # Guardar en SQLite
            pedidos_guardados = []
            conn = sqlite3.connect(self.db_path)
            
            for pedido in pedidos_firebase:
                try:
                    # Verificar si ya existe
                    cursor = conn.cursor()
                    cursor.execute('SELECT id FROM pedidos WHERE firebase_id = ?', (pedido['id'],))
                    
                    if cursor.fetchone():
                        logger.info(f"⚠️ Pedido {pedido['id'][:8]}... ya existe en la BD")
                        continue
                    
                    # Insertar nuevo pedido
                    customer = pedido.get('customer', {})
                    items = pedido.get('items', [])
                    
                    cursor.execute('''
                        INSERT INTO pedidos (
                            id, firebase_id, cliente_nombre, cliente_email, cliente_telefono,
                            metodo_pago, total, moneda, items_json, estado_pago, estado_pos,
                            notas, fecha_creacion, sincronizado
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        f"POS_{int(time.time())}_{pedido['id'][:8]}",  # ID local
                        pedido['id'],  # ID de Firebase
                        customer.get('name', 'Cliente'),
                        customer.get('email', ''),
                        customer.get('phone', ''),
                        customer.get('payment_method', 'tarjeta'),
                        pedido.get('total', 0),
                        pedido.get('currency', 'MXN'),
                        json.dumps(items),
                        pedido.get('payment_status', 'approved'),
                        'nuevo',
                        pedido.get('notes', ''),
                        datetime.now(timezone.utc).isoformat(),
                        1
                    ))
                    
                    pedido_local_id = cursor.lastrowid
                    
                    # Insertar items individuales
                    for item in items:
                        cursor.execute('''
                            INSERT INTO pedido_items (
                                pedido_id, item_id, nombre, cantidad, precio_unitario, precio_total
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            f"POS_{int(time.time())}_{pedido['id'][:8]}",
                            item.get('id', ''),
                            item.get('title', 'Item'),
                            item.get('quantity', 1),
                            item.get('unit_price', 0),
                            item.get('quantity', 1) * item.get('unit_price', 0)
                        ))
                    
                    # Registrar en historial
                    cursor.execute('''
                        INSERT INTO estado_historial (pedido_id, estado_nuevo, fecha_cambio, usuario)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        f"POS_{int(time.time())}_{pedido['id'][:8]}",
                        'nuevo',
                        datetime.now(timezone.utc).isoformat(),
                        'sistema'
                    ))
                    
                    pedidos_guardados.append(pedido)
                    logger.info(f"✅ Pedido guardado: {customer.get('name', 'Cliente')} - ${pedido.get('total', 0)}")
                    
                except Exception as e:
                    logger.error(f"❌ Error guardando pedido individual: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            logger.info(f"🔥 {len(pedidos_guardados)} nuevos pedidos guardados en SQLite")
            return pedidos_guardados
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo pedidos nuevos: {e}")
            return []
    
    def actualizar_estado_pedido(self, pedido_id, nuevo_estado, usuario="pos_user"):
        """Actualizar estado de un pedido en SQLite y Firebase"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener estado actual y firebase_id
            cursor.execute('''
                SELECT estado_pos, firebase_id FROM pedidos WHERE id = ?
            ''', (pedido_id,))
            
            resultado = cursor.fetchone()
            if not resultado:
                logger.error(f"❌ Pedido {pedido_id} no encontrado")
                return False
            
            estado_anterior, firebase_id = resultado
            
            # Actualizar en SQLite
            cursor.execute('''
                UPDATE pedidos 
                SET estado_pos = ?, fecha_actualizacion = ?
                WHERE id = ?
            ''', (nuevo_estado, datetime.now(timezone.utc).isoformat(), pedido_id))
            
            # Registrar en historial
            cursor.execute('''
                INSERT INTO estado_historial (pedido_id, estado_anterior, estado_nuevo, fecha_cambio, usuario)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                pedido_id,
                estado_anterior,
                nuevo_estado,
                datetime.now(timezone.utc).isoformat(),
                usuario
            ))
            
            conn.commit()
            conn.close()
            
            # Actualizar en Firebase
            try:
                response = requests.put(
                    f"{self.server_url}/pos/orders/{firebase_id}/status",
                    json={"status": nuevo_estado},
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Estado actualizado: {pedido_id} -> {nuevo_estado}")
                    return True
                else:
                    logger.warning(f"⚠️ Actualizado en SQLite pero no en Firebase: {response.status_code}")
                    return True
                    
            except Exception as e:
                logger.warning(f"⚠️ Actualizado en SQLite pero error en Firebase: {e}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error actualizando estado: {e}")
            return False
    
    def obtener_pedidos_activos(self):
        """Obtener pedidos activos de SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, firebase_id, cliente_nombre, cliente_telefono, total, 
                       items_json, estado_pos, fecha_creacion
                FROM pedidos 
                WHERE estado_pos IN ('nuevo', 'preparando', 'listo')
                ORDER BY fecha_creacion ASC
            ''')
            
            pedidos = []
            for row in cursor.fetchall():
                pedido = {
                    'id': row[0],
                    'firebase_id': row[1],
                    'cliente': row[2],
                    'telefono': row[3],
                    'total': row[4],
                    'items': json.loads(row[5]),
                    'estado': row[6],
                    'fecha': row[7]
                }
                pedidos.append(pedido)
            
            conn.close()
            return pedidos
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo pedidos activos: {e}")
            return []
    
    def obtener_estadisticas(self):
        """Obtener estadísticas del POS"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Contar por estados
            cursor.execute('''
                SELECT estado_pos, COUNT(*) 
                FROM pedidos 
                WHERE date(fecha_creacion) = date('now')
                GROUP BY estado_pos
            ''')
            
            stats = {}
            for estado, count in cursor.fetchall():
                stats[estado] = count
            
            # Total del día
            cursor.execute('''
                SELECT COUNT(*), COALESCE(SUM(total), 0)
                FROM pedidos 
                WHERE date(fecha_creacion) = date('now')
            ''')
            
            total_pedidos, total_ventas = cursor.fetchone()
            stats['total_pedidos'] = total_pedidos
            stats['total_ventas'] = total_ventas
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}
    
    def iniciar_monitoreo(self, intervalo=30):
        """Iniciar monitoreo automático"""
        logger.info(f"🔄 Iniciando monitoreo cada {intervalo} segundos...")
        
        while True:
            try:
                # Obtener nuevos pedidos
                nuevos = self.obtener_pedidos_nuevos()
                
                if nuevos:
                    print(f"\n🔥 {len(nuevos)} NUEVOS PEDIDOS!")
                    for pedido in nuevos:
                        customer = pedido.get('customer', {})
                        print(f"📋 {customer.get('name', 'Cliente')} - ${pedido.get('total', 0)}")
                    print("=" * 50)
                
                # Mostrar resumen cada 5 minutos
                if int(time.time()) % 300 == 0:
                    stats = self.obtener_estadisticas()
                    print(f"\n📊 Resumen del día:")
                    print(f"   Total pedidos: {stats.get('total_pedidos', 0)}")
                    print(f"   Total ventas: ${stats.get('total_ventas', 0):.2f}")
                    print(f"   Nuevos: {stats.get('nuevo', 0)}")
                    print(f"   Preparando: {stats.get('preparando', 0)}")
                    print(f"   Listos: {stats.get('listo', 0)}")
                
                time.sleep(intervalo)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoreo detenido por el usuario")
                break
            except Exception as e:
                logger.error(f"❌ Error en monitoreo: {e}")
                time.sleep(intervalo)

# Funciones de utilidad para tu POS
def mostrar_pedidos_activos():
    """Mostrar pedidos activos en consola"""
    client = CaffeYMigaSQLiteClient()
    pedidos = client.obtener_pedidos_activos()
    
    if not pedidos:
        print("📭 No hay pedidos activos")
        return
    
    print(f"\n🔥 {len(pedidos)} PEDIDOS ACTIVOS")
    print("=" * 60)
    
    for pedido in pedidos:
        print(f"ID: {pedido['id']}")
        print(f"Cliente: {pedido['cliente']}")
        print(f"Teléfono: {pedido['telefono']}")
        print(f"Total: ${pedido['total']:.2f}")
        print(f"Estado: {pedido['estado'].upper()}")
        print(f"Items:")
        for item in pedido['items']:
            print(f"  • {item.get('quantity', 1)}x {item.get('title', 'Item')} - ${item.get('unit_price', 0)}")
        print("-" * 60)

def cambiar_estado_pedido():
    """Función interactiva para cambiar estado"""
    client = CaffeYMigaSQLiteClient()
    pedidos = client.obtener_pedidos_activos()
    
    if not pedidos:
        print("📭 No hay pedidos activos")
        return
    
    print("\n🔥 PEDIDOS DISPONIBLES:")
    for i, pedido in enumerate(pedidos, 1):
        print(f"{i}. {pedido['cliente']} - {pedido['estado']} - ${pedido['total']:.2f}")
    
    try:
        opcion = int(input("\nSelecciona pedido (número): ")) - 1
        if 0 <= opcion < len(pedidos):
            pedido = pedidos[opcion]
            
            print(f"\nEstados disponibles:")
            estados = ['preparando', 'listo', 'entregado', 'cancelado']
            for i, estado in enumerate(estados, 1):
                print(f"{i}. {estado.upper()}")
            
            estado_opcion = int(input("Selecciona nuevo estado: ")) - 1
            if 0 <= estado_opcion < len(estados):
                nuevo_estado = estados[estado_opcion]
                
                if client.actualizar_estado_pedido(pedido['id'], nuevo_estado):
                    print(f"✅ Pedido actualizado a: {nuevo_estado.upper()}")
                else:
                    print("❌ Error actualizando pedido")
            else:
                print("❌ Opción inválida")
        else:
            print("❌ Opción inválida")
    except ValueError:
        print("❌ Ingresa un número válido")

if __name__ == "__main__":
    print("🔥 Cliente POS SQLite - Caffe & Miga")
    print("=" * 40)
    
    # Crear cliente
    client = CaffeYMigaSQLiteClient()
    
    print("\nOpciones:")
    print("1. Obtener pedidos nuevos")
    print("2. Mostrar pedidos activos")
    print("3. Cambiar estado de pedido")
    print("4. Ver estadísticas")
    print("5. Iniciar monitoreo automático")
    
    opcion = input("\nSelecciona una opción (1-5): ")
    
    if opcion == "1":
        pedidos = client.obtener_pedidos_nuevos()
        print(f"✅ {len(pedidos)} pedidos nuevos obtenidos")
        
    elif opcion == "2":
        mostrar_pedidos_activos()
        
    elif opcion == "3":
        cambiar_estado_pedido()
        
    elif opcion == "4":
        stats = client.obtener_estadisticas()
        print(f"\n📊 Estadísticas del día:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
            
    elif opcion == "5":
        client.iniciar_monitoreo(30)
        
    else:
        print("❌ Opción inválida")
