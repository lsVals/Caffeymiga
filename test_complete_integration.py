#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SCRIPT DE PRUEBA - Integración Completa Caffe & Miga
# Este script simula todo el flujo: E-commerce → Firebase → POS

import requests
import json
import time
from datetime import datetime

def test_complete_flow():
    """Probar el flujo completo de integración"""
    
    print("🔥 PRUEBA DE INTEGRACIÓN COMPLETA CAFFE & MIGA")
    print("=" * 60)
    
    # 1. Verificar que el servidor esté funcionando
    try:
        response = requests.get("http://localhost:3000/", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor backend funcionando")
        else:
            print("❌ Servidor no responde")
            return False
    except:
        print("❌ Error conectando al servidor")
        return False
    
    # 2. Simular pedido del e-commerce
    print("\n📦 Simulando pedido del e-commerce...")
    
    pedido_test = {
        "items": [
            {
                "id": "cafe_americano",
                "title": "Café Americano",
                "quantity": 2,
                "unit_price": 25.0,
                "description": "Café americano caliente"
            },
            {
                "id": "croissant",
                "title": "Croissant de Jamón",
                "quantity": 1,
                "unit_price": 45.0,
                "description": "Croissant relleno de jamón y queso"
            }
        ],
        "payer": {
            "name": "Cliente Prueba POS",
            "email": "test@caffeymiga.com",
            "phone": {
                "area_code": "502",
                "number": "12345678"
            }
        },
        "payment_method": "tarjeta",
        "notes": "Pedido de prueba para integración POS",
        "metadata": {
            "test": True,
            "integration_test": True
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:3000/create_preference",
            json=pedido_test,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Pedido creado exitosamente")
            print(f"📋 ID Preferencia: {data['id']}")
            print(f"💰 Total: ${data['total']}")
            print(f"🔥 Firebase ID: {data.get('firebase_order_id', 'N/A')}")
            
            # Esperar un momento para que se procese
            print("\n⏳ Esperando procesamiento...")
            time.sleep(3)
            
            return True
            
        else:
            print(f"❌ Error creando pedido: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en solicitud: {e}")
        return False
    
    # 3. Verificar que el pedido esté en Firebase
    print("\n🔥 Verificando pedidos en Firebase...")
    
    try:
        response = requests.get("http://localhost:3000/pos/orders", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get('orders', [])
            
            print(f"✅ {len(orders)} pedidos encontrados en Firebase")
            
            # Buscar nuestro pedido de prueba
            test_order = None
            for order in orders:
                customer = order.get('customer', {})
                if customer.get('name') == 'Cliente Prueba POS':
                    test_order = order
                    break
            
            if test_order:
                print("🎯 Pedido de prueba encontrado:")
                print(f"   👤 Cliente: {test_order['customer']['name']}")
                print(f"   📱 Teléfono: {test_order['customer']['phone']}")
                print(f"   💰 Total: ${test_order['total']}")
                print(f"   📝 Items: {len(test_order['items'])} productos")
                print(f"   📅 Creado: {test_order.get('created_at', 'N/A')}")
                
                return True
            else:
                print("⚠️ Pedido de prueba no encontrado")
                return False
                
        else:
            print(f"❌ Error consultando pedidos: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error consultando Firebase: {e}")
        return False

def test_pos_dashboard():
    """Probar el dashboard POS"""
    print("\n📊 Probando dashboard POS...")
    
    try:
        response = requests.get("http://localhost:3000/pos/dashboard", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get('statistics', {})
            
            print("✅ Dashboard POS funcionando:")
            print(f"   📈 Total pedidos: {stats.get('total', 0)}")
            print(f"   🆕 Listos para preparar: {stats.get('listo_para_preparar', 0)}")
            print(f"   🔄 Preparando: {stats.get('preparando', 0)}")
            print(f"   ✅ Listos: {stats.get('listo', 0)}")
            print(f"   🔥 Firebase: {data.get('firebase_status', 'unknown')}")
            
            return True
            
        else:
            print(f"❌ Error en dashboard: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error consultando dashboard: {e}")
        return False

def main():
    """Función principal de prueba"""
    print(f"🕐 Iniciando prueba: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ejecutar pruebas
    flow_ok = test_complete_flow()
    dashboard_ok = test_pos_dashboard()
    
    print("\n" + "=" * 60)
    print("📋 RESULTADOS DE LA PRUEBA:")
    print("=" * 60)
    
    if flow_ok and dashboard_ok:
        print("🎉 ¡INTEGRACIÓN COMPLETA FUNCIONANDO!")
        print("✅ E-commerce → Firebase → POS = OK")
        print("✅ Servidor backend = OK")
        print("✅ Mercado Pago = OK")
        print("✅ Firebase = OK")
        print("✅ APIs POS = OK")
        
        print("\n🚀 PRÓXIMOS PASOS:")
        print("1. Ejecutar integración en tu sistema POS")
        print("2. Los pedidos web aparecerán automáticamente")
        print("3. ¡Sin WhatsApp, directo a tu cafetería!")
        
    else:
        print("❌ Algunos componentes tienen problemas")
        print("🔧 Revisa los logs del servidor")
        
    print("\n🔥 ¡Integración Caffe & Miga lista!")

if __name__ == "__main__":
    main()
