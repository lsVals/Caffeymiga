#!/usr/bin/env python3
"""
Script para probar todos los métodos de pago de Caffe & Miga
"""

import requests
import json

def test_efectivo():
    """Probar pago en efectivo"""
    print("💵 Probando pago en efectivo...")
    
    test_data = {
        "items": [
            {
                "id": "test_cafe",
                "title": "Café Americano",
                "quantity": 1,
                "unit_price": 25.0,
                "description": "Café de prueba"
            }
        ],
        "payer": {
            "name": "Test Efectivo",
            "phone": {
                "area_code": "502",
                "number": "12345678"
            },
            "email": "test@efectivo.com"
        },
        "payment_method": "efectivo",
        "metadata": {
            "pickup_time": "14:00",
            "source": "web_test"
        },
        "notes": "Pedido de prueba - efectivo"
    }
    
    try:
        response = requests.post(
            "http://localhost:3000/pos/orders",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Pago en efectivo: FUNCIONANDO")
            result = response.json()
            print(f"   Order ID: {result.get('order_id', 'N/A')}")
            return True
        else:
            print(f"❌ Pago en efectivo: ERROR {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en efectivo: {e}")
        return False

def test_terminal():
    """Probar pago con terminal"""
    print("💳 Probando pago con terminal...")
    
    test_data = {
        "items": [
            {
                "id": "test_cafe",
                "title": "Café Latte", 
                "quantity": 1,
                "unit_price": 35.0,
                "description": "Latte de prueba"
            }
        ],
        "payer": {
            "name": "Test Terminal",
            "phone": {
                "area_code": "502", 
                "number": "87654321"
            },
            "email": "test@terminal.com"
        },
        "payment_method": "terminal",
        "metadata": {
            "pickup_time": "15:00",
            "source": "web_test"
        },
        "notes": "Pedido de prueba - terminal"
    }
    
    try:
        response = requests.post(
            "http://localhost:3000/pos/orders",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Pago con terminal: FUNCIONANDO")
            result = response.json()
            print(f"   Order ID: {result.get('order_id', 'N/A')}")
            return True
        else:
            print(f"❌ Pago con terminal: ERROR {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en terminal: {e}")
        return False

def test_mercadopago():
    """Probar pago con Mercado Pago"""
    print("🛒 Probando pago con Mercado Pago...")
    
    test_data = {
        "items": [
            {
                "id": "test_frappe",
                "title": "Frappé de Chocolate",
                "quantity": 1,
                "unit_price": 45.0,
                "description": "Frappé de prueba",
                "currency_id": "MXN",
                "category_id": "food"
            }
        ],
        "payer": {
            "name": "Test MercadoPago",
            "surname": "Usuario",
            "email": "test@mercadopago.com",
            "phone": {
                "area_code": "502",
                "number": "11223344"
            },
            "identification": {
                "type": "DNI",
                "number": "12345678"
            },
            "address": {
                "street_name": "Test Street",
                "street_number": 123,
                "zip_code": "01001"
            }
        },
        "back_urls": {
            "success": "http://localhost:3000/success.html",
            "failure": "http://localhost:3000/failure.html", 
            "pending": "http://localhost:3000/pending.html"
        },
        "auto_return": "approved",
        "notification_url": "http://localhost:3000/webhook",
        "metadata": {
            "pickup_time": "16:00",
            "customer_phone": "11223344"
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:3000/create_preference",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Mercado Pago: FUNCIONANDO")
            result = response.json()
            print(f"   Preference ID: {result.get('id', 'N/A')}")
            print(f"   Init Point: {result.get('init_point', 'N/A')[:50]}...")
            return True
        else:
            print(f"❌ Mercado Pago: ERROR {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en Mercado Pago: {e}")
        return False

def test_servidor():
    """Verificar que el servidor esté funcionando"""
    print("🌐 Verificando servidor...")
    
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor: FUNCIONANDO")
            return True
        else:
            print(f"❌ Servidor: ERROR {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error del servidor: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test de Métodos de Pago - Caffe & Miga")
    print("=" * 50)
    
    # Test del servidor
    if not test_servidor():
        print("\n❌ El servidor no está funcionando. Ejecuta 'python main.py' primero.")
        exit(1)
    
    print()
    
    # Test de cada método
    efectivo_ok = test_efectivo()
    print()
    
    terminal_ok = test_terminal()
    print()
    
    mercadopago_ok = test_mercadopago()
    print()
    
    # Resumen
    print("📊 RESUMEN DE PRUEBAS:")
    print("=" * 30)
    print(f"💵 Efectivo:      {'✅ OK' if efectivo_ok else '❌ FALLA'}")
    print(f"💳 Terminal:      {'✅ OK' if terminal_ok else '❌ FALLA'}")
    print(f"🛒 Mercado Pago:  {'✅ OK' if mercadopago_ok else '❌ FALLA'}")
    
    if efectivo_ok and terminal_ok and mercadopago_ok:
        print("\n🎉 ¡Todos los métodos de pago funcionan correctamente!")
    else:
        print("\n⚠️ Algunos métodos de pago tienen problemas.")
        print("💡 Revisa los logs del servidor para más detalles.")
