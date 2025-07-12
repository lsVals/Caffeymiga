#!/usr/bin/env python3
"""
Script de sincronización POS para Caffe & Miga
Conecta el sistema web con el sistema POS local
"""

import requests
import time
import json
import sqlite3
import os
from datetime import datetime

class SincronizadorPOS:
    def __init__(self, servidor_url="http://localhost:3000", pos_db_path=None):
        self.servidor_url = servidor_url
        self.pos_db_path = pos_db_path or "pos_pedidos.db"
        self.ultimo_sync = None
        
    def crear_base_datos(self):
        """Crear base de datos local si no existe"""
        conn = sqlite3.connect(self.pos_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id TEXT PRIMARY KEY,
                cliente_nombre TEXT,
                cliente_telefono TEXT,
                hora_recogida TEXT,
                items TEXT,
                total REAL,
                estado TEXT DEFAULT 'pendiente',
                metodo_pago TEXT,
                fecha_creacion TEXT,
                fecha_actualizacion TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Base de datos local creada/verificada")
    
    def obtener_pedidos_servidor(self):
        """Obtener pedidos del servidor web"""
        try:
            response = requests.get(f"{self.servidor_url}/pos/orders", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('orders', [])
            else:
                print(f"❌ Error del servidor: {response.status_code}")
                return []
        except requests.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return []
    
    def guardar_pedido_local(self, pedido):
        """Guardar pedido en base de datos local"""
        conn = sqlite3.connect(self.pos_db_path)
        cursor = conn.cursor()
        
        try:
            # Convertir items a JSON string si es necesario
            items_json = json.dumps(pedido.get('items', [])) if isinstance(pedido.get('items'), list) else str(pedido.get('items', ''))
            
            cursor.execute('''
                INSERT OR REPLACE INTO pedidos 
                (id, cliente_nombre, cliente_telefono, hora_recogida, items, total, estado, metodo_pago, fecha_creacion, fecha_actualizacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pedido.get('id', pedido.get('preference_id', '')),
                pedido.get('customer_name', pedido.get('payer', {}).get('name', '')),
                pedido.get('customer_phone', pedido.get('payer', {}).get('phone', {}).get('number', '')),
                pedido.get('pickup_time', pedido.get('metadata', {}).get('pickup_time', '')),
                items_json,
                float(pedido.get('total', 0)),
                pedido.get('status', 'pendiente'),
                pedido.get('payment_method', 'mercado_pago'),
                pedido.get('created_at', datetime.now().isoformat()),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error guardando pedido: {e}")
            return False
        finally:
            conn.close()
    
    def sincronizar(self):
        """Sincronizar pedidos del servidor al POS local"""
        print("🔄 Iniciando sincronización...")
        
        # Crear base de datos si no existe
        self.crear_base_datos()
        
        # Obtener pedidos del servidor
        pedidos = self.obtener_pedidos_servidor()
        
        if not pedidos:
            print("ℹ️ No hay pedidos nuevos")
            return
        
        print(f"📦 Encontrados {len(pedidos)} pedidos en el servidor")
        
        # Guardar pedidos localmente
        guardados = 0
        for pedido in pedidos:
            if self.guardar_pedido_local(pedido):
                guardados += 1
        
        print(f"✅ Sincronizados {guardados} pedidos al sistema POS local")
        self.ultimo_sync = datetime.now()
    
    def verificar_conexion(self):
        """Verificar si el servidor está disponible"""
        try:
            response = requests.get(f"{self.servidor_url}/pos/test", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Servidor conectado - {data.get('order_count', 0)} pedidos disponibles")
                return True
            else:
                print(f"❌ Servidor respondió con código: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"❌ No se pudo conectar al servidor: {e}")
            return False
    
    def mostrar_pedidos_locales(self):
        """Mostrar pedidos en la base de datos local"""
        conn = sqlite3.connect(self.pos_db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM pedidos")
            count = cursor.fetchone()[0]
            
            cursor.execute("SELECT cliente_nombre, total, estado, fecha_creacion FROM pedidos ORDER BY fecha_creacion DESC LIMIT 5")
            pedidos = cursor.fetchall()
            
            print(f"\n📊 Resumen POS Local ({self.pos_db_path}):")
            print(f"   Total de pedidos: {count}")
            print(f"   Últimos 5 pedidos:")
            
            for pedido in pedidos:
                nombre, total, estado, fecha = pedido
                print(f"   - {nombre} | ${total} | {estado} | {fecha}")
                
        except sqlite3.Error as e:
            print(f"❌ Error leyendo base de datos: {e}")
        finally:
            conn.close()

def main():
    print("🏪 Sincronizador POS - Caffe & Miga")
    print("=" * 50)
    
    sincronizador = SincronizadorPOS()
    
    # Verificar conexión
    if not sincronizador.verificar_conexion():
        print("❌ No se puede conectar al servidor web. Asegúrate de que esté ejecutándose.")
        return
    
    # Sincronizar una vez
    sincronizador.sincronizar()
    
    # Mostrar resumen
    sincronizador.mostrar_pedidos_locales()
    
    print("\n✅ Sincronización completada")
    print("💡 Para sincronización automática, ejecuta este script periódicamente")

if __name__ == "__main__":
    main()
