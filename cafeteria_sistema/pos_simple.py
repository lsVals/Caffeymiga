#!/usr/bin/env python3
# Visualizador simple de pedidos para el POS

import sqlite3
import json
from datetime import datetime
import os

def mostrar_pedidos():
    """Mostrar todos los pedidos pendientes de manera clara"""
    
    # Cambiar al directorio padre para acceder a la base de datos
    db_path = "../pos_pedidos.db"
    
    if not os.path.exists(db_path):
        print("❌ No se encontró la base de datos de pedidos")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Obtener pedidos pendientes ordenados por fecha
        c.execute('''
            SELECT id, cliente_nombre, cliente_telefono, hora_recogida, 
                   items, total, metodo_pago, fecha_creacion, estado
            FROM pedidos 
            WHERE estado = 'pendiente'
            ORDER BY fecha_creacion DESC
        ''')
        
        pedidos = c.fetchall()
        
        if not pedidos:
            print("\n📋 No hay pedidos pendientes")
            return
        
        print(f"\n🍕 SISTEMA POS - CAFFE & MIGA")
        print("=" * 50)
        print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"📊 {len(pedidos)} pedidos pendientes")
        print("=" * 50)
        
        for i, pedido in enumerate(pedidos, 1):
            (order_id, cliente_nombre, cliente_telefono, hora_recogida, 
             items_json, total, metodo_pago, fecha_creacion, estado) = pedido
            
            print(f"\n🎯 PEDIDO #{i}")
            print(f"🆔 ID: {order_id}")
            print(f"👤 Cliente: {cliente_nombre if cliente_nombre else '❌ Sin nombre'}")
            print(f"📱 Teléfono: {cliente_telefono if cliente_telefono else '❌ Sin teléfono'}")
            print(f"🕐 Hora de recogida: {hora_recogida if hora_recogida else '❌ Sin hora'}")
            print(f"💰 Total: ${total}")
            print(f"💳 Método de pago: {metodo_pago}")
            print(f"📅 Fecha del pedido: {fecha_creacion}")
            
            # Mostrar productos
            try:
                if items_json:
                    items = json.loads(items_json)
                    print(f"🛒 PRODUCTOS:")
                    for j, item in enumerate(items, 1):
                        nombre = item.get('name', 'Producto')
                        precio = item.get('price', 0)
                        cantidad = item.get('quantity', 1)
                        print(f"   {j}. {nombre} - ${precio} x{cantidad}")
                else:
                    print(f"🛒 PRODUCTOS: ❌ Sin productos")
            except Exception as e:
                print(f"🛒 PRODUCTOS: ❌ Error al cargar ({e})")
            
            print("-" * 30)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al acceder a la base de datos: {e}")

def main():
    """Función principal"""
    while True:
        try:
            print("\n" + "=" * 50)
            mostrar_pedidos()
            print("\n🔄 Presiona Enter para actualizar o Ctrl+C para salir")
            input()
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
