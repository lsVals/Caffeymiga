#!/usr/bin/env python3
"""
Script para verificar bases de datos SQLite en el sistema
"""

import sqlite3
import os
import glob
from datetime import datetime

def mostrar_bases_datos():
    """Mostrar todas las bases de datos SQLite encontradas"""
    print("🔍 Buscando bases de datos SQLite...")
    print("=" * 60)
    
    # Buscar archivos .db en el directorio actual
    db_files = glob.glob("*.db")
    
    if not db_files:
        print("❌ No se encontraron archivos .db en el directorio actual")
        return
    
    for db_file in db_files:
        print(f"\n📁 Base de datos: {db_file}")
        print("-" * 40)
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Obtener todas las tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if not tables:
                print("   ⚠️ No hay tablas en esta base de datos")
                conn.close()
                continue
            
            print(f"   📊 Tablas encontradas: {len(tables)}")
            
            for (table_name,) in tables:
                print(f"   \n   🗂️ Tabla: {table_name}")
                
                # Contar registros
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"      📈 Registros: {count}")
                
                if count > 0 and 'pedido' in table_name.lower():
                    print(f"      📋 Últimos 3 registros:")
                    try:
                        cursor.execute(f"SELECT * FROM {table_name} ORDER BY rowid DESC LIMIT 3")
                        records = cursor.fetchall()
                        
                        # Mostrar nombres de columnas
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = [col[1] for col in cursor.fetchall()]
                        print(f"         Columnas: {', '.join(columns)}")
                        
                        for i, record in enumerate(records, 1):
                            print(f"         {i}. {record}")
                    except Exception as e:
                        print(f"         ❌ Error leyendo registros: {e}")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Error accediendo a {db_file}: {e}")
    
    print("\n" + "=" * 60)

def buscar_tabla_pedidos():
    """Buscar específicamente tablas que contengan pedidos"""
    print("\n🎯 Buscando tablas de pedidos específicamente...")
    print("=" * 60)
    
    db_files = glob.glob("*.db")
    pedidos_encontrados = []
    
    for db_file in db_files:
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Buscar tablas con 'pedido' en el nombre
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%pedido%';")
            pedido_tables = cursor.fetchall()
            
            for (table_name,) in pedido_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                
                pedidos_encontrados.append({
                    'db': db_file,
                    'tabla': table_name,
                    'registros': count
                })
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error con {db_file}: {e}")
    
    if pedidos_encontrados:
        print("✅ Tablas de pedidos encontradas:")
        for pedido in pedidos_encontrados:
            print(f"   📊 {pedido['db']} -> {pedido['tabla']} ({pedido['registros']} registros)")
    else:
        print("❌ No se encontraron tablas de pedidos")

if __name__ == "__main__":
    print("🏪 Verificador de Bases de Datos - Caffe & Miga")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    mostrar_bases_datos()
    buscar_tabla_pedidos()
    
    print("\n💡 Si tu sistema POS no muestra pedidos, verifica:")
    print("   1. Que esté leyendo la base de datos correcta")
    print("   2. Que la tabla tenga el nombre correcto")
    print("   3. Que los pedidos estén en el formato esperado")
