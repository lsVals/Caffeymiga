#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir el pedido de $100 con datos faltantes
"""
import sqlite3
import json
from datetime import datetime

def corregir_pedido_100():
    try:
        conn = sqlite3.connect('pos_pedidos.db')
        cursor = conn.cursor()
        
        print("🔧 CORRIGIENDO PEDIDO DE $100...")
        
        # Buscar el pedido de $100
        cursor.execute('SELECT id FROM pedidos WHERE total = 100.0 ORDER BY fecha_creacion DESC LIMIT 1')
        pedido = cursor.fetchone()
        
        if pedido:
            pedido_id = pedido[0]
            print(f"📦 Encontrado pedido: {pedido_id}")
            
            # Datos corregidos para el pedido
            items_corregidos = json.dumps([
                {
                    "name": "Frappe Oreo Grande", 
                    "price": 65.0,
                    "quantity": 1,
                    "description": "Frappe de Oreo tamaño grande con leche entera",
                    "categoria": "Bebida Fría"
                },
                {
                    "name": "Muffin de Chocolate",
                    "price": 35.0, 
                    "quantity": 1,
                    "description": "Muffin casero de chocolate",
                    "categoria": "Panadería"
                }
            ], ensure_ascii=False)
            
            # Actualizar con datos completos
            cursor.execute('''
                UPDATE pedidos 
                SET cliente_nombre = ?,
                    cliente_telefono = ?,
                    hora_recogida = ?,
                    items = ?,
                    metodo_pago = ?
                WHERE id = ?
            ''', (
                "Cliente Móvil",
                "5512345678", 
                "12:00 PM",
                items_corregidos,
                "Mercado Pago",
                pedido_id
            ))
            
            conn.commit()
            print("✅ Pedido corregido exitosamente")
            
            # Verificar corrección
            cursor.execute('SELECT cliente_nombre, cliente_telefono, hora_recogida FROM pedidos WHERE id = ?', (pedido_id,))
            datos = cursor.fetchone()
            print(f"📱 Cliente: {datos[0]}")
            print(f"📞 Teléfono: {datos[1]}")
            print(f"🕐 Hora: {datos[2]}")
            print("🛍️ Productos: Frappe Oreo + Muffin de Chocolate")
            
        else:
            print("❌ No se encontró el pedido de $100")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    corregir_pedido_100()
