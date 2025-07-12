# INTEGRACIÓN SIMPLE PARA CAFETERIA_SISTEMA.PY
# Este script se ejecuta junto con tu sistema existente

import sqlite3
import requests
import threading
import time
from datetime import datetime
import json

class CaffeMigaIntegration:
    def __init__(self):
        self.server_url = "http://127.0.0.1:3000"
        self.db_path = "ventas.db"
        self.running = False
        
        print("🔥 Iniciando integración Caffe & Miga")
        print(f"📊 Base de datos: {self.db_path}")
        print(f"🌐 Servidor: {self.server_url}")
        
        # Verificar conexión
        self.test_connection()
    
    def test_connection(self):
        """Probar conexión con el servidor"""
        try:
            response = requests.get(f"{self.server_url}/", timeout=5)
            if response.status_code == 200:
                print("✅ Conexión con servidor OK")
                return True
            else:
                print("⚠️ Servidor responde pero con error")
                return False
        except:
            print("❌ No se puede conectar al servidor")
            print("💡 Asegúrate de que el servidor esté corriendo en puerto 3000")
            return False
    
    def get_web_orders(self):
        """Obtener pedidos web del servidor"""
        try:
            response = requests.get(f"{self.server_url}/pos/orders", timeout=10)
            if response.status_code == 200:
                data = response.json()
                orders = data.get('orders', [])
                print(f"📦 {len(orders)} pedidos disponibles")
                return orders
            else:
                print(f"⚠️ Error obteniendo pedidos: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error conectando: {e}")
            return []
    
    def insert_web_order(self, order):
        """Insertar pedido web en la base de datos"""
        try:
            # Datos del pedido
            customer = order.get('customer', {})
            items = order.get('items', [])
            
            # Crear descripción de productos
            productos_desc = []
            total_cantidad = 0
            
            for item in items:
                qty = item.get('quantity', 1)
                title = item.get('title', 'Producto')
                price = item.get('unit_price', 0)
                
                productos_desc.append(f"{qty}x {title} (${price})")
                total_cantidad += qty
            
            productos_str = " + ".join(productos_desc)
            
            # Conectar a la base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar estructura de la tabla tickets
            cursor.execute("PRAGMA table_info(tickets)")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"📋 Columnas disponibles: {columns}")
            
            # Insertar pedido
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Datos a insertar
            insert_data = {
                'fecha': fecha_actual,
                'producto': productos_str,
                'cantidad': total_cantidad,
                'precio': order.get('total', 0),
                'pago': 'WEB-TARJETA',
                'estado': 'NUEVO-WEB',
                'motivo_cancelacion': f"Pedido web - {customer.get('name', 'Cliente')} - Tel: {customer.get('phone', 'N/A')}"
            }
            
            # Construir query dinámicamente
            available_columns = []
            values = []
            
            for col, value in insert_data.items():
                if col in columns:
                    available_columns.append(col)
                    values.append(value)
            
            if available_columns:
                placeholders = ', '.join(['?' for _ in values])
                query = f"INSERT INTO tickets ({', '.join(available_columns)}) VALUES ({placeholders})"
                
                cursor.execute(query, values)
                conn.commit()
                
                print(f"✅ Pedido insertado: {customer.get('name', 'Cliente')} - ${order.get('total', 0)}")
                print(f"   📝 Productos: {productos_str}")
                
                # Marcar como procesado en el servidor
                order_id = order.get('id')
                if order_id:
                    try:
                        requests.put(f"{self.server_url}/pos/orders/{order_id}/status",
                                   json={"status": "preparando"}, timeout=5)
                    except:
                        pass
                
                conn.close()
                return True
            else:
                print("❌ No se encontraron columnas compatibles")
                conn.close()
                return False
                
        except Exception as e:
            print(f"❌ Error insertando pedido: {e}")
            return False
    
    def check_for_orders(self):
        """Verificar y procesar nuevos pedidos"""
        print("\n🔄 Verificando nuevos pedidos...")
        
        orders = self.get_web_orders()
        
        if not orders:
            print("📭 No hay pedidos nuevos")
            return
        
        new_orders = 0
        for order in orders:
            # Solo procesar pedidos nuevos o pendientes
            pos_status = order.get('pos_status', 'listo_para_preparar')
            if pos_status in ['listo_para_preparar', 'nuevo']:
                if self.insert_web_order(order):
                    new_orders += 1
        
        if new_orders > 0:
            print(f"🎉 {new_orders} pedidos nuevos agregados a tu sistema")
        else:
            print("📝 No hay pedidos nuevos para procesar")
    
    def start_monitoring(self, interval=30):
        """Iniciar monitoreo automático"""
        self.running = True
        print(f"\n🔄 Iniciando monitoreo automático cada {interval} segundos")
        print("💡 Presiona Ctrl+C para detener")
        
        def monitor():
            while self.running:
                try:
                    self.check_for_orders()
                    time.sleep(interval)
                except KeyboardInterrupt:
                    print("\n🛑 Monitoreo detenido por el usuario")
                    self.running = False
                    break
                except Exception as e:
                    print(f"❌ Error en monitoreo: {e}")
                    time.sleep(interval)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        
        try:
            monitor_thread.join()
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo monitoreo...")
            self.running = False
    
    def stop_monitoring(self):
        """Detener monitoreo"""
        self.running = False
        print("🛑 Monitoreo detenido")

def main():
    """Función principal"""
    print("🔥 INTEGRACIÓN CAFFE & MIGA")
    print("=" * 40)
    print("Este script conecta tu sistema con el e-commerce")
    print("Los pedidos web aparecerán automáticamente en tu base de datos")
    print("=" * 40)
    
    # Crear integración
    integration = CaffeMigaIntegration()
    
    print("\nOpciones:")
    print("1. Verificar pedidos ahora")
    print("2. Iniciar monitoreo automático")
    print("3. Solo probar conexión")
    
    try:
        opcion = input("\nSelecciona una opción (1-3): ").strip()
        
        if opcion == "1":
            integration.check_for_orders()
        elif opcion == "2":
            integration.start_monitoring(30)
        elif opcion == "3":
            integration.test_connection()
        else:
            print("Opción inválida")
            
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
