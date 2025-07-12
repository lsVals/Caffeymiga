#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
from datetime import datetime

def check_database(db_path, db_name):
    """Verificar contenido de una base de datos"""
    print(f"\n{'='*50}")
    print(f"🔍 VERIFICANDO {db_name.upper()}")
    print(f"📂 Ruta: {db_path}")
    print(f"{'='*50}")
    
    if not os.path.exists(db_path):
        print(f"❌ {db_name} NO EXISTE")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Ver todas las tablas
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        
        if not tables:
            print(f"⚠️ {db_name} está VACÍA (sin tablas)")
            conn.close()
            return False
        
        print(f"📋 Tablas encontradas: {[t[0] for t in tables]}")
        
        # Verificar contenido de cada tabla
        for table in tables:
            table_name = table[0]
            print(f"\n📊 Tabla: {table_name}")
            
            try:
                # Contar registros
                c.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = c.fetchone()[0]
                print(f"   📈 Registros: {count}")
                
                if count > 0:
                    # Mostrar estructura
                    c.execute(f"PRAGMA table_info({table_name})")
                    columns = c.fetchall()
                    print(f"   🏗️ Columnas: {[col[1] for col in columns]}")
                    
                    # Mostrar últimos registros
                    c.execute(f"SELECT * FROM {table_name} ORDER BY ROWID DESC LIMIT 3")
                    recent = c.fetchall()
                    if recent:
                        print(f"   🔄 Últimos registros:")
                        for i, row in enumerate(recent, 1):
                            print(f"      {i}: {row}")
                else:
                    print(f"   ⚠️ Tabla {table_name} está VACÍA")
                    
            except Exception as e:
                print(f"   ❌ Error leyendo tabla {table_name}: {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error conectando a {db_name}: {e}")
        return False

def main():
    print(f"🕒 Verificación de bases de datos - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Base de datos de ventas
    ventas_path = "cafeteria_sistema/ventas.db"
    ventas_ok = check_database(ventas_path, "VENTAS")
    
    # Base de datos de pedidos POS
    pedidos_path = "cafeteria_sistema/pos_pedidos.db"
    pedidos_ok = check_database(pedidos_path, "PEDIDOS POS")
    
    print(f"\n{'='*50}")
    print("📋 RESUMEN:")
    print(f"✅ Ventas DB: {'OK' if ventas_ok else 'PROBLEMA'}")
    print(f"✅ Pedidos DB: {'OK' if pedidos_ok else 'PROBLEMA'}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
