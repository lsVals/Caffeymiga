#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para agregar pedidos manualmente al sistema
"""
import sqlite3
import json
from datetime import datetime

def agregar_pedido_manual():
    """Función para agregar pedidos manualmente"""
    print("📝 Agregar nuevo pedido al sistema")
    print("=" * 40)
    
    # Solicitar datos del pedido
    cliente = input("👤 Nombre del cliente: ")
    telefono = input("📱 Teléfono: ")
    hora = input("🕐 Hora de recogida: ")
    producto = input("🛍️ Nombre del producto: ")
    precio = float(input("💰 Precio: $"))
    cantidad = int(input("🔢 Cantidad: "))
    
    total = precio * cantidad
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('pos_pedidos.db')
        cursor = conn.cursor()
        
        # Generar ID único
        order_id = f"manual_{int(datetime.now().timestamp())}"
        
        # Preparar items
        items = [{
            "name": producto,
            "price": precio,
            "quantity": cantidad
        }]
        
        # Insertar pedido
        cursor.execute('''
            INSERT INTO pedidos (id, cliente_nombre, cliente_telefono, hora_recogida, 
                               items, total, estado, metodo_pago, fecha_creacion, fecha_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_id,
            cliente,
            telefono,
            hora,
            json.dumps(items, ensure_ascii=False),
            total,
            'pendiente',
            'mercado_pago',
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        print("\n✅ ¡Pedido agregado exitosamente!")
        print(f"🆔 ID: {order_id}")
        print(f"👤 Cliente: {cliente}")
        print(f"📱 Teléfono: {telefono}")
        print(f"🕐 Hora: {hora}")
        print(f"🛍️ Producto: {producto} x{cantidad}")
        print(f"💰 Total: ${total}")
        print("\n🔄 Actualiza 'Pedidos en Línea' en el sistema POS")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    agregar_pedido_manual()
