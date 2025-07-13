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
                    
                    # Extraer datos del cliente de manera más robusta
                    cliente_nombre = cliente_info.get('name', '')
                    cliente_telefono = cliente_info.get('phone', '')
                    metodo_pago = cliente_info.get('payment_method', 'No especificado')
                    
                    # Si el teléfono viene como objeto (estructura antigua)
                    if isinstance(cliente_telefono, dict):
                        cliente_telefono = cliente_telefono.get('number', '')
                    
                    # Si no hay datos, intentar de la estructura alternativa
                    if not cliente_nombre and 'payer' in order:
                        payer = order['payer']
                        cliente_nombre = payer.get('name', '')
                        if isinstance(payer.get('phone'), dict):
                            cliente_telefono = payer.get('phone', {}).get('number', '')
                        else:
                            cliente_telefono = payer.get('phone', '')
                    
                    print(f"🔍 DEBUG EXTRACCIÓN DATOS:")
                    print(f"   👤 Nombre extraído: '{cliente_nombre}'")
                    print(f"   📱 Teléfono extraído: '{cliente_telefono}'")
                    print(f"   💳 Método pago: '{metodo_pago}'")
                    print(f"   📊 Estructura customer: {cliente_info}")
                    print(f"   📊 Estructura payer: {order.get('payer', 'No existe')}")
                    
                    # Formatear items con información clara y legible
                    items = []
                    for item in items_raw:
                        # Obtener nombre base del producto
                        nombre_producto = item.get('title', item.get('nombre', 'Producto'))
                        
                        # Mejorar formato del nombre para mejor legibilidad en POS
                        nombre_formateado = self._formatear_nombre_producto(nombre_producto)
                        
                        items.append({
                            "name": nombre_formateado,
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
                        cliente_nombre,
                        cliente_telefono,
                        metadata.get('pickup_time', ''),
                        json.dumps(items, ensure_ascii=False),
                        total,
                        'pendiente',
                        metodo_pago,
                        order.get('timestamp', datetime.now().isoformat()),
                        datetime.now().isoformat()
                    ))
                    
                    self.pedidos_procesados.add(order_id)
                    nuevos_pedidos += 1
                    
                    logger.info(f"✅ NUEVO PEDIDO AUTOMÁTICO:")
                    logger.info(f"   👤 Cliente: {cliente_nombre or 'Sin nombre'}")
                    logger.info(f"   📱 Teléfono: {cliente_telefono or 'Sin teléfono'}")
                    logger.info(f"   💳 Pago: {metodo_pago}")
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
    
    def _formatear_nombre_producto(self, nombre_producto):
        """Formatear nombre de producto para mejor legibilidad en POS"""
        try:
            # Casos especiales para promociones
            if "2x100 Frappes" in nombre_producto:
                # Extraer información de sabores y leches
                if "(" in nombre_producto and ")" in nombre_producto:
                    # Buscar patrones como "(Moka + Taro)" y "Moka: Deslactosada, Taro: Deslactosada"
                    partes = nombre_producto.split(" - ")
                    if len(partes) >= 3:
                        base = "🎉 PROMO 2x100 Frappes"
                        sabores = ""
                        leches = ""
                        
                        for parte in partes[1:]:
                            if "(" in parte and "+" in parte:
                                # Extraer sabores: "(Moka + Taro)"
                                sabores = parte.strip("()")
                            elif ":" in parte and any(leche in parte for leche in ["Entera", "Deslactosada", "Light"]):
                                # Extraer información de leches
                                leches = parte
                        
                        if sabores and leches:
                            return f"{base}: {sabores} | Leches: {leches}"
                        elif sabores:
                            return f"{base}: {sabores}"
                
                return "🎉 PROMO 2x100 Frappes"
            
            # Casos para frappes individuales
            elif "Frappé" in nombre_producto or "frappé" in nombre_producto:
                if "(Leche:" in nombre_producto:
                    # Formato: "Frappé Moka (Leche: Deslactosada)"
                    partes = nombre_producto.split("(Leche:")
                    if len(partes) == 2:
                        sabor = partes[0].strip()
                        leche = partes[1].strip().rstrip(")")
                        return f"🥤 {sabor} | Leche: {leche}"
                return f"🥤 {nombre_producto}"
            
            # Casos para bebidas frías
            elif any(bebida in nombre_producto for bebida in ["Latte Matcha", "Cold Brew", "Chai", "Caramel Macchiato"]):
                if "(Leche:" in nombre_producto:
                    partes = nombre_producto.split("(Leche:")
                    if len(partes) == 2:
                        bebida = partes[0].strip()
                        leche = partes[1].strip().rstrip(")")
                        return f"🧊 {bebida} | Leche: {leche}"
                return f"🧊 {nombre_producto}"
            
            # Casos para café caliente
            elif any(cafe in nombre_producto for cafe in ["Capuchino", "Moka", "Latte", "Americano"]):
                if "(Leche:" in nombre_producto:
                    partes = nombre_producto.split("(Leche:")
                    if len(partes) == 2:
                        cafe = partes[0].strip()
                        leche = partes[1].strip().rstrip(")")
                        return f"☕ {cafe} | Leche: {leche}"
                return f"☕ {nombre_producto}"
            
            # Casos para bebidas embotelladas
            elif any(refresco in nombre_producto for refresco in ["Coca Cola", "Agua"]):
                return f"🥤 {nombre_producto}"
            
            # Casos para postres
            elif any(postre in nombre_producto for postre in ["Waffles", "Budín", "Flan"]):
                return f"🍰 {nombre_producto}"
            
            # Casos para pan
            elif any(pan in nombre_producto for pan in ["Carterita", "Concha"]):
                return f"🥖 {nombre_producto}"
            
            # Producto genérico
            else:
                return f"📦 {nombre_producto}"
                
        except Exception as e:
            logger.warning(f"⚠️ Error formateando producto '{nombre_producto}': {e}")
            return nombre_producto

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
