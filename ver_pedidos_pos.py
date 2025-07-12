#!/usr/bin/env python3
"""
Mostrar pedidos sincronizados para Caffe & Miga POS
Ejecuta este script desde la carpeta de tu sistema POS
"""

import sqlite3
import json
import os
from datetime import datetime

def mostrar_pedidos():
    """Mostrar todos los pedidos sincronizados"""
    db_path = "pos_pedidos.db"
    
    if not os.path.exists(db_path):
        print("❌ No se encontró la base de datos pos_pedidos.db")
        print("💡 Ejecuta primero el sincronizador desde la carpeta web")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total = cursor.fetchone()[0]
        
        print(f"🏪 PEDIDOS CAFFE & MIGA - Total: {total}")
        print("=" * 80)
        
        if total == 0:
            print("📭 No hay pedidos pendientes")
            return
        
        cursor.execute("""
            SELECT id, cliente_nombre, cliente_telefono, hora_recogida, 
                   items, total, estado, metodo_pago, fecha_creacion
            FROM pedidos 
            ORDER BY fecha_creacion DESC
        """)
        
        pedidos = cursor.fetchall()
        
        for i, pedido in enumerate(pedidos, 1):
            id_pedido, nombre, telefono, hora, items_json, total, estado, metodo, fecha = pedido
            
            print(f"\n📋 PEDIDO #{i}")
            print(f"   ID: {id_pedido}")
            print(f"   Cliente: {nombre or 'Sin nombre'}")
            print(f"   Teléfono: {telefono or 'Sin teléfono'}")
            print(f"   Hora recogida: {hora or 'Sin especificar'}")
            print(f"   Total: ${total}")
            print(f"   Estado: {estado}")
            print(f"   Método pago: {metodo}")
            print(f"   Fecha: {fecha}")
            
            # Mostrar items si están disponibles
            try:
                if items_json:
                    items = json.loads(items_json) if isinstance(items_json, str) else items_json
                    print(f"   Productos:")
                    if isinstance(items, list):
                        for item in items:
                            if isinstance(item, dict):
                                nombre_item = item.get('title', item.get('name', 'Producto'))
                                cantidad = item.get('quantity', 1)
                                precio = item.get('unit_price', item.get('price', 0))
                                print(f"     - {cantidad}x {nombre_item} (${precio})")
                            else:
                                print(f"     - {item}")
                    else:
                        print(f"     - {items}")
            except:
                print(f"   Productos: {items_json}")
            
            print("-" * 80)
        
        # Mostrar estadísticas
        cursor.execute("SELECT estado, COUNT(*) FROM pedidos GROUP BY estado")
        estados = cursor.fetchall()
        
        print(f"\n📊 ESTADÍSTICAS:")
        for estado, count in estados:
            print(f"   {estado}: {count} pedidos")
            
    except sqlite3.Error as e:
        print(f"❌ Error leyendo base de datos: {e}")
    finally:
        conn.close()

def marcar_como_listo(pedido_id):
    """Marcar un pedido como listo"""
    db_path = "pos_pedidos.db"
    
    if not os.path.exists(db_path):
        print("❌ No se encontró la base de datos")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE pedidos 
            SET estado = 'listo', fecha_actualizacion = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), pedido_id))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ Pedido {pedido_id} marcado como LISTO")
            return True
        else:
            print(f"❌ No se encontró el pedido {pedido_id}")
            return False
            
    except sqlite3.Error as e:
        print(f"❌ Error actualizando pedido: {e}")
        return False
    finally:
        conn.close()

def main():
    print("🏪 SISTEMA POS - CAFFE & MIGA")
    print("=" * 50)
    
    while True:
        mostrar_pedidos()
        
        print(f"\n🔧 OPCIONES:")
        print("1. Refrescar pedidos")
        print("2. Marcar pedido como listo")
        print("3. Salir")
        
        opcion = input("\nSelecciona una opción (1-3): ").strip()
        
        if opcion == "1":
            print("\n🔄 Refrescando...")
            continue
        elif opcion == "2":
            pedido_id = input("Ingresa el ID del pedido a marcar como listo: ").strip()
            if pedido_id:
                marcar_como_listo(pedido_id)
                input("\nPresiona Enter para continuar...")
        elif opcion == "3":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción no válida")
            input("Presiona Enter para continuar...")

if __name__ == "__main__":
    main()
