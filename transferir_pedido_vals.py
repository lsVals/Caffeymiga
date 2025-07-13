#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para transferir el pedido de Vals de pos_pedidos.db a ventas.db
"""
import sqlite3
import json
from datetime import datetime

def transferir_pedido_vals():
    try:
        # Conectar a pos_pedidos.db para obtener el pedido
        conn_pos = sqlite3.connect('cafeteria_sistema/pos_pedidos.db')
        cursor_pos = conn_pos.cursor()
        
        # Buscar el pedido de Vals
        cursor_pos.execute("SELECT * FROM pedidos WHERE cliente_nombre = 'Vals' ORDER BY fecha_creacion DESC LIMIT 1")
        pedido_vals = cursor_pos.fetchone()
        
        if not pedido_vals:
            print("❌ No se encontró el pedido de Vals en pos_pedidos.db")
            return
        
        print(f"✅ Encontrado pedido de Vals: {pedido_vals[0]}")
        
        # Conectar a ventas.db para insertar
        conn_ventas = sqlite3.connect('cafeteria_sistema/ventas.db')
        cursor_ventas = conn_ventas.cursor()
        
        # Generar nuevo ID para ventas.db
        cursor_ventas.execute("SELECT MAX(id) FROM pedidos")
        max_id = cursor_ventas.fetchone()[0]
        nuevo_id = (max_id or 0) + 1
        
        # Insertar en ventas.db
        cursor_ventas.execute('''
            INSERT INTO pedidos (id, id_web, cliente_nombre, cliente_telefono, hora_recogida, 
                               productos, total, estado, metodo_pago, fecha_creacion, fecha_actualizacion, origen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            nuevo_id,                    # id
            pedido_vals[0],             # id_web (usar el ID original como referencia)
            pedido_vals[1],             # cliente_nombre
            pedido_vals[2],             # cliente_telefono
            pedido_vals[3],             # hora_recogida
            pedido_vals[4],             # productos (items)
            pedido_vals[5],             # total
            pedido_vals[6],             # estado
            pedido_vals[7],             # metodo_pago
            pedido_vals[8],             # fecha_creacion
            pedido_vals[9],             # fecha_actualizacion
            'web'                       # origen
        ))
        
        conn_ventas.commit()
        conn_ventas.close()
        conn_pos.close()
        
        print(f"✅ Pedido transferido exitosamente a ventas.db con ID: {nuevo_id}")
        print(f"📱 Cliente: {pedido_vals[1]}")
        print(f"☎️ Teléfono: {pedido_vals[2]}")
        print(f"🕐 Hora recogida: {pedido_vals[3]}")
        print(f"💰 Total: ${pedido_vals[5]}")
        print(f"💳 Método pago: {pedido_vals[7]}")
        print("🔄 Ahora debería aparecer en 'Pedidos en Línea'")
        
    except Exception as e:
        print(f"❌ Error transfiriendo pedido: {e}")

if __name__ == "__main__":
    transferir_pedido_vals()
