#!/usr/bin/env python3
"""
Script para probar el envío de datos del cliente al servidor
Simula exactamente lo que hace la página web
"""
import requests
import json
import time

# URL del servidor
SERVER_URL = "https://caffeymiga-1.onrender.com"

def test_customer_data():
    """Probar envío de datos del cliente"""
    
    # Datos de prueba que simula lo que envía script.js
    test_data = {
        "items": [
            {
                "id": "frappe_test",
                "title": "Frappe de Prueba",
                "quantity": 1,
                "unit_price": 100,
                "description": "Frappe test - Hora recogida: 10:00"
            }
        ],
        "payer": {
            "name": "VICTOR PRUEBA SCRIPT",
            "phone": {
                "area_code": "52",
                "number": "55-1234-5678"
            },
            "email": "55-1234-5678@caffeymiga.com"
        },
        "payment_method": "efectivo",
        "notes": "Hora de recogida: 10:00. Total: $100. Método: Efectivo en sucursal",
        "metadata": {
            "pickup_time": "10:00",
            "source": "web_ecommerce",
            "payment_method": "efectivo",
            "requires_payment": False
        }
    }
    
    print("🔥 PRUEBA DE DATOS DEL CLIENTE")
    print("=" * 50)
    print(f"📡 Enviando a: {SERVER_URL}/pos/orders")
    print(f"📦 Datos enviados:")
    print(json.dumps(test_data, indent=2))
    print("=" * 50)
    
    try:
        # Enviar request exactly como lo hace script.js
        response = requests.post(
            f"{SERVER_URL}/pos/orders",
            headers={
                'Content-Type': 'application/json',
            },
            json=test_data,
            timeout=30
        )
        
        print(f"📊 RESPUESTA DEL SERVIDOR:")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ ÉXITO: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ ERROR: {response.text}")
            
    except Exception as e:
        print(f"💥 EXCEPCIÓN: {e}")

def test_direct_server():
    """Probar conexión directa al servidor"""
    print("\n🔍 PROBANDO CONEXIÓN AL SERVIDOR...")
    
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=10)
        print(f"✅ Servidor respondiendo: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    test_direct_server()
    time.sleep(2)
    test_customer_data()
