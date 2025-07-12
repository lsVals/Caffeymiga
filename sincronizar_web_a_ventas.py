#!/usr/bin/env python3
"""
Script para sincronizar pedidos web a la base de datos de ventas local
Copia pedidos de pos_pedidos.db a ventas.db
"""

import sqlite3
import json
from datetime import datetime

class SincronizadorVentas:
    def __init__(self):
        self.pos_db = "pos_pedidos.db"  # Base de datos de pedidos web
        self.ventas_db = "ventas.db"    # Base de datos de ventas locales (ahora en la misma carpeta)
        
    def crear_tabla_ventas(self):
        """Crear tabla de ventas si no existe"""
        conn = sqlite3.connect(self.ventas_db)
        cursor = conn.cursor()
        
        # Crear tabla compatible con tu sistema POS
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_web TEXT,
                cliente_nombre TEXT,
                cliente_telefono TEXT,
                hora_recogida TEXT,
                productos TEXT,
                total REAL,
                estado TEXT DEFAULT 'pendiente',
                metodo_pago TEXT,
                fecha_creacion TEXT,
                fecha_actualizacion TEXT,
                origen TEXT DEFAULT 'web'
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Tabla de ventas creada/verificada")
    
    def obtener_pedidos_web(self):
        """Obtener pedidos de la base de datos web"""
        try:
            conn = sqlite3.connect(self.pos_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM pedidos")
            pedidos = cursor.fetchall()
            
            # Obtener nombres de columnas
            cursor.execute("PRAGMA table_info(pedidos)")
            columns = [col[1] for col in cursor.fetchall()]
            
            conn.close()
            
            # Convertir a diccionarios
            pedidos_dict = []
            for pedido in pedidos:
                pedido_dict = dict(zip(columns, pedido))
                pedidos_dict.append(pedido_dict)
            
            return pedidos_dict
            
        except Exception as e:
            print(f"❌ Error obteniendo pedidos web: {e}")
            return []
    
    def verificar_pedido_existe(self, id_web):
        """Verificar si un pedido web ya existe en ventas"""
        try:
            conn = sqlite3.connect(self.ventas_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM pedidos WHERE id_web = ?", (id_web,))
            existe = cursor.fetchone()[0] > 0
            
            conn.close()
            return existe
            
        except Exception as e:
            print(f"❌ Error verificando pedido: {e}")
            return False
    
    def insertar_pedido_ventas(self, pedido):
        """Insertar pedido web en la base de datos de ventas"""
        try:
            conn = sqlite3.connect(self.ventas_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO pedidos 
                (id_web, cliente_nombre, cliente_telefono, hora_recogida, productos, total, estado, metodo_pago, fecha_creacion, fecha_actualizacion, origen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pedido.get('id', ''),
                pedido.get('cliente_nombre', ''),
                pedido.get('cliente_telefono', ''),
                pedido.get('hora_recogida', ''),
                pedido.get('items', ''),  # Ya viene como JSON string
                float(pedido.get('total', 0)),
                pedido.get('estado', 'pendiente'),
                pedido.get('metodo_pago', 'web'),
                pedido.get('fecha_creacion', datetime.now().isoformat()),
                datetime.now().isoformat(),
                'web'
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error insertando pedido: {e}")
            return False
    
    def sincronizar(self):
        """Sincronizar pedidos web a ventas"""
        print("🔄 Sincronizando pedidos web a sistema de ventas...")
        
        # Crear tabla si no existe
        self.crear_tabla_ventas()
        
        # Obtener pedidos web
        pedidos_web = self.obtener_pedidos_web()
        
        if not pedidos_web:
            print("ℹ️ No hay pedidos web para sincronizar")
            return
        
        print(f"📦 Encontrados {len(pedidos_web)} pedidos web")
        
        # Sincronizar cada pedido
        nuevos = 0
        for pedido in pedidos_web:
            id_web = pedido.get('id', '')
            
            if not self.verificar_pedido_existe(id_web):
                if self.insertar_pedido_ventas(pedido):
                    nuevos += 1
                    print(f"✅ Sincronizado: {pedido.get('cliente_nombre', 'Sin nombre')} - ${pedido.get('total', 0)}")
        
        print(f"\n✅ Sincronización completada: {nuevos} pedidos nuevos agregados a ventas.db")
        
        # Mostrar resumen
        self.mostrar_resumen()
    
    def mostrar_resumen(self):
        """Mostrar resumen de pedidos en ventas.db"""
        try:
            conn = sqlite3.connect(self.ventas_db)
            cursor = conn.cursor()
            
            # Contar pedidos por origen
            cursor.execute("SELECT origen, COUNT(*) FROM pedidos GROUP BY origen")
            resumen = cursor.fetchall()
            
            print(f"\n📊 Resumen ventas.db:")
            for origen, count in resumen:
                print(f"   {origen}: {count} pedidos")
            
            # Mostrar últimos pedidos web
            cursor.execute("SELECT cliente_nombre, total, metodo_pago, fecha_creacion FROM pedidos WHERE origen='web' ORDER BY fecha_creacion DESC LIMIT 5")
            ultimos = cursor.fetchall()
            
            if ultimos:
                print(f"\n🌐 Últimos 5 pedidos web:")
                for nombre, total, metodo, fecha in ultimos:
                    print(f"   - {nombre} | ${total} | {metodo} | {fecha[:19]}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error mostrando resumen: {e}")

def main():
    print("🏪 Sincronizador Web → Ventas - Caffe & Miga")
    print("=" * 60)
    
    sincronizador = SincronizadorVentas()
    sincronizador.sincronizar()
    
    print("\n💡 Ahora tu sistema POS debería mostrar los pedidos web en ventas.db")
    print("💡 Ejecuta este script cada vez que quieras sincronizar nuevos pedidos")

if __name__ == "__main__":
    main()
