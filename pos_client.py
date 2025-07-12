# Cliente POS para Caffe & Miga
# Copia este archivo a la carpeta de tu sistema POS
# Instala: pip install requests

import requests
import json
import time
from datetime import datetime

class CaffeYMigaPOSClient:
    def __init__(self, server_url="http://127.0.0.1:3000"):
        """
        Cliente para conectar tu POS con Caffe & Miga
        
        Args:
            server_url: URL del servidor de Caffe & Miga
        """
        self.server_url = server_url.rstrip('/')
        self.last_check = datetime.now()
    
    def get_new_orders(self):
        """
        Obtener pedidos nuevos para el POS
        
        Returns:
            list: Lista de pedidos pendientes
        """
        try:
            response = requests.get(f"{self.server_url}/pos/orders", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                orders = data.get('orders', [])
                
                print(f"✅ Obtenidos {len(orders)} pedidos pendientes")
                return orders
            else:
                print(f"❌ Error obteniendo pedidos: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return []
    
    def update_order_status(self, order_id, new_status):
        """
        Actualizar estado de un pedido
        
        Args:
            order_id (str): ID del pedido
            new_status (str): Nuevo estado (preparando, listo, entregado, cancelado)
        
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            data = {"status": new_status}
            response = requests.put(
                f"{self.server_url}/pos/orders/{order_id}/status",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Pedido {order_id} actualizado a: {new_status}")
                return True
            else:
                print(f"❌ Error actualizando pedido: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def get_dashboard_stats(self):
        """
        Obtener estadísticas del dashboard
        
        Returns:
            dict: Estadísticas del POS
        """
        try:
            response = requests.get(f"{self.server_url}/pos/dashboard", timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error obteniendo estadísticas: {response.status_code}")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return {}
    
    def start_monitoring(self, callback_function, interval=30):
        """
        Monitorear pedidos nuevos cada X segundos
        
        Args:
            callback_function: Función que se ejecuta cuando llegan pedidos nuevos
            interval: Intervalo en segundos (default: 30)
        """
        print(f"🔄 Iniciando monitoreo cada {interval} segundos...")
        
        while True:
            try:
                orders = self.get_new_orders()
                
                if orders:
                    # Llamar a tu función personalizada
                    callback_function(orders)
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoreo detenido por el usuario")
                break
            except Exception as e:
                print(f"❌ Error en monitoreo: {e}")
                time.sleep(interval)

# Funciones de ejemplo para integrar con tu POS
def procesar_pedidos_nuevos(orders):
    """
    Función de ejemplo - PERSONALIZA ESTA FUNCIÓN para tu POS
    
    Args:
        orders (list): Lista de pedidos nuevos
    """
    print(f"\n🔥 {len(orders)} pedidos nuevos recibidos!")
    
    for order in orders:
        print(f"\n📋 Pedido ID: {order.get('id', 'N/A')[:8]}...")
        print(f"👤 Cliente: {order.get('customer', {}).get('name', 'N/A')}")
        print(f"📞 Teléfono: {order.get('customer', {}).get('phone', 'N/A')}")
        print(f"💰 Total: ${order.get('total', 0)} {order.get('currency', 'MXN')}")
        print(f"🕒 Hora: {order.get('created_at', 'N/A')}")
        
        print("🛒 Items:")
        for item in order.get('items', []):
            print(f"  • {item.get('quantity', 1)}x {item.get('title', 'Item')} - ${item.get('unit_price', 0)}")
        
        # AQUÍ ES DONDE INTEGRAS CON TU POS
        # Ejemplos:
        # - Agregar a tu base de datos
        # - Imprimir ticket
        # - Enviar notificación
        # - Actualizar inventario
        
        print("=" * 50)

def ejemplo_uso_basico():
    """Ejemplo básico de uso"""
    # Crear cliente
    pos_client = CaffeYMigaPOSClient()
    
    # Obtener pedidos una vez
    orders = pos_client.get_new_orders()
    
    # Procesar pedidos
    if orders:
        procesar_pedidos_nuevos(orders)
        
        # Ejemplo: marcar primer pedido como "preparando"
        first_order = orders[0]
        order_id = first_order.get('id')
        pos_client.update_order_status(order_id, 'preparando')

def ejemplo_monitoreo_continuo():
    """Ejemplo de monitoreo continuo"""
    # Crear cliente
    pos_client = CaffeYMigaPOSClient()
    
    # Iniciar monitoreo (esto corre infinitamente)
    pos_client.start_monitoring(procesar_pedidos_nuevos, interval=30)

# Ejemplo para integrar con tu sistema existente
def integrar_con_mi_pos():
    """
    PERSONALIZA ESTA FUNCIÓN según tu sistema POS
    """
    pos_client = CaffeYMigaPOSClient()
    
    # Tu lógica personalizada aquí
    orders = pos_client.get_new_orders()
    
    for order in orders:
        # Ejemplo de integración:
        
        # 1. Guardar en tu base de datos
        # mi_database.insert_order(order)
        
        # 2. Imprimir ticket
        # mi_impresora.print_ticket(order)
        
        # 3. Enviar notificación
        # mi_notificaciones.send_alert(f"Nuevo pedido: {order['customer']['name']}")
        
        # 4. Actualizar estado a "preparando"
        pos_client.update_order_status(order['id'], 'preparando')
        
        print(f"✅ Pedido {order['id'][:8]}... integrado con éxito")

if __name__ == "__main__":
    print("🔥 Cliente POS - Caffe & Miga")
    print("=" * 40)
    
    # Descomenta la opción que necesites:
    
    # Opción 1: Uso básico (una vez)
    ejemplo_uso_basico()
    
    # Opción 2: Monitoreo continuo
    # ejemplo_monitoreo_continuo()
    
    # Opción 3: Integración personalizada
    # integrar_con_mi_pos()
