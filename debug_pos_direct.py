#!/usr/bin/env python3
# Test directo de la función show_pedidos_online del POS

import sqlite3
import sys
import os

def test_pos_function():
    print("🔍 SIMULANDO FUNCIÓN SHOW_PEDIDOS_ONLINE DEL POS")
    print("=" * 60)
    
    # Cambiar al directorio cafeteria_sistema como lo haría el POS
    original_dir = os.getcwd()
    cafeteria_dir = os.path.join(original_dir, "cafeteria_sistema")
    
    print(f"📂 Directorio actual: {original_dir}")
    print(f"📂 Directorio POS: {cafeteria_dir}")
    
    if os.path.exists(cafeteria_dir):
        os.chdir(cafeteria_dir)
        print(f"✅ Cambiado a: {os.getcwd()}")
    
    # Probar la ruta que usa el POS (../pos_pedidos.db)
    db_path = "../pos_pedidos.db"
    print(f"\n🔗 Probando ruta: {db_path}")
    print(f"🔗 Ruta absoluta: {os.path.abspath(db_path)}")
    print(f"📋 ¿Archivo existe? {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        print("❌ LA BASE DE DATOS NO SE ENCUENTRA!")
        print("🔍 Buscando pos_pedidos.db...")
        
        # Buscar en directorios posibles
        possible_paths = [
            "pos_pedidos.db",
            "../pos_pedidos.db", 
            "../../pos_pedidos.db",
            os.path.join(original_dir, "pos_pedidos.db")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ Encontrada en: {os.path.abspath(path)}")
                db_path = path
                break
        else:
            print("❌ No se encontró pos_pedidos.db en ningún lugar")
            return
    
    # Probar conexión como lo hace el POS
    try:
        print(f"\n🔌 Conectando a: {db_path}")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Test de conexión
        c.execute("SELECT COUNT(*) FROM pedidos")
        total = c.fetchone()[0]
        print(f"✅ Conexión exitosa - Total pedidos: {total}")
        
        # Obtener pedidos pendientes como lo hace el POS
        c.execute("""
            SELECT id, cliente_nombre, cliente_telefono, hora_recogida, 
                   items, total, estado, metodo_pago, fecha_creacion 
            FROM pedidos 
            WHERE estado = 'pendiente'
            ORDER BY fecha_creacion ASC
        """)
        
        pendientes = c.fetchall()
        print(f"📋 Pedidos pendientes encontrados: {len(pendientes)}")
        
        if pendientes:
            print("\n🎯 PEDIDOS QUE DEBERÍA VER EL POS:")
            for i, row in enumerate(pendientes, 1):
                print(f"   {i}. ID: {row[0]} - Cliente: {row[1] or 'Sin nombre'} - Total: ${row[5]}")
        else:
            print("❌ No hay pedidos pendientes")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return
    
    # Volver al directorio original
    os.chdir(original_dir)
    
    print(f"\n✅ Test completado. El POS DEBERÍA ver {len(pendientes)} pedidos.")
    if len(pendientes) > 0:
        print("🔧 Si no los ve, hay un problema en la interfaz del POS.")
    
if __name__ == "__main__":
    test_pos_function()
