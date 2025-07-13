#!/usr/bin/env python3
# Script para debuggear el estado de los pedidos

import sqlite3
import json
from datetime import datetime

print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA")
print("=" * 50)

# 1. Verificar base de datos POS
print("\n📊 1. VERIFICANDO BASE DE DATOS POS:")
try:
    conn = sqlite3.connect('pos_pedidos.db')
    c = conn.cursor()
    
    # Contar total de pedidos
    c.execute('SELECT COUNT(*) FROM pedidos')
    total = c.fetchone()[0]
    print(f"   Total de pedidos: {total}")
    
    # Mostrar últimos 3 pedidos
    c.execute('''SELECT id, cliente_nombre, cliente_telefono, total, estado, 
                        fecha_creacion, hora_recogida 
                 FROM pedidos 
                 ORDER BY fecha_creacion DESC 
                 LIMIT 3''')
    
    pedidos = c.fetchall()
    print(f"   Últimos 3 pedidos:")
    for i, pedido in enumerate(pedidos, 1):
        print(f"   {i}. ID: {pedido[0]}")
        print(f"      Cliente: '{pedido[1]}' | Teléfono: '{pedido[2]}'")
        print(f"      Total: ${pedido[3]} | Estado: {pedido[4]}")
        print(f"      Fecha: {pedido[5]} | Hora recogida: {pedido[6]}")
        print()
    
    conn.close()
    
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Verificar últimos pedidos con efectivo
print("\n💰 2. PEDIDOS DE EFECTIVO:")
try:
    conn = sqlite3.connect('pos_pedidos.db')
    c = conn.cursor()
    
    c.execute('''SELECT id, cliente_nombre, cliente_telefono, metodo_pago, fecha_creacion 
                 FROM pedidos 
                 WHERE metodo_pago LIKE '%efectivo%' OR metodo_pago LIKE '%Efectivo%'
                 ORDER BY fecha_creacion DESC 
                 LIMIT 3''')
    
    efectivo_pedidos = c.fetchall()
    if efectivo_pedidos:
        print(f"   Encontrados {len(efectivo_pedidos)} pedidos de efectivo:")
        for pedido in efectivo_pedidos:
            print(f"   - {pedido[0]}: {pedido[1]} ({pedido[2]}) - {pedido[3]} - {pedido[4]}")
    else:
        print("   ❌ No se encontraron pedidos de efectivo")
    
    conn.close()
    
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Verificar sincronización
print("\n🔄 3. ESTADO DE SINCRONIZACIÓN:")
try:
    import requests
    response = requests.get('https://caffeymiga-1.onrender.com/pos/orders', timeout=10)
    if response.status_code == 200:
        orders = response.json()
        print(f"   ✅ Servidor responde: {len(orders)} pedidos disponibles")
        if orders:
            latest = orders[-1]
            print(f"   Último pedido en servidor:")
            print(f"   - ID: {latest.get('id', 'N/A')}")
            print(f"   - Cliente: {latest.get('cliente', {}).get('nombre', 'N/A')}")
            print(f"   - Total: ${latest.get('total', 'N/A')}")
    else:
        print(f"   ❌ Servidor error: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Error conectando al servidor: {e}")

print("\n" + "=" * 50)
print("🎯 DIAGNÓSTICO COMPLETADO")
