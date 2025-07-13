#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para agregar manualmente el pedido de Vals al sistema POS
"""
import sqlite3
import json
from datetime import datetime

def agregar_pedido_vals():
    try:
        # Conectar a la base de datos del POS
        conn = sqlite3.connect('cafeteria_sistema/pos_pedidos.db')
        cursor = conn.cursor()
        
        # Datos del pedido de Vals
        order_data = {
            'id': f'vals_{int(datetime.now().timestamp())}',
            'cliente_nombre': 'Vals',
            'cliente_telefono': '846464644',
            'hora_recogida': '2:00 PM',
            'items': json.dumps([{"name": "Producto Mobile", "price": 24, "quantity": 1}]),
            'total': 24.0,
            'estado': 'pendiente',
            'metodo_pago': 'mercado_pago',
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
        
        print(f"✅ Pedido de Vals agregado exitosamente: {order_data['id']}")
        print(f"📱 Cliente: {order_data['cliente_nombre']}")
        print(f"☎️ Teléfono: {order_data['cliente_telefono']}")
        print(f"🕐 Hora recogida: {order_data['hora_recogida']}")
        print(f"💰 Total: ${order_data['total']}")
        print(f"💳 Método pago: {order_data['metodo_pago']}")
        
    except Exception as e:
        print(f"❌ Error agregando pedido: {e}")

if __name__ == "__main__":
    agregar_pedido_vals()
