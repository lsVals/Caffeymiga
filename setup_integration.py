#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 GUÍA DE INTEGRACIÓN CAFFE & MIGA
===================================

Esta guía te ayudará a integrar el sistema de pedidos web con tu POS existente.

PASOS PARA LA INTEGRACIÓN:
"""

print("🚀 CAFFE & MIGA - ASISTENTE DE INTEGRACIÓN")
print("=" * 50)

print("\n📋 ESTADO ACTUAL:")
print("✅ E-commerce web funcionando")
print("✅ Pagos con Mercado Pago activos")
print("✅ Firebase conectado y guardando pedidos")
print("✅ GitHub repository desplegado")

print("\n🔧 OPCIONES DE INTEGRACIÓN:")
print("\n1️⃣ USAR SISTEMA POS COMPLETO (Recomendado)")
print("   - Sistema completo desarrollado para ti")
print("   - Interfaz gráfica moderna")
print("   - No requiere modificar tu sistema existente")
print("   - Comando: cd pos_integration && python caffe_miga_tkinter.py")

print("\n2️⃣ INTEGRAR CON TU SISTEMA EXISTENTE")
print("   - Necesitas tu archivo de sistema POS actual")
print("   - Copiarlo a esta carpeta")
print("   - Ejecutar instalador automático")

print("\n3️⃣ API PARA CONECTAR CUALQUIER SISTEMA")
print("   - Tu sistema actual puede consultar:")
print("   - GET http://localhost:3000/pos/orders")
print("   - Obtiene pedidos en tiempo real")

print("\n🌟 CONFIRMACIÓN DE FUNCIONAMIENTO:")
print("- Pedidos web → Mercado Pago → Firebase → POS")
print("- Sistema completamente operativo")

print("\n📞 ¿QUÉ OPCIÓN PREFIERES?")
print("Escribe el número (1, 2 o 3) y presiona Enter:")

try:
    opcion = input().strip()
    
    if opcion == "1":
        print("\n✅ OPCIÓN 1 SELECCIONADA")
        print("🚀 Ejecutando sistema POS completo...")
        import subprocess
        subprocess.run(["python", "pos_integration/caffe_miga_tkinter.py"])
        
    elif opcion == "2":
        print("\n✅ OPCIÓN 2 SELECCIONADA")
        print("📋 INSTRUCCIONES:")
        print("1. Copia tu archivo de sistema POS a esta carpeta")
        print("2. Asegúrate que se llame 'cafeteria_sistema.py'")
        print("3. Ejecuta: python instalar_pos_completo.py")
        
    elif opcion == "3":
        print("\n✅ OPCIÓN 3 SELECCIONADA")
        print("🔗 API ENDPOINTS DISPONIBLES:")
        print("- GET  http://localhost:3000/pos/orders")
        print("- POST http://localhost:3000/pos/orders")
        print("📖 Documentación completa en README.md")
        
    else:
        print("❌ Opción no válida. Ejecuta el script nuevamente.")
        
except KeyboardInterrupt:
    print("\n\n👋 ¡Integración pausada! Ejecuta este script cuando estés listo.")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 50)
print("🎉 ¡SISTEMA CAFFE & MIGA LISTO!")
print("📞 Soporte: Ejecuta este script para más opciones")
