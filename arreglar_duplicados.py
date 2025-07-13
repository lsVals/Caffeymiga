#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para arreglar pedidos duplicados y problemas de items
"""
import sqlite3
import json
from datetime import datetime

def arreglar_duplicados():
    try:
        conn = sqlite3.connect('pos_pedidos.db')
        cursor = conn.cursor()
        
        print("🔧 ARREGLANDO PROBLEMAS DEL SISTEMA...")
        
        # 1. Eliminar duplicados recientes (efectivo_1752388024)
        cursor.execute('DELETE FROM pedidos WHERE id = "efectivo_1752388024"')
        
        # 2. Corregir el pedido web_1752388007 con información completa del iPhone
        items_corregidos = json.dumps([
            {
                "name": "Producto seleccionado desde iPhone",
                "price": 12.0,
                "quantity": 1,
                "description": "Pedido realizado desde iPhone con Mercado Pago",
                "categoria": "Bebida",
                "detalles": "Especificar tipo de bebida, leche, etc."
            }
        ], ensure_ascii=False)
        
        cursor.execute('''
            UPDATE pedidos 
            SET items = ?, 
                cliente_nombre = "Teste",
                cliente_telefono = "2154362580", 
                hora_recogida = "11:30 AM",
                metodo_pago = "Terminal Mercado Pago en sucursal"
            WHERE id = "web_1752388007"
        ''', (items_corregidos,))
        
        conn.commit()
        
        # 3. Verificar resultado
        cursor.execute('SELECT COUNT(*) FROM pedidos')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT id, cliente_nombre, total, items FROM pedidos ORDER BY fecha_creacion DESC LIMIT 3')
        ultimos = cursor.fetchall()
        
        print(f"✅ ARREGLO COMPLETADO")
        print(f"📊 Total pedidos: {total}")
        print("\n📱 Últimos pedidos:")
        for pedido in ultimos:
            items_ok = "✅ OK" if pedido[3] and pedido[3] != "" else "❌ VACÍO"
            print(f"   • {pedido[0]} - {pedido[1]} - ${pedido[2]} - Items: {items_ok}")
        
        conn.close()
        print("\n🎯 Problema de duplicados solucionado")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    arreglar_duplicados()
