#!/usr/bin/env python3
# Test de conexión POS con base de datos

import sqlite3
import sys
import os

# Simular la clase PedidosWebManager
class TestPedidosWebManager:
    def __init__(self):
        self.db_path = "pos_pedidos.db"
    
    def test_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM pedidos")
            count = c.fetchone()[0]
            conn.close()
            print(f"✅ Conexión exitosa! Base de datos tiene {count} pedidos")
            return True
        except Exception as e:
            print(f"❌ Error conectando: {e}")
            return False
    
    def get_web_orders(self):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute("""
                SELECT id, cliente_nombre, cliente_telefono, hora_recogida, 
                       items, total, estado, metodo_pago, fecha_creacion 
                FROM pedidos 
                WHERE estado = 'pendiente'
                ORDER BY fecha_creacion ASC
            """)
            
            pedidos = []
            for row in c.fetchall():
                pedido = {
                    'id': row[0],
                    'cliente_nombre': row[1] if row[1] else 'Cliente Web',
                    'cliente_telefono': row[2] if row[2] else 'No especificado',
                    'hora_recogida': row[3] if row[3] else 'No especificada',
                    'items': row[4] if row[4] else '[]',
                    'total': row[5] if row[5] else 0.0,
                    'estado': row[6],
                    'metodo_pago': row[7] if row[7] else 'No especificado',
                    'fecha_creacion': row[8]
                }
                pedidos.append(pedido)
            
            conn.close()
            return pedidos
            
        except Exception as e:
            print(f"❌ Error obteniendo pedidos: {e}")
            return []

def main():
    print("🧪 TEST DE CONEXIÓN POS")
    print("=" * 50)
    
    # Verificar que existe la base de datos
    if not os.path.exists("pos_pedidos.db"):
        print("❌ No se encuentra pos_pedidos.db en el directorio actual")
        return
    
    # Crear manager de prueba
    manager = TestPedidosWebManager()
    
    # Test de conexión
    print("\n1. Probando conexión...")
    if not manager.test_connection():
        return
    
    # Test de obtener pedidos
    print("\n2. Probando obtener pedidos pendientes...")
    pedidos = manager.get_web_orders()
    
    if pedidos:
        print(f"✅ Se encontraron {len(pedidos)} pedidos pendientes:")
        for i, pedido in enumerate(pedidos[:3], 1):  # Mostrar solo los primeros 3
            print(f"   {i}. ID: {pedido['id']} - Cliente: {pedido['cliente_nombre']} - Total: ${pedido['total']}")
        if len(pedidos) > 3:
            print(f"   ... y {len(pedidos) - 3} más")
    else:
        print("ℹ️  No hay pedidos pendientes")
    
    print("\n✅ ¡Test completado exitosamente!")
    print("\nEl POS debería poder ver estos pedidos ahora 🎉")

if __name__ == "__main__":
    main()
