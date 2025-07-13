#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir el pedido de $100 con los datos correctos de Valsaa
"""
import sqlite3
import json
from datetime import datetime

def corregir_pedido_valsaa():
    try:
        conn = sqlite3.connect('pos_pedidos.db')
        cursor = conn.cursor()
        
        print("🔧 CORRIGIENDO PEDIDO DE VALSAA ($100)...")
        
        # Encontrar el pedido de $100
        cursor.execute('SELECT id FROM pedidos WHERE total = 100.0 ORDER BY fecha_creacion DESC LIMIT 1')
        pedido = cursor.fetchone()
        
        if pedido:
            pedido_id = pedido[0]
            print(f"📋 Corrigiendo pedido: {pedido_id}")
            
            # Corregir con los datos exactos del pedido
            cursor.execute('''
                UPDATE pedidos 
                SET cliente_nombre = "Valsaa",
                    cliente_telefono = "1253652580", 
                    hora_recogida = "12:00 PM",
                    metodo_pago = "Terminal Mercado Pago en sucursal"
                WHERE id = ?
            ''', (pedido_id,))
            
            conn.commit()
            
            # Verificar el resultado
            cursor.execute('SELECT cliente_nombre, cliente_telefono, hora_recogida, metodo_pago FROM pedidos WHERE id = ?', (pedido_id,))
            datos = cursor.fetchone()
            
            print("✅ PEDIDO CORREGIDO:")
            print(f"👤 Cliente: {datos[0]}")
            print(f"📱 Teléfono: {datos[1]}")
            print(f"🕐 Hora: {datos[2]}")
            print(f"💳 Método: {datos[3]}")
            print("\n🎯 Ahora presiona 'Actualizar' en tu POS para ver los cambios")
            
        else:
            print("❌ No se encontró el pedido de $100")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    corregir_pedido_valsaa()
