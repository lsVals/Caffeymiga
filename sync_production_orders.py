#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincronizador de pedidos desde producción
Obtiene pedidos desde el servidor de producción y los sincroniza con el POS local
"""

import requests
import json
import sqlite3
import os
from datetime import datetime

def sync_orders_from_production():
    """Sincronizar pedidos desde el servidor de producción"""
    try:
        print("🔄 Sincronizando pedidos desde producción...")
        
        # URL del servidor de producción
        production_url = "https://caffeymiga-1.onrender.com"
        
        # Endpoint para obtener pedidos nuevos
        response = requests.get(f"{production_url}/pos/orders/sync", timeout=30)
        
        if response.status_code == 200:
            orders = response.json()
            print(f"📦 Encontrados {len(orders)} pedidos nuevos")
            
            # Guardar cada pedido en SQLite local
            for order in orders:
                save_to_local_sqlite(order)
                print(f"✅ Pedido sincronizado: {order.get('customer', {}).get('name', 'Sin nombre')}")
            
            print(f"🎉 Sincronización completada: {len(orders)} pedidos")
            return True
            
        else:
            print(f"❌ Error al conectar con producción: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en sincronización: {e}")
        return False

def save_to_local_sqlite(order_data):
    """Guardar pedido en SQLite local"""
    try:
        db_path = "cafeteria_sistema/pos_pedidos.db"
        
        if not os.path.exists(db_path):
            print("❌ Base de datos local no encontrada")
            return False
            
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Verificar si el pedido ya existe
        c.execute("SELECT id FROM pedidos WHERE id = ?", (order_data['id'],))
        if c.fetchone():
            print(f"⚠️ Pedido {order_data['id']} ya existe, omitiendo...")
            conn.close()
            return True
        
        # Extraer datos
        customer = order_data.get('customer', {})
        items = order_data.get('items', [])
        metadata = order_data.get('metadata', {})
        
        # Insertar pedido
        c.execute("""
            INSERT INTO pedidos (id, cliente_nombre, cliente_telefono, hora_recogida, 
                               items, total, estado, metodo_pago, fecha_creacion, fecha_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_data['id'],
            customer.get('name', ''),
            customer.get('phone', ''),
            metadata.get('pickup_time', ''),
            json.dumps(items),
            order_data.get('total', 0),
            'pendiente',
            customer.get('payment_method', 'mercado_pago'),
            order_data.get('timestamp', datetime.now().isoformat()),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error guardando en SQLite: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SINCRONIZADOR DE PEDIDOS - CAFFÈ & MIGA")
    print("=" * 50)
    sync_orders_from_production()
