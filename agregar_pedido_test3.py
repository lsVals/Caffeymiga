#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para agregar el pedido de Test3 al sistema POS
"""
import sqlite3
import json
from datetime import datetime

def agregar_pedido_test3():
    try:
        # Conectar a la base de datos del POS
        conn = sqlite3.connect('pos_pedidos.db')
        cursor = conn.cursor()
        
        # Datos del pedido de Test3
        order_data = {
            'id': f'test3_{int(datetime.now().timestamp())}',
            'cliente_nombre': 'Test3',
            'cliente_telefono': '5842652580',
            'hora_recogida': '5:30 PM',
            'items': json.dumps([{"name": "Producto Test3", "price": 100, "quantity": 1}]),
            'total': 100.0,
            'estado': 'pendiente',
            'metodo_pago': 'efectivo',
            'fecha_creacion': datetime.now().isoformat(),
            'fecha_actualizacion': datetime.now().isoformat()
        }
        
        # Insertar el pedido
        cursor.execute('''
            INSERT INTO pedidos (id, cliente_nombre, cliente_telefono, hora_recogida, 
                               items, total, estado, metodo_pago, fecha_creacion, fecha_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_data['id'],
            order_data['cliente_nombre'],
            order_data['cliente_telefono'],
            order_data['hora_recogida'],
            order_data['items'],
            order_data['total'],
            order_data['estado'],
            order_data['metodo_pago'],
            order_data['fecha_creacion'],
            order_data['fecha_actualizacion']
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Pedido de Test3 agregado exitosamente: {order_data['id']}")
        print(f"👤 Cliente: {order_data['cliente_nombre']}")
        print(f"📱 Teléfono: {order_data['cliente_telefono']}")
        print(f"🕐 Hora recogida: {order_data['hora_recogida']}")
        print(f"💰 Total: ${order_data['total']}")
        print(f"💳 Método pago: {order_data['metodo_pago']}")
        
        # Verificar total de pedidos pendientes
        conn = sqlite3.connect('pos_pedidos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE estado='pendiente'")
        total_pendientes = cursor.fetchone()[0]
        conn.close()
        
        print(f"📊 Total de pedidos pendientes: {total_pendientes}")
        
    except Exception as e:
        print(f"❌ Error agregando pedido: {e}")

if __name__ == "__main__":
    agregar_pedido_test3()
