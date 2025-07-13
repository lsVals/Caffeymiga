#!/usr/bin/env python3
# VISOR DE PEDIDOS SIMPLE - CAFFE & MIGA

import sqlite3
import json
import os
from datetime import datetime

def mostrar_pedidos():
    """Mostrar pedidos de forma simple y clara"""
    
    db_path = "pos_pedidos.db"
    
    if not os.path.exists(db_path):
        print("❌ No se encontró la base de datos")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Obtener pedidos de hoy
        c.execute('''
            SELECT id, cliente_nombre, cliente_telefono, hora_recogida, 
                   items, total, metodo_pago, fecha_creacion, estado
            FROM pedidos 
            WHERE date(fecha_creacion) = date('now')
            ORDER BY fecha_creacion DESC
        ''')
        
        pedidos = c.fetchall()
        
        print("\n" + "="*60)
        print("🍕 CAFFE & MIGA - PEDIDOS DE HOY")
        print("="*60)
        print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"📊 {len(pedidos)} pedidos recibidos hoy")
        print("="*60)
        
        if not pedidos:
            print("\n📋 No hay pedidos de hoy")
            return
        
        for i, pedido in enumerate(pedidos, 1):
            (order_id, cliente_nombre, cliente_telefono, hora_recogida, 
             items_json, total, metodo_pago, fecha_creacion, estado) = pedido
            
            print(f"\n🎯 PEDIDO #{i}")
            print(f"🆔 {order_id}")
            print(f"👤 Cliente: {cliente_nombre if cliente_nombre else '❌ Sin nombre'}")
            print(f"📱 Teléfono: {cliente_telefono if cliente_telefono else '❌ Sin teléfono'}")
            print(f"🕐 Hora recogida: {hora_recogida if hora_recogida else '❌ Sin hora'}")
            print(f"💰 Total: ${total}")
            print(f"💳 Pago: {metodo_pago}")
            print(f"📅 Recibido: {fecha_creacion}")
            print(f"📦 Estado: {estado}")
            
            # Mostrar productos
            if items_json:
                try:
                    items = json.loads(items_json)
                    print(f"🛒 PRODUCTOS ({len(items)} items):")
                    for j, item in enumerate(items, 1):
                        nombre = item.get('name', 'Producto')
                        precio = item.get('price', 0)
                        cantidad = item.get('quantity', 1)
                        print(f"   {j}. {nombre}")
                        print(f"      ${precio} x {cantidad} = ${precio * cantidad}")
                except Exception as e:
                    print(f"🛒 PRODUCTOS: Error al cargar ({e})")
            else:
                print("🛒 PRODUCTOS: ❌ Sin productos")
            
            print("-" * 50)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    mostrar_pedidos()
    print("\n💡 Para actualizar, ejecuta este archivo otra vez")
    print("🔄 Los pedidos llegan automáticamente cada 30 segundos")
