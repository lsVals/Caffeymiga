#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincronizador automático de pedidos desde servidor de producción
"""
import time
import requests
import sqlite3
import json
from datetime import datetime

def sync_orders_from_production():
    """Sincronizar pedidos desde el servidor de producción"""
    try:
        print("🔄 Sincronizando pedidos desde el servidor...")
        
        # URL del servidor de producción
        server_url = "https://caffeymiga-1.onrender.com"
        
        # Obtener pedidos del servidor
        response = requests.get(f"{server_url}/pos/orders", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get('orders', [])
            
            if not orders:
                print("📭 No hay pedidos nuevos en el servidor")
                return
            
            print(f"📥 Encontrados {len(orders)} pedidos en el servidor")
            
            # Conectar a la base de datos local
            conn = sqlite3.connect('pos_pedidos.db')
            cursor = conn.cursor()
            
            nuevos_pedidos = 0
            
            for order in orders:
                try:
                    order_id = order.get('id', f"sync_{int(datetime.now().timestamp())}")
                    
                    # Verificar si ya existe
                    cursor.execute("SELECT id FROM pedidos WHERE id = ?", (order_id,))
                    if cursor.fetchone():
                        continue  # Ya existe
                    
                    # Formatear productos
                    items = []
                    for producto in order.get('productos', []):
                        items.append({
                            "name": producto.get('nombre', 'Producto Web'),
                            "price": producto.get('precio', 0),
                            "quantity": producto.get('cantidad', 1)
                        })
                    
                    # Insertar nuevo pedido
                    cursor.execute('''
                        INSERT INTO pedidos (id, cliente_nombre, cliente_telefono, hora_recogida, 
                                           items, total, estado, metodo_pago, fecha_creacion, fecha_actualizacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        order_id,
                        order.get('cliente_nombre', ''),
                        order.get('cliente_telefono', ''),
                        order.get('hora_recogida', ''),
                        json.dumps(items, ensure_ascii=False),
                        order.get('total', 0),
                        'pendiente',
                        order.get('metodo_pago', 'mercado_pago'),
                        order.get('fecha', datetime.now().isoformat()),
                        datetime.now().isoformat()
                    ))
                    
                    nuevos_pedidos += 1
                    print(f"✅ Nuevo pedido sincronizado: {order.get('cliente_nombre', 'Sin nombre')} - ${order.get('total', 0)}")
                    
                except Exception as e:
                    print(f"❌ Error procesando pedido: {e}")
            
            conn.commit()
            conn.close()
            
            if nuevos_pedidos > 0:
                print(f"🎉 {nuevos_pedidos} pedidos nuevos agregados al sistema")
            else:
                print("📌 Todos los pedidos ya estaban sincronizados")
        
        else:
            print(f"⚠️ Error del servidor: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"🌐 Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error en sincronización: {e}")

def main():
    """Ejecutar sincronización una vez"""
    print("🚀 Iniciando sincronización de pedidos...")
    print("📡 Conectando con servidor de producción...")
    
    sync_orders_from_production()
    
    print("✅ Sincronización completada")

if __name__ == "__main__":
    main()
