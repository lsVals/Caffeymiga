#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA ÚNICO DE SINCRONIZACIÓN CORREGIDO
- Elimina duplicados automáticamente
- Captura datos del cliente correctamente
- UN SOLO sistema de sincronización
"""

import requests
import sqlite3
import json
import time
import logging
from datetime import datetime
import os

class SyncUnicoCorregido:
    def __init__(self):
        self.servidor_url = "https://caffeymiga-1.onrender.com"
        self.intervalo = 30
        self.pedidos_procesados = set()
        
        # Configurar logging sin emojis
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('sync_unico.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def inicializar_db(self):
        """Inicializar base de datos con estructura correcta"""
        conn = sqlite3.connect('caffeymiga_pedidos.db')  # NUEVO NOMBRE ÚNICO
        cursor = conn.cursor()
        
        # Crear tabla si no existe (SIN cliente_email por ahora)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id TEXT PRIMARY KEY,
                cliente_nombre TEXT,
                cliente_telefono TEXT,
                hora_recogida TEXT,
                metodo_pago TEXT,
                items TEXT,
                total REAL,
                estado TEXT DEFAULT 'pendiente',
                fecha_creacion TEXT,
                fecha_actualizacion TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Base de datos inicializada")

    def limpiar_duplicados(self):
        """Eliminar pedidos duplicados manteniendo el más reciente"""
        conn = sqlite3.connect('caffeymiga_pedidos.db')  # NUEVO NOMBRE ÚNICO
        cursor = conn.cursor()
        
        # Encontrar duplicados por cliente y total
        cursor.execute('''
            DELETE FROM pedidos 
            WHERE rowid NOT IN (
                SELECT MIN(rowid) 
                FROM pedidos 
                GROUP BY cliente_nombre, cliente_telefono, total, DATE(fecha_creacion)
            )
            AND cliente_nombre != ''
        ''')
        
        duplicados_eliminados = cursor.rowcount
        
        # También eliminar pedidos sin datos de cliente muy antiguos
        cursor.execute('''
            DELETE FROM pedidos 
            WHERE (cliente_nombre = '' OR cliente_nombre IS NULL)
            AND fecha_creacion < datetime('now', '-1 hour')
        ''')
        
        conn.commit()
        conn.close()
        
        if duplicados_eliminados > 0:
            print(f"🧹 Eliminados {duplicados_eliminados} duplicados")
        
        return duplicados_eliminados

    def obtener_pedidos_servidor(self):
        """Obtener pedidos del servidor"""
        try:
            response = requests.get(
                f"{self.servidor_url}/pos/orders",
                timeout=15,
                headers={'Accept': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                orders = data.get('orders', [])
                return orders
            else:
                print(f"⚠️ Servidor respondió: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error conectando al servidor: {e}")
            return []

    def procesar_pedido(self, order):
        """Procesar un pedido individual con extracción mejorada de datos"""
        try:
            # ID del pedido
            order_id = order.get('id', order.get('preference_id', f"auto_{int(time.time())}"))
            
            # EXTRACCIÓN MEJORADA DE DATOS DEL CLIENTE
            cliente_nombre = ""
            cliente_telefono = ""
            cliente_email = ""
            metodo_pago = "No especificado"
            
            # Intentar desde 'customer' primero
            if 'customer' in order:
                customer = order['customer']
                cliente_nombre = customer.get('name', '')
                cliente_telefono = customer.get('phone', '')
                cliente_email = customer.get('email', '')
                metodo_pago = customer.get('payment_method', metodo_pago)
                
                # Si phone es un objeto
                if isinstance(cliente_telefono, dict):
                    cliente_telefono = cliente_telefono.get('number', '')
            
            # Si no hay datos, intentar desde 'payer'
            if not cliente_nombre and 'payer' in order:
                payer = order['payer']
                cliente_nombre = payer.get('name', '')
                cliente_email = payer.get('email', '')
                
                # Teléfono desde payer
                phone_data = payer.get('phone', {})
                if isinstance(phone_data, dict):
                    cliente_telefono = phone_data.get('number', '')
                else:
                    cliente_telefono = phone_data or ''
            
            # Metadata
            metadata = order.get('metadata', {})
            hora_recogida = metadata.get('pickup_time', '')
            
            # Si no hay método de pago, usar default según tipo
            if metodo_pago == "No especificado":
                if order.get('payment_method') == 'efectivo':
                    metodo_pago = "Efectivo en sucursal"
                else:
                    metodo_pago = "Terminal Mercado Pago en sucursal"
            
            # Procesar items
            items_raw = order.get('items', [])
            items = []
            
            for item in items_raw:
                nombre = item.get('title', item.get('nombre', 'Producto'))
                precio = item.get('unit_price', item.get('precio', 0))
                cantidad = item.get('quantity', item.get('cantidad', 1))
                
                items.append({
                    "name": nombre,
                    "price": precio,
                    "quantity": cantidad,
                    "description": item.get('description', '')
                })
            
            # Total
            total = order.get('total', sum(item['price'] * item['quantity'] for item in items))
            
            # DEBUG de extracción
            print(f"\n🔍 PROCESANDO PEDIDO {order_id}")
            print(f"   Nombre: '{cliente_nombre}'")
            print(f"   Teléfono: '{cliente_telefono}'")
            print(f"   Email: '{cliente_email}'")
            print(f"   Pago: '{metodo_pago}'")
            print(f"   Recogida: '{hora_recogida}'")
            print(f"   Total: ${total}")
            
            return {
                'id': order_id,
                'cliente_nombre': cliente_nombre,
                'cliente_telefono': cliente_telefono,
                'hora_recogida': hora_recogida,
                'metodo_pago': metodo_pago,
                'items': json.dumps(items, ensure_ascii=False),
                'total': total,
                'timestamp': order.get('timestamp', datetime.now().isoformat())
            }
            
        except Exception as e:
            print(f"❌ Error procesando pedido: {e}")
            return None

    def guardar_pedido(self, pedido_data):
        """Guardar pedido en base de datos evitando duplicados"""
        conn = sqlite3.connect('caffeymiga_pedidos.db')  # NUEVO NOMBRE ÚNICO
        cursor = conn.cursor()
        
        try:
            # Verificar si ya existe
            cursor.execute("SELECT id FROM pedidos WHERE id = ?", (pedido_data['id'],))
            if cursor.fetchone():
                print(f"⚠️ Pedido {pedido_data['id']} ya existe, actualizando...")
                
                # Actualizar
                cursor.execute('''
                    UPDATE pedidos SET
                        cliente_nombre = ?, cliente_telefono = ?,
                        hora_recogida = ?, metodo_pago = ?, items = ?, total = ?,
                        fecha_actualizacion = ?
                    WHERE id = ?
                ''', (
                    pedido_data['cliente_nombre'],
                    pedido_data['cliente_telefono'], 
                    pedido_data['hora_recogida'],
                    pedido_data['metodo_pago'],
                    pedido_data['items'],
                    pedido_data['total'],
                    datetime.now().isoformat(),
                    pedido_data['id']
                ))
                
                print(f"✅ Pedido {pedido_data['id']} actualizado")
            else:
                # Insertar nuevo
                cursor.execute('''
                    INSERT INTO pedidos 
                    (id, cliente_nombre, cliente_telefono,
                     hora_recogida, metodo_pago, items, total, estado,
                     fecha_creacion, fecha_actualizacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pedido_data['id'],
                    pedido_data['cliente_nombre'],
                    pedido_data['cliente_telefono'],
                    pedido_data['hora_recogida'],
                    pedido_data['metodo_pago'],
                    pedido_data['items'],
                    pedido_data['total'],
                    'pendiente',
                    pedido_data['timestamp'],
                    datetime.now().isoformat()
                ))
                
                print(f"➕ Nuevo pedido {pedido_data['id']} guardado")
                print(f"   Cliente: {pedido_data['cliente_nombre']}")
                print(f"   Teléfono: {pedido_data['cliente_telefono']}")
                print(f"   Total: ${pedido_data['total']}")
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error guardando pedido: {e}")
            return False
        finally:
            conn.close()

    def ejecutar_ciclo(self):
        """Ejecutar un ciclo de sincronización"""
        print(f"\n🔄 Ciclo sincronización - {datetime.now().strftime('%H:%M:%S')}")
        
        # 1. Limpiar duplicados
        self.limpiar_duplicados()
        
        # 2. Obtener pedidos del servidor
        orders = self.obtener_pedidos_servidor()
        
        if not orders:
            print("📭 No hay pedidos nuevos")
            return
        
        print(f"📥 Encontrados {len(orders)} pedidos en servidor")
        
        # 3. Procesar cada pedido
        nuevos = 0
        for order in orders:
            pedido_data = self.procesar_pedido(order)
            if pedido_data and self.guardar_pedido(pedido_data):
                nuevos += 1
        
        if nuevos > 0:
            print(f"✅ {nuevos} pedidos procesados correctamente")

    def iniciar(self):
        """Iniciar sincronización continua"""
        print("=" * 60)
        print("🚀 SISTEMA ÚNICO DE SINCRONIZACIÓN INICIADO")
        print(f"⏱️ Revisando cada {self.intervalo} segundos")
        print(f"📡 Servidor: {self.servidor_url}")
        print("🔄 Los pedidos llegarán automáticamente...")
        print("⏹️ Presiona Ctrl+C para detener")
        print("=" * 60)
        
        # Inicializar DB
        self.inicializar_db()
        
        try:
            while True:
                self.ejecutar_ciclo()
                print(f"💤 Esperando {self.intervalo} segundos...")
                time.sleep(self.intervalo)
                
        except KeyboardInterrupt:
            print("\n⏹️ Sincronización detenida por usuario")
        except Exception as e:
            print(f"\n❌ Error crítico: {e}")

if __name__ == "__main__":
    sync = SyncUnicoCorregido()
    sync.iniciar()
