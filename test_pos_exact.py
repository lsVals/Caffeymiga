#!/usr/bin/env python3
# Test específico de la función show_pedidos_online

import sqlite3
import sys
import os
import json

def test_show_pedidos_online():
    print("🔍 SIMULANDO FUNCIÓN SHOW_PEDIDOS_ONLINE EXACTA")
    print("=" * 70)
    
    # Cambiar al directorio cafeteria_sistema como hace el POS
    original_dir = os.getcwd()
    try:
        os.chdir("cafeteria_sistema")
        print(f"✅ Directorio POS: {os.getcwd()}")
    except:
        print("❌ No se pudo cambiar al directorio cafeteria_sistema")
        return
    
    # Usar la misma ruta que el POS
    db_path = "../pos_pedidos.db"
    print(f"🔗 Ruta BD: {db_path}")
    print(f"📋 ¿Existe? {os.path.exists(db_path)}")
    
    try:
        # Test de conexión igual que PedidosWebManager.test_connection()
        print("\n1. 🔌 TEST DE CONEXIÓN:")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM pedidos")
        count = c.fetchone()[0]
        conn.close()
        print(f"   ✅ Conexión OK - Total pedidos: {count}")
        
        # Obtener pedidos igual que PedidosWebManager.get_web_orders()
        print("\n2. 📋 OBTENIENDO PEDIDOS PENDIENTES:")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        c.execute("""
            SELECT id, cliente_nombre, cliente_telefono, hora_recogida, 
                   items, total, estado, metodo_pago, fecha_creacion 
            FROM pedidos 
            WHERE estado = 'pendiente'
            ORDER BY fecha_creacion ASC
        """)
        
        rows = c.fetchall()
        print(f"   📊 Pedidos pendientes encontrados: {len(rows)}")
        
        if rows:
            print("\n3. 🎯 DETALLES DE PEDIDOS QUE DEBERÍA VER:")
            for i, row in enumerate(rows, 1):
                pedido = {
                    'id': row[0],
                    'cliente_nombre': row[1] if row[1] else 'Cliente Web',
                    'cliente_telefono': row[2] if row[2] else 'No especificado',
                    'hora_recogida': row[3] if row[3] else 'No especificada',
                    'items': row[4] if row[4] else '[]',
                    'total': row[5] if row[5] else 0.0,
                    'estado': row[6],
                    'metodo_pago': row[7] if row[7] else 'No especificado',
                    'fecha_creacion': row[8]
                }
                
                print(f"\n   PEDIDO #{i}:")
                print(f"   🆔 ID: {pedido['id']}")
                print(f"   👤 Cliente: {pedido['cliente_nombre']}")
                print(f"   💰 Total: ${pedido['total']}")
                print(f"   📅 Estado: {pedido['estado']}")
                
                # Test del parsing de items igual que en create_order_widget
                try:
                    items_str = pedido['items'] if pedido['items'] else '[]'
                    items = json.loads(items_str) if items_str else []
                    
                    if items and len(items) > 0:
                        print(f"   🛍️ Productos ({len(items)}):")
                        for j, item in enumerate(items, 1):
                            name = item.get('name', 'Producto sin nombre')
                            quantity = item.get('quantity', 1)
                            price = float(item.get('price', 0))
                            print(f"      {j}. {name} x{quantity} = ${price:.2f}")
                    else:
                        print(f"   ⚠️ Sin productos especificados")
                        
                except json.JSONDecodeError as e:
                    print(f"   ❌ Error JSON: {e}")
                except Exception as e:
                    print(f"   ❌ Error productos: {e}")
        else:
            print("\n   ⚠️ NO HAY PEDIDOS PENDIENTES")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        return
    
    finally:
        os.chdir(original_dir)
    
    print(f"\n" + "="*70)
    if rows:
        print(f"✅ RESULTADO: El POS DEBERÍA mostrar {len(rows)} pedidos")
        print("🔧 Si no los ve, hay un problema en la interfaz GUI del POS")
    else:
        print("❌ RESULTADO: No hay pedidos pendientes para mostrar")

if __name__ == "__main__":
    test_show_pedidos_online()
