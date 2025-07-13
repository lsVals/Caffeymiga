#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT PARA VERIFICAR Y CREAR PEDIDO DE PRUEBA
"""

import sqlite3
import json
from datetime import datetime

def verificar_base_datos():
    """Verificar estado de la base de datos"""
    try:
        conn = sqlite3.connect('caffeymiga_pedidos.db')  # NUEVO NOMBRE ÚNICO
        cursor = conn.cursor()
        
        # Contar pedidos totales
        cursor.execute('SELECT COUNT(*) FROM pedidos')
        total = cursor.fetchone()[0]
        
        # Contar pedidos pendientes
        cursor.execute('SELECT COUNT(*) FROM pedidos WHERE estado = "pendiente"')
        pendientes = cursor.fetchone()[0]
        
        print(f"📊 ESTADO BASE DE DATOS:")
        print(f"   Total pedidos: {total}")
        print(f"   Pedidos pendientes: {pendientes}")
        
        if pendientes > 0:
            cursor.execute('SELECT id, cliente_nombre, cliente_telefono, total FROM pedidos WHERE estado = "pendiente" LIMIT 5')
            pedidos = cursor.fetchall()
            print(f"\n🔍 PEDIDOS PENDIENTES:")
            for p in pedidos:
                print(f"   ID: {p[0]} | Cliente: '{p[1]}' | Tel: '{p[2]}' | Total: ${p[3]}")
        
        conn.close()
        return pendientes > 0
        
    except Exception as e:
        print(f"❌ Error verificando BD: {e}")
        return False

def crear_pedido_prueba():
    """Crear un pedido de prueba con datos reales"""
    try:
        conn = sqlite3.connect('caffeymiga_pedidos.db')  # NUEVO NOMBRE ÚNICO
        cursor = conn.cursor()
        
        # Crear pedido de prueba
        pedido_id = f"prueba_{int(datetime.now().timestamp())}"
        items = [
            {
                "name": "Cappuccino Grande - Leche Entera",
                "price": 45,
                "quantity": 1,
                "description": "Prueba del sistema"
            }
        ]
        
        cursor.execute('''
            INSERT INTO pedidos 
            (id, cliente_nombre, cliente_telefono, hora_recogida, 
             metodo_pago, items, total, estado, fecha_creacion, fecha_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pedido_id,
            "VICTOR PRUEBA",
            "55-1234-5678",
            "14:30",
            "Efectivo en sucursal",
            json.dumps(items, ensure_ascii=False),
            45.0,
            'pendiente',
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ PEDIDO DE PRUEBA CREADO:")
        print(f"   ID: {pedido_id}")
        print(f"   Cliente: VICTOR PRUEBA")
        print(f"   Teléfono: 55-1234-5678")
        print(f"   Total: $45")
        print(f"   ¡REVISAR EL SISTEMA POS AHORA!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando pedido prueba: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🔍 VERIFICADOR DE BASE DE DATOS Y PEDIDOS")
    print("=" * 50)
    
    # Verificar estado actual
    hay_pedidos = verificar_base_datos()
    
    if not hay_pedidos:
        print(f"\n⚠️ No hay pedidos pendientes")
        print(f"🔨 Creando pedido de prueba...")
        crear_pedido_prueba()
    else:
        print(f"\n✅ HAY PEDIDOS PENDIENTES")
        print(f"❓ Si no aparecen en el POS, hay problema de conexión")
    
    print(f"\n🔄 Ahora revisa tu sistema POS para ver si aparecen los pedidos")
