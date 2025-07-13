#!/usr/bin/env python3
# Test directo del PedidosWebManager en el contexto del POS

import sys
import os

# Cambiar al directorio del POS
os.chdir("cafeteria_sistema")

# Importar el POS
sys.path.append('.')
from cafeteria_sistema import PedidosWebManager

def test_pedidos_web_manager():
    print("🔍 TEST DIRECTO DEL PEDIDOSWEBMANAGER")
    print("=" * 60)
    
    # Crear instancia del manager como lo hace el POS
    manager = PedidosWebManager()
    
    print(f"📂 Directorio actual: {os.getcwd()}")
    print(f"🔗 Ruta BD configurada: {manager.db_path}")
    print(f"📋 ¿BD existe? {os.path.exists(manager.db_path)}")
    
    # Test de conexión
    print("\n1. 🔌 TEST DE CONEXIÓN:")
    connection_ok = manager.test_connection()
    print(f"   Resultado: {'✅ OK' if connection_ok else '❌ FALLÓ'}")
    
    if not connection_ok:
        print("❌ CONEXIÓN FALLÓ - El POS mostraría error de conexión")
        return
    
    # Test de obtener pedidos
    print("\n2. 📋 OBTENIENDO PEDIDOS:")
    pedidos = manager.get_web_orders()
    print(f"   Cantidad obtenida: {len(pedidos)}")
    
    if pedidos:
        print("\n3. 🎯 PEDIDOS ENCONTRADOS:")
        for i, pedido in enumerate(pedidos, 1):
            print(f"   PEDIDO #{i}:")
            print(f"   🆔 ID: {pedido['id']}")
            print(f"   👤 Cliente: {pedido['cliente_nombre']}")
            print(f"   💰 Total: ${pedido['total']}")
            print(f"   📦 Estado: {pedido['estado']}")
            print()
    else:
        print("   ⚠️ NO SE ENCONTRARON PEDIDOS")
        print("   Esto haría que el POS muestre 'NO HAY PEDIDOS PENDIENTES'")
    
    print("=" * 60)
    print(f"✅ RESULTADO: PedidosWebManager debería devolver {len(pedidos)} pedidos al POS")
    
    return len(pedidos)

if __name__ == "__main__":
    test_pedidos_web_manager()
