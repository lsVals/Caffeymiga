# Script de instalación para tu sistema cafeteria_sistema
# Ejecutar desde: C:\Users\victo\OneDrive\Escritorio\cafeteria_sistema\

import os
import shutil
import sqlite3

def instalar_integracion_caffe_miga():
    """Instalar integración de Caffe & Miga en tu sistema"""
    
    print("🔥 Instalando integración Caffe & Miga...")
    print("=" * 50)
    
    # 1. Verificar que estamos en la carpeta correcta
    carpeta_actual = os.getcwd()
    if not carpeta_actual.endswith("cafeteria_sistema"):
        print("⚠️ ADVERTENCIA: Ejecuta este script desde la carpeta 'cafeteria_sistema'")
        print(f"Carpeta actual: {carpeta_actual}")
        respuesta = input("¿Continuar de todas formas? (s/n): ")
        if respuesta.lower() != 's':
            return
    
    # 2. Crear carpeta de integración
    carpeta_integracion = "caffe_miga_integration"
    if not os.path.exists(carpeta_integracion):
        os.makedirs(carpeta_integracion)
        print(f"✅ Carpeta creada: {carpeta_integracion}")
    
    # 3. Copiar archivo de integración
    archivo_integracion = """
# ARCHIVO COPIADO AUTOMÁTICAMENTE - Integración Caffe & Miga
# Este archivo conecta tu sistema con el e-commerce

import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import requests
import json
import threading
import time
from datetime import datetime

class CaffeYMigaIntegration:
    def __init__(self, master=None):
        self.master = master
        self.server_url = "http://127.0.0.1:3000"
        
        # CONFIGURACIÓN - AJUSTA ESTOS VALORES
        self.mi_base_datos = "cafeteria.db"  # ← CAMBIA POR TU BD
        self.tabla_pedidos = "pedidos"       # ← CAMBIA POR TU TABLA
        
        self.is_running = False
    
    def obtener_pedidos_nuevos(self):
        try:
            response = requests.get(f"{self.server_url}/pos/orders", timeout=10)
            if response.status_code == 200:
                return response.json().get('orders', [])
            return []
        except:
            return []
    
    def insertar_pedido_en_mi_bd(self, pedido):
        try:
            customer = pedido.get('customer', {})
            items = pedido.get('items', [])
            
            conn = sqlite3.connect(self.mi_base_datos)
            cursor = conn.cursor()
            
            # AJUSTA ESTA QUERY SEGÚN TU TABLA
            cursor.execute('''
                INSERT INTO pedidos (
                    id_externo, cliente, telefono, total, items, estado, fecha, origen
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pedido['id'],
                customer.get('name', 'Cliente Web'),
                customer.get('phone', ''),
                pedido.get('total', 0),
                json.dumps(items),
                'nuevo',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'web'
            ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Pedido agregado: {customer.get('name', 'Cliente')} - ${pedido.get('total', 0)}")
            
            # Mostrar notificación
            if self.master:
                messagebox.showinfo("🔥 Nuevo Pedido Web", 
                    f"Cliente: {customer.get('name', 'Cliente')}\\n"
                    f"Total: ${pedido.get('total', 0):.2f}\\n"
                    f"¡Revisar sistema!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error insertando pedido: {e}")
            return False
    
    def marcar_como_procesado(self, firebase_id):
        try:
            requests.put(f"{self.server_url}/pos/orders/{firebase_id}/status",
                        json={"status": "preparando"}, timeout=10)
            return True
        except:
            return False
    
    def sincronizar(self):
        print("🔄 Sincronizando pedidos...")
        pedidos = self.obtener_pedidos_nuevos()
        
        if not pedidos:
            print("📭 No hay pedidos nuevos")
            return
        
        for pedido in pedidos:
            if self.insertar_pedido_en_mi_bd(pedido):
                self.marcar_como_procesado(pedido['id'])
        
        print(f"✅ {len(pedidos)} pedidos procesados")
    
    def iniciar_monitoreo(self, intervalo=30):
        if self.is_running:
            return
            
        self.is_running = True
        
        def monitor():
            while self.is_running:
                try:
                    self.sincronizar()
                    time.sleep(intervalo)
                except:
                    time.sleep(intervalo)
        
        threading.Thread(target=monitor, daemon=True).start()
        print(f"🔄 Monitoreo iniciado cada {intervalo} segundos")
    
    def detener_monitoreo(self):
        self.is_running = False
        print("🛑 Monitoreo detenido")

# FUNCIONES PARA INTEGRAR EN TU SISTEMA EXISTENTE

def agregar_a_tu_menu(menu_principal, ventana_principal):
    '''Agregar a tu menú principal'''
    integration = CaffeYMigaIntegration(ventana_principal)
    
    caffe_menu = tk.Menu(menu_principal, tearoff=0)
    menu_principal.add_cascade(label="🔥 Pedidos Web", menu=caffe_menu)
    
    caffe_menu.add_command(label="Sincronizar", command=integration.sincronizar)
    caffe_menu.add_command(label="Iniciar Monitor", 
                          command=lambda: integration.iniciar_monitoreo(30))
    caffe_menu.add_command(label="Detener Monitor", 
                          command=integration.detener_monitoreo)

def agregar_boton_a_tu_ventana(parent_frame, ventana_principal):
    '''Agregar botón a tu ventana'''
    integration = CaffeYMigaIntegration(ventana_principal)
    
    btn = ttk.Button(parent_frame, text="🔥 Sincronizar Pedidos Web",
                    command=integration.sincronizar)
    btn.pack(pady=5)
    
    return integration

if __name__ == "__main__":
    # Prueba independiente
    root = tk.Tk()
    root.title("Integración Caffe & Miga")
    
    integration = CaffeYMigaIntegration(root)
    
    ttk.Button(root, text="Sincronizar Ahora", 
              command=integration.sincronizar).pack(pady=20)
    
    root.mainloop()
"""
    
    # Guardar archivo
    with open(f"{carpeta_integracion}/caffe_miga_integration.py", "w", encoding="utf-8") as f:
        f.write(archivo_integracion)
    
    print(f"✅ Archivo creado: {carpeta_integracion}/caffe_miga_integration.py")
    
    # 4. Crear archivo de configuración
    config_content = '''
# Configuración para tu sistema cafeteria_sistema

# 1. AJUSTA ESTOS VALORES SEGÚN TU BASE DE DATOS:
MI_BD_CONFIG = {
    "archivo": "cafeteria.db",     # ← Nombre de tu archivo .db
    "tabla": "pedidos",            # ← Nombre de tu tabla de pedidos
    "columnas": {
        "id_externo": "id_externo",
        "cliente": "cliente", 
        "telefono": "telefono",
        "total": "total",
        "items": "items",
        "estado": "estado",
        "fecha": "fecha"
    }
}

# 2. CONFIGURACIÓN DEL SERVIDOR
SERVIDOR = {
    "url": "http://127.0.0.1:3000",
    "intervalo_sync": 30  # segundos
}

# 3. PARA USAR EN TU CÓDIGO PRINCIPAL:
"""
# En tu archivo principal .py, agregar:

from caffe_miga_integration.caffe_miga_integration import agregar_a_tu_menu

# En tu función donde creas el menú:
agregar_a_tu_menu(tu_menu_principal, tu_ventana_principal)

# O si prefieres un botón:
from caffe_miga_integration.caffe_miga_integration import agregar_boton_a_tu_ventana

# En tu ventana principal:
integration = agregar_boton_a_tu_ventana(tu_frame_principal, tu_ventana)
"""
'''
    
    with open(f"{carpeta_integracion}/config.py", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print(f"✅ Configuración creada: {carpeta_integracion}/config.py")
    
    # 5. Crear script de prueba
    test_script = '''
# Script de prueba - Ejecutar para verificar integración

import sys
import os
sys.path.append(os.path.dirname(__file__))

from caffe_miga_integration import CaffeYMigaIntegration

def probar_integracion():
    print("🔥 Probando integración Caffe & Miga...")
    
    integration = CaffeYMigaIntegration()
    
    # Probar conexión
    try:
        import requests
        response = requests.get("http://127.0.0.1:3000/pos/dashboard", timeout=5)
        if response.status_code == 200:
            print("✅ Conexión al servidor exitosa")
        else:
            print("❌ Servidor no responde correctamente")
            return
    except:
        print("❌ No se puede conectar al servidor")
        print("   Asegúrate de que el servidor esté ejecutándose en puerto 3000")
        return
    
    # Probar sincronización
    integration.sincronizar()
    
    print("✅ Prueba completada")

if __name__ == "__main__":
    probar_integracion()
'''
    
    with open(f"{carpeta_integracion}/probar_integracion.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print(f"✅ Script de prueba: {carpeta_integracion}/probar_integracion.py")
    
    # 6. Verificar dependencias
    print("\n📦 Verificando dependencias...")
    try:
        import requests
        print("✅ requests disponible")
    except ImportError:
        print("❌ Instalar requests: pip install requests")
    
    try:
        import tkinter
        print("✅ tkinter disponible")
    except ImportError:
        print("❌ tkinter no disponible")
    
    # 7. Instrucciones finales
    print("\n" + "=" * 50)
    print("🎉 ¡INSTALACIÓN COMPLETADA!")
    print("=" * 50)
    print(f"📁 Archivos creados en: {carpeta_integracion}/")
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Edita config.py con los datos de tu base de datos")
    print("2. Ejecuta: python probar_integracion.py")
    print("3. Integra en tu código principal:")
    print("   from caffe_miga_integration.caffe_miga_integration import agregar_a_tu_menu")
    print("\n🔥 ¡Tu sistema ahora puede recibir pedidos del e-commerce!")

if __name__ == "__main__":
    instalar_integracion_caffe_miga()
