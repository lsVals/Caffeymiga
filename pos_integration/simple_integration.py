# Script Simple para Integrar con tu POS existente
# Copia este archivo a tu carpeta de POS y ejecútalo

import sqlite3
import requests
import json
from datetime import datetime

class SimplePOSIntegration:
    def __init__(self):
        self.server_url = "http://127.0.0.1:3000"
        # Cambiar por la ruta de tu base de datos existente
        self.tu_base_datos = "mi_pos.db"  # ← CAMBIA ESTO
    
    def obtener_pedidos_nuevos(self):
        """Obtener pedidos desde Caffe & Miga"""
        try:
            response = requests.get(f"{self.server_url}/pos/orders")
            if response.status_code == 200:
                return response.json().get('orders', [])
            return []
        except:
            print("❌ Error conectando con servidor")
            return []
    
    def agregar_a_mi_pos(self, pedido):
        """
        PERSONALIZA ESTA FUNCIÓN según tu base de datos
        """
        try:
            # Ejemplo - ajusta según tu esquema de BD
            conn = sqlite3.connect(self.tu_base_datos)
            cursor = conn.cursor()
            
            # Insertar en tu tabla de pedidos
            cursor.execute("""
                INSERT INTO pedidos (
                    id_externo, cliente, telefono, total, items, estado, fecha
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                pedido['id'],
                pedido['customer']['name'],
                pedido['customer']['phone'],
                pedido['total'],
                json.dumps(pedido['items']),
                'nuevo',
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Agregado a POS: {pedido['customer']['name']} - ${pedido['total']}")
            return True
            
        except Exception as e:
            print(f"❌ Error agregando a POS: {e}")
            return False
    
    def marcar_como_procesado(self, pedido_id):
        """Marcar pedido como procesado en Firebase"""
        try:
            response = requests.put(
                f"{self.server_url}/pos/orders/{pedido_id}/status",
                json={"status": "preparando"}
            )
            return response.status_code == 200
        except:
            return False
    
    def sincronizar(self):
        """Función principal - ejecutar cada X minutos"""
        print("🔄 Sincronizando con Caffe & Miga...")
        
        pedidos = self.obtener_pedidos_nuevos()
        
        if not pedidos:
            print("📭 No hay pedidos nuevos")
            return
        
        print(f"🔥 {len(pedidos)} pedidos nuevos encontrados!")
        
        for pedido in pedidos:
            if self.agregar_a_mi_pos(pedido):
                self.marcar_como_procesado(pedido['id'])

# USAR ESTA FUNCIÓN EN TU SISTEMA EXISTENTE
def sincronizar_pedidos():
    """Función que puedes llamar desde tu POS cada 30 segundos"""
    pos = SimplePOSIntegration()
    pos.sincronizar()

if __name__ == "__main__":
    # Ejecutar una vez
    sincronizar_pedidos()
    
    # O ejecutar en bucle
    import time
    while True:
        sincronizar_pedidos()
        time.sleep(30)  # Cada 30 segundos
