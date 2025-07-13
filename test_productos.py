#!/usr/bin/env python3
# Test del nuevo formato de productos

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sincronizacion_automatica import SincronizadorAutomatico

# Crear instancia del sincronizador para probar la función
sync = SincronizadorAutomatico()

# Ejemplos de nombres de productos que llegan del sistema
productos_test = [
    "2x100 Frappes - Cualquier Sabor (Moka + Taro) - Moka: Deslactosada, Taro: Deslactosada (Moka + Taro)",
    "Frappé Moka (Leche: Deslactosada)",
    "Capuchino (Leche: Entera)",
    "Latte Matcha (Leche: Deslactosada Light)",
    "Coca Cola 355ml",
    "Waffles",
    "Carterita"
]

print("🎨 NUEVO FORMATO DE PRODUCTOS EN EL POS")
print("=" * 50)

for i, producto in enumerate(productos_test, 1):
    producto_formateado = sync._formatear_nombre_producto(producto)
    print(f"{i}. ANTES: {producto}")
    print(f"   DESPUÉS: {producto_formateado}")
    print()

print("✅ ¡Los productos ahora se verán mucho más claros en el POS!")
