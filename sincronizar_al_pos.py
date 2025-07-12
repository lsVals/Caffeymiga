#!/usr/bin/env python3
"""
Script para sincronizar pedidos web al sistema POS en cafeteria_sistema
"""

import sqlite3
import requests
import json
from datetime import datetime

def sincronizar_pedidos_pos():
    """Sincronizar pedidos del servidor web al sistema POS"""
    
    # Rutas de las bases de datos
    pos_web_db = "pos_pedidos.db"  # BD de pedidos web (aquí)
    pos_sistema_db = "cafeteria_sistema/pos_pedidos.db"  # BD del sistema POS
    
    print("🔄 Sincronizando pedidos al sistema POS...")
    
    try:
        # 1. Obtener pedidos del servidor web
        print("📡 Obteniendo pedidos del servidor...")
        response = requests.get("http://localhost:3000/pos/orders", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Error del servidor: {response.status_code}")
            return False
        
        data = response.json()
        orders = data.get('orders', [])
        
        if not orders:
            print("ℹ️ No hay pedidos en el servidor")
            return True
        
        print(f"📦 Encontrados {len(orders)} pedidos en el servidor")
        
        # 2. Crear/conectar a la base de datos del sistema POS
        conn = sqlite3.connect(pos_sistema_db)
        cursor = conn.cursor()
        
        # Crear tabla si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id TEXT PRIMARY KEY,
                cliente_nombre TEXT,
                cliente_telefono TEXT,
                hora_recogida TEXT,
                items TEXT,
                total REAL,
                estado TEXT DEFAULT 'pendiente',
                metodo_pago TEXT,
                fecha_creacion TEXT,
                fecha_actualizacion TEXT
            )
        ''')
        
        # 3. Sincronizar cada pedido
        nuevos = 0
        actualizados = 0
        
        for order in orders:
            try:
                # Extraer datos del pedido
                order_id = order.get('id', order.get('preference_id', ''))
                cliente_nombre = order.get('customer_name', order.get('payer', {}).get('name', 'Cliente Web'))
                cliente_telefono = order.get('customer_phone', order.get('payer', {}).get('phone', {}).get('number', ''))
                hora_recogida = order.get('pickup_time', order.get('metadata', {}).get('pickup_time', ''))
                total = float(order.get('total', 0))
                metodo_pago = order.get('payment_method', 'mercado_pago')
                items = json.dumps(order.get('items', []))
                fecha_creacion = order.get('created_at', datetime.now().isoformat())
                
                # Verificar si el pedido ya existe
                cursor.execute("SELECT COUNT(*) FROM pedidos WHERE id = ?", (order_id,))
                existe = cursor.fetchone()[0] > 0
                
                if existe:
                    # Actualizar pedido existente
                    cursor.execute('''
                        UPDATE pedidos SET
                            cliente_nombre = ?, cliente_telefono = ?, hora_recogida = ?,
                            items = ?, total = ?, metodo_pago = ?, fecha_actualizacion = ?
                        WHERE id = ?
                    ''', (cliente_nombre, cliente_telefono, hora_recogida, items, 
                          total, metodo_pago, datetime.now().isoformat(), order_id))
                    actualizados += 1
                else:
                    # Insertar nuevo pedido
                    cursor.execute('''
                        INSERT INTO pedidos 
                        (id, cliente_nombre, cliente_telefono, hora_recogida, items, 
                         total, estado, metodo_pago, fecha_creacion, fecha_actualizacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (order_id, cliente_nombre, cliente_telefono, hora_recogida, 
                          items, total, 'pendiente', metodo_pago, fecha_creacion, 
                          datetime.now().isoformat()))
                    nuevos += 1
                    print(f"✅ Nuevo pedido: {cliente_nombre} - ${total}")
                
            except Exception as e:
                print(f"❌ Error procesando pedido: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Sincronización completada:")
        print(f"   📦 Pedidos nuevos: {nuevos}")
        print(f"   🔄 Pedidos actualizados: {actualizados}")
        print(f"   📊 Total: {nuevos + actualizados}")
        
        return True
        
    except requests.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def verificar_pedidos_pos():
    """Verificar pedidos en el sistema POS"""
    try:
        conn = sqlite3.connect("cafeteria_sistema/pos_pedidos.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE estado = 'pendiente'")
        pendientes = cursor.fetchone()[0]
        
        print(f"\n📊 Estado del sistema POS:")
        print(f"   📦 Total de pedidos: {total}")
        print(f"   ⏳ Pedidos pendientes: {pendientes}")
        
        if pendientes > 0:
            cursor.execute("""
                SELECT cliente_nombre, total, metodo_pago, fecha_creacion 
                FROM pedidos WHERE estado = 'pendiente' 
                ORDER BY fecha_creacion DESC LIMIT 5
            """)
            ultimos = cursor.fetchall()
            
            print(f"   🌐 Últimos pedidos pendientes:")
            for nombre, total, metodo, fecha in ultimos:
                print(f"      - {nombre} | ${total} | {metodo} | {fecha[:19]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verificando pedidos: {e}")

if __name__ == "__main__":
    print("🏪 Sincronizador Sistema POS - Caffe & Miga")
    print("=" * 60)
    
    if sincronizar_pedidos_pos():
        verificar_pedidos_pos()
        print("\n💡 Los pedidos están listos en tu sistema POS")
        print("💡 Ejecuta este script cada vez que quieras sincronizar")
    else:
        print("\n❌ Error en la sincronización")
        print("💡 Verifica que el servidor web esté ejecutándose")
