#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_pos_database():
    """Verificar los pedidos en la base de datos del POS"""
    db_path = os.path.join('pos_integration', 'pos_pedidos.db')
    
    if not os.path.exists(db_path):
        print("❌ Base de datos del POS no encontrada")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si hay pedidos
        cursor.execute('SELECT COUNT(*) FROM pedidos')
        total_pedidos = cursor.fetchone()[0]
        print(f"📊 Total de pedidos en POS: {total_pedidos}")
        
        # Mostrar últimos 5 pedidos
        cursor.execute('SELECT * FROM pedidos ORDER BY id DESC LIMIT 5')
        pedidos = cursor.fetchall()
        
        print("\n=== ÚLTIMOS PEDIDOS EN POS ===")
        for pedido in pedidos:
            print(f"🆔 ID: {pedido[0]}")
            print(f"👤 Cliente: {pedido[1]}")
            print(f"💰 Total: ${pedido[2]}")
            print(f"📋 Estado: {pedido[3]}")
            print(f"📅 Fecha: {pedido[4]}")
            print("-" * 40)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al verificar base de datos: {e}")

if __name__ == "__main__":
    check_pos_database()
