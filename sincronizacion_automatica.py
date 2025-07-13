#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE SINCRONIZACIÓN AUTOMÁTICA COMPLETA
Descarga pedidos automáticamente desde el servidor de producción
Se ejecuta continuamente en segundo plano
"""
import time
import requests
import sqlite3
import json
from datetime import datetime
import threading
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sync_automatico.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SincronizadorAutomatico:
    def __init__(self):
        self.servidor_url = "https://caffeymiga-1.onrender.com"
        self.intervalo_segundos = 30  # Revisar cada 30 segundos
        self.ejecutando = False
        self.hilo = None
        self.pedidos_procesados = set()  # Para evitar duplicados
        
    def iniciar(self):
        """Iniciar sincronización automática continua"""
        if self.ejecutando:
            logger.warning("⚠️ La sincronización automática ya está ejecutándose")
            return
        
        self.ejecutando = True
        self.hilo = threading.Thread(target=self._bucle_sincronizacion, daemon=True)
        self.hilo.start()
        
        logger.info("🚀 SINCRONIZACIÓN AUTOMÁTICA INICIADA")
        logger.info(f"⏱️ Revisando cada {self.intervalo_segundos} segundos")
        logger.info(f"📡 Servidor: {self.servidor_url}")
        logger.info("🔄 Los pedidos llegarán automáticamente...")
    
    def detener(self):
        """Detener sincronización automática"""
        self.ejecutando = False
        if self.hilo:
            self.hilo.join()
        logger.info("⏹️ Sincronización automática detenida")
    
    def _bucle_sincronizacion(self):
        """Bucle principal que se ejecuta continuamente"""
        while self.ejecutando:
            try:
                self._sincronizar_pedidos()
                time.sleep(self.intervalo_segundos)
            except Exception as e:
                logger.error(f"❌ Error en bucle de sincronización: {e}")
                time.sleep(60)  # Esperar más tiempo si hay error
    
    def _sincronizar_pedidos(self):
        """Sincronizar pedidos desde Firebase/servidor"""
        try:
            # Método 1: Intentar obtener desde Firebase directamente
            if self._sincronizar_desde_firebase():
                return
            
            # Método 2: Intentar desde endpoint del servidor
            if self._sincronizar_desde_servidor():
                return
                
            # Método 3: Sincronización de respaldo
            self._sincronizacion_respaldo()
            
        except Exception as e:
            logger.error(f"❌ Error en sincronización: {e}")
    
    def _sincronizar_desde_firebase(self):
        """Sincronizar directamente desde Firebase"""
        try:
            # Endpoint que consulta Firebase directamente
            response = requests.get(
                f"{self.servidor_url}/api/orders/firebase", 
                timeout=15,
                params={'status': 'pending'}
            )
            
            if response.status_code == 200:
                data = response.json()
                orders = data.get('orders', [])
                
                if orders:
                    nuevos = self._procesar_pedidos(orders, "Firebase")
                    if nuevos > 0:
                        logger.info(f"📥 Firebase: {nuevos} pedidos nuevos descargados")
                    return True
                else:
                    logger.debug("📭 Firebase: No hay pedidos nuevos")
                    return True
            
        except Exception as e:
            logger.debug(f"🔍 Firebase no disponible: {e}")
        
        return False
    
    def _sincronizar_desde_servidor(self):
        """Sincronizar desde endpoint del servidor"""
        try:
            response = requests.get(
                f"{self.servidor_url}/pos/orders", 
                timeout=15,
                headers={'Accept': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                orders = data.get('orders', [])
                
                if orders:
                    nuevos = self._procesar_pedidos(orders, "Servidor")
                    if nuevos > 0:
                        logger.info(f"📥 Servidor: {nuevos} pedidos nuevos descargados")
                    return True
                else:
                    logger.debug("📭 Servidor: No hay pedidos nuevos")
                    return True
            
        except Exception as e:
            logger.debug(f"🔍 Servidor no disponible: {e}")
        
        return False
    
    def _sincronizacion_respaldo(self):
        """Sistema de respaldo para obtener pedidos"""
        try:
            # Intentar diferentes endpoints
            endpoints = [
                "/api/orders/pending",
                "/webhook/orders",
                "/sync/orders"
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(f"{self.servidor_url}{endpoint}", timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if 'orders' in data:
                            nuevos = self._procesar_pedidos(data['orders'], f"Respaldo{endpoint}")
                            if nuevos > 0:
                                logger.info(f"📥 Respaldo: {nuevos} pedidos desde {endpoint}")
                            return
                except:
                    continue
            
            logger.debug("💤 Sin pedidos nuevos en este momento")
            
        except Exception as e:
            logger.debug(f"🔍 Respaldo no disponible: {e}")
    
    def _procesar_pedidos(self, orders, fuente):
        """Procesar y guardar pedidos en la base de datos local"""
        nuevos_pedidos = 0
        
        try:
            conn = sqlite3.connect('pos_pedidos.db')
            cursor = conn.cursor()
            
            for order in orders:
                try:
                    order_id = order.get('id', order.get('preference_id', f"auto_{int(datetime.now().timestamp())}"))
                    
                    # Evitar duplicados
                    if order_id in self.pedidos_procesados:
                        continue
                    
                    # Verificar si ya existe en la BD
                    cursor.execute("SELECT id FROM pedidos WHERE id = ?", (order_id,))
                    if cursor.fetchone():
                        self.pedidos_procesados.add(order_id)
                        continue
                    
                    # Extraer información del pedido
                    cliente_info = order.get('customer', order.get('payer', {}))
                    items_raw = order.get('items', order.get('productos', []))
                    metadata = order.get('metadata', {})
                    
                    # Formatear items
                    items = []
                    for item in items_raw:
                        items.append({
                            "name": item.get('title', item.get('nombre', 'Producto')),
                            "price": item.get('unit_price', item.get('precio', 0)),
                            "quantity": item.get('quantity', item.get('cantidad', 1)),
                            "description": item.get('description', '')
                        })
                    
                    # Calcular total si no está disponible
                    total = order.get('total', sum(item['price'] * item['quantity'] for item in items))
                    
                    # Insertar pedido
                    cursor.execute('''
                        INSERT INTO pedidos (id, cliente_nombre, cliente_telefono, hora_recogida, 
                                           items, total, estado, metodo_pago, fecha_creacion, fecha_actualizacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        order_id,
                        cliente_info.get('name', ''),
                        cliente_info.get('phone', cliente_info.get('number', '')),
                        metadata.get('pickup_time', ''),
                        json.dumps(items, ensure_ascii=False),
                        total,
                        'pendiente',
                        cliente_info.get('payment_method', 'mercado_pago'),
                        order.get('timestamp', datetime.now().isoformat()),
                        datetime.now().isoformat()
                    ))
                    
                    self.pedidos_procesados.add(order_id)
                    nuevos_pedidos += 1
                    
                    logger.info(f"✅ NUEVO PEDIDO AUTOMÁTICO:")
                    logger.info(f"   👤 Cliente: {cliente_info.get('name', 'Sin nombre')}")
                    logger.info(f"   📱 Teléfono: {cliente_info.get('phone', 'Sin teléfono')}")
                    logger.info(f"   💰 Total: ${total}")
                    logger.info(f"   🆔 ID: {order_id}")
                    logger.info(f"   📡 Fuente: {fuente}")
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando pedido individual: {e}")
            
            conn.commit()
            conn.close()
            
            return nuevos_pedidos
            
        except Exception as e:
            logger.error(f"❌ Error en base de datos: {e}")
            return 0

def main():
    """Ejecutar sincronización automática continua"""
    sincronizador = SincronizadorAutomatico()
    
    print("🚀 INICIANDO SINCRONIZACIÓN AUTOMÁTICA COMPLETA")
    print("=" * 60)
    print("📱 Los pedidos del móvil/web llegarán AUTOMÁTICAMENTE")
    print("🔄 No necesitas hacer nada - todo es automático")
    print("📊 Revisa 'Pedidos en Línea' en tu sistema POS")
    print("⏹️ Presiona Ctrl+C para detener")
    print("=" * 60)
    
    try:
        sincronizador.iniciar()
        
        # Mantener el programa ejecutándose
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sincronización automática...")
        sincronizador.detener()
        print("✅ Sistema detenido correctamente")

if __name__ == "__main__":
    main()
