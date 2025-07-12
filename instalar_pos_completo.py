#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 INSTALADOR AUTOMÁTICO CAFFE & MIGA
====================================
Este script instala la integración de pedidos en línea en tu sistema POS existente.

INSTRUCCIONES:
1. Coloca tu archivo 'cafeteria_sistema.py' en esta misma carpeta
2. Ejecuta este script: python instalar_pos_completo.py
3. Se creará una copia modificada lista para usar

NOTA: Se hará una copia de seguridad de tu archivo original
"""

import os
import shutil
from datetime import datetime

def hacer_backup(archivo_original):
    """Crear copia de seguridad"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{archivo_original}.backup_{timestamp}"
    shutil.copy2(archivo_original, backup_name)
    print(f"✅ Copia de seguridad creada: {backup_name}")
    return backup_name

def instalar_integracion():
    """Instalador principal"""
    print("🔥 INSTALADOR CAFFE & MIGA - INTEGRACIÓN POS")
    print("=" * 50)
    
    # Verificar archivo original
    archivo_pos = "cafeteria_sistema.py"
    if not os.path.exists(archivo_pos):
        print(f"❌ ERROR: No se encuentra el archivo '{archivo_pos}'")
        print(f"📍 Lugar actual: {os.getcwd()}")
        print("\n📋 INSTRUCCIONES:")
        print("1. Copia tu archivo 'cafeteria_sistema.py' a esta carpeta:")
        print(f"   {os.getcwd()}")
        print("2. Ejecuta este instalador nuevamente")
        return False
    
    print(f"✅ Archivo encontrado: {archivo_pos}")
    
    # Hacer backup
    backup_file = hacer_backup(archivo_pos)
    
    # Leer archivo original
    with open(archivo_pos, 'r', encoding='utf-8') as f:
        contenido_original = f.read()
    
    # Verificar si ya tiene integración
    if "PedidosOnlineManager" in contenido_original:
        print("⚠️ ADVERTENCIA: El archivo ya parece tener integración")
        respuesta = input("¿Reinstalar de todas formas? (s/n): ")
        if respuesta.lower() != 's':
            print("❌ Instalación cancelada")
            return False
    
    print("🔧 Aplicando integración...")
    
    # CONTENIDO A INSERTAR
    imports_nuevos = """
# 🌐 IMPORTS PARA INTEGRACIÓN WEB CAFFE & MIGA
import requests
import threading
import time
import json
from tkinter import messagebox"""
    
    clase_manager = '''

# 🌐 CLASE PARA MANEJAR PEDIDOS EN LÍNEA
class PedidosOnlineManager:
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.server_url = "http://127.0.0.1:3000"
        self.monitoring = False
        self.monitor_thread = None
        
    def test_connection(self):
        """Probar conexión con el servidor web"""
        try:
            response = requests.get(f"{self.server_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_web_orders(self):
        """Obtener pedidos web del servidor"""
        try:
            response = requests.get(f"{self.server_url}/pos/orders", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('orders', [])
            return []
        except Exception as e:
            print(f"Error obteniendo pedidos: {e}")
            return []
    
    def update_order_status(self, order_id, status):
        """Actualizar estado de un pedido"""
        try:
            response = requests.put(
                f"{self.server_url}/pos/orders/{order_id}/status",
                json={"status": status},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def process_web_order(self, order):
        """Procesar pedido web e insertarlo en la base de datos"""
        try:
            from datetime import datetime
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
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Guardar en base de datos (usando tu función existente)
            if hasattr(self.parent_app, 'guardar_ticket_sqlite'):
                self.parent_app.guardar_ticket_sqlite(
                    fecha=fecha_actual,
                    producto=productos_str,
                    cantidad=total_cantidad,
                    precio=order.get('total', 0),
                    pago='WEB-ONLINE',
                    estado='NUEVO-WEB',
                    motivo_cancelacion=f"Pedido web - {customer.get('name', 'Cliente')} - Tel: {customer.get('phone', 'N/A')}"
                )
            
            return True
        except Exception as e:
            print(f"Error procesando pedido: {e}")
            return False'''

    metodo_pedidos_online = '''
    
    def show_pedidos_online(self):
        """Nueva pantalla para manejar pedidos en línea"""
        self.clear_frames()
        frame = tk.Frame(self, bg="#F4F6F7")
        frame.pack(fill="both", expand=True)
        self.frames["pedidos_online"] = frame

        # Canvas + scrollbar
        canvas = tk.Canvas(frame, bg="#F4F6F7", highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        scrollable_frame = tk.Frame(canvas, bg="#F4F6F7")
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scrollable_frame.bind("<Configure>", on_configure)

        # Card principal
        card = tk.Frame(
            scrollable_frame,
            bg="#FFFFFF",
            bd=0,
            relief="flat",
            highlightbackground="#E67E22",
            highlightthickness=4,
            width=900
        )
        card.pack(pady=20)

        # Título
        tk.Label(
            card, 
            text="🌐 Pedidos en Línea", 
            font=("Segoe UI", 28, "bold"), 
            bg="#FFFFFF", 
            fg="#E67E22"
        ).pack(pady=20)

        # Estado de conexión
        self.estado_conexion = tk.Label(
            card,
            text="🔍 Verificando conexión...",
            font=("Segoe UI", 14),
            bg="#FFFFFF",
            fg="#E67E22"
        )
        self.estado_conexion.pack(pady=10)

        # Frame para botones de control
        control_frame = tk.Frame(card, bg="#FFFFFF")
        control_frame.pack(pady=15)

        def verificar_conexion():
            if self.pedidos_manager.test_connection():
                self.estado_conexion.config(text="✅ Conectado al servidor web", fg="#27AE60")
            else:
                self.estado_conexion.config(text="❌ Sin conexión al servidor", fg="#E74C3C")

        def actualizar_pedidos():
            verificar_conexion()
            mostrar_pedidos()

        def marcar_preparando(order_id, order_frame):
            if self.pedidos_manager.update_order_status(order_id, "preparando"):
                order_frame.config(bg="#F39C12")
                messagebox.showinfo("Estado actualizado", "Pedido marcado como 'Preparando'")
                actualizar_pedidos()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el estado")

        def marcar_listo(order_id, order_frame):
            if self.pedidos_manager.update_order_status(order_id, "listo"):
                order_frame.config(bg="#27AE60")
                messagebox.showinfo("Estado actualizado", "Pedido marcado como 'Listo'")
                actualizar_pedidos()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el estado")

        def mostrar_pedidos():
            # Limpiar pedidos anteriores
            for widget in card.winfo_children():
                if hasattr(widget, 'es_pedido'):
                    widget.destroy()

            orders = self.pedidos_manager.get_web_orders()
            
            if not orders:
                tk.Label(
                    card,
                    text="📭 No hay pedidos en línea pendientes",
                    font=("Segoe UI", 16),
                    bg="#FFFFFF",
                    fg="#7F8C8D"
                ).pack(pady=30)
                return

            for order in orders:
                # Frame del pedido
                order_frame = tk.Frame(card, bg="#ECF0F1", bd=2, relief="raised")
                order_frame.pack(fill="x", padx=20, pady=10)
                order_frame.es_pedido = True  # Marcador para limpieza

                # Color según estado
                status = order.get('status', 'nuevo')
                if status == 'preparando':
                    order_frame.config(bg="#F39C12")
                elif status == 'listo':
                    order_frame.config(bg="#27AE60")

                # Info del pedido
                customer = order.get('customer', {})
                items = order.get('items', [])
                
                info_text = f"🛍️ Pedido #{order.get('id', '')[:8]}\n"
                info_text += f"👤 Cliente: {customer.get('name', 'Sin nombre')}\n"
                info_text += f"📞 Teléfono: {customer.get('phone', 'Sin teléfono')}\n"
                info_text += f"💰 Total: ${order.get('total', 0)}\n"
                info_text += f"📋 Estado: {status.upper()}\n\n"
                info_text += "🛒 Productos:\n"
                
                for item in items:
                    info_text += f"   • {item.get('quantity', 1)}x {item.get('title', 'Producto')} - ${item.get('unit_price', 0)}\n"

                tk.Label(
                    order_frame,
                    text=info_text,
                    font=("Segoe UI", 12),
                    bg=order_frame['bg'],
                    fg="#2C3E50",
                    justify="left"
                ).pack(side="left", padx=15, pady=10)

                # Botones de acción
                buttons_frame = tk.Frame(order_frame, bg=order_frame['bg'])
                buttons_frame.pack(side="right", padx=15, pady=10)

                if status == 'nuevo':
                    tk.Button(
                        buttons_frame,
                        text="🔥 Preparando",
                        command=lambda oid=order.get('id'), of=order_frame: marcar_preparando(oid, of),
                        bg="#F39C12",
                        fg="white",
                        font=("Segoe UI", 10, "bold"),
                        width=12
                    ).pack(pady=2)

                if status in ['nuevo', 'preparando']:
                    tk.Button(
                        buttons_frame,
                        text="✅ Listo",
                        command=lambda oid=order.get('id'), of=order_frame: marcar_listo(oid, of),
                        bg="#27AE60",
                        fg="white",
                        font=("Segoe UI", 10, "bold"),
                        width=12
                    ).pack(pady=2)

        # Botones de control
        tk.Button(
            control_frame,
            text="🔄 Actualizar Pedidos",
            command=actualizar_pedidos,
            bg="#E67E22",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            width=20
        ).pack(side="left", padx=10)

        tk.Button(
            control_frame,
            text="🔙 Volver al Menú",
            command=self.show_menu,
            bg="#34495E",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            width=20
        ).pack(side="left", padx=10)

        # Cargar pedidos al iniciar
        verificar_conexion()
        mostrar_pedidos()'''
    
    # APLICAR MODIFICACIONES
    contenido_modificado = contenido_original
    
    # 1. Agregar imports
    if "import tkinter as tk" in contenido_modificado:
        contenido_modificado = contenido_modificado.replace(
            "import tkinter as tk",
            f"import tkinter as tk{imports_nuevos}"
        )
    
    # 2. Agregar clase antes de AppCafeteria
    if "class AppCafeteria" in contenido_modificado:
        contenido_modificado = contenido_modificado.replace(
            "class AppCafeteria",
            f"{clase_manager}\n\nclass AppCafeteria"
        )
    
    # 3. Agregar inicialización del manager
    if "self.promocion_frappes_activa = False" in contenido_modificado:
        contenido_modificado = contenido_modificado.replace(
            "self.promocion_frappes_activa = False",
            "self.promocion_frappes_activa = False\n        # 🌐 Inicializar manager de pedidos online\n        self.pedidos_manager = PedidosOnlineManager(self)"
        )
    
    # 4. Modificar lista de botones en show_menu
    # Buscar el patrón de botones y agregar el nuevo
    if '("Generar Compra", self.show_compra)' in contenido_modificado:
        contenido_modificado = contenido_modificado.replace(
            '("Generar Compra", self.show_compra)',
            '("Generar Compra", self.show_compra),\n        ("🌐 Pedidos en Línea", self.show_pedidos_online)'
        )
    
    # 5. Agregar método show_pedidos_online al final de la clase
    # Buscar el final de la clase (antes del if __name__)
    if 'if __name__ == "__main__":' in contenido_modificado:
        contenido_modificado = contenido_modificado.replace(
            'if __name__ == "__main__":',
            f'{metodo_pedidos_online}\n\nif __name__ == "__main__":'
        )
    else:
        # Si no hay main, agregar al final
        contenido_modificado += metodo_pedidos_online
    
    # Guardar archivo modificado
    archivo_modificado = "cafeteria_sistema_con_integracion.py"
    with open(archivo_modificado, 'w', encoding='utf-8') as f:
        f.write(contenido_modificado)
    
    print(f"✅ Integración completada!")
    print(f"📄 Archivo modificado creado: {archivo_modificado}")
    print(f"🔄 Archivo original respaldado como: {backup_file}")
    
    print("\n🚀 PRÓXIMOS PASOS:")
    print("1. Instala las dependencias: pip install requests")
    print(f"2. Ejecuta el nuevo archivo: python {archivo_modificado}")
    print("3. En el menú principal verás el nuevo botón '🌐 Pedidos en Línea'")
    print("4. ¡Ya puedes recibir pedidos de tu sitio web!")
    
    return True

if __name__ == "__main__":
    instalar_integracion()
