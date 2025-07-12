#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 🔥 SCRIPT PARA APLICAR INTEGRACIÓN AUTOMÁTICAMENTE
# Este script modifica tu cafeteria_sistema.py para agregar pedidos web

import os
import shutil
from datetime import datetime

def aplicar_integracion():
    """Aplicar modificaciones al archivo cafeteria_sistema.py"""
    
    print("🔥 APLICANDO INTEGRACIÓN CAFFE & MIGA")
    print("=" * 50)
    
    # Ruta al archivo original
    archivo_original = r"C:\Users\victo\OneDrive\Escritorio\cafeteria_sistema\cafeteria_sistema.py"
    
    # Verificar que existe
    if not os.path.exists(archivo_original):
        print(f"❌ No se encontró el archivo: {archivo_original}")
        print("🔍 Buscando en ubicaciones alternativas...")
        
        # Buscar en ubicaciones comunes
        posibles_rutas = [
            r"C:\Users\victo\Desktop\cafeteria_sistema\cafeteria_sistema.py",
            r"C:\Users\victo\OneDrive\Desktop\cafeteria_sistema\cafeteria_sistema.py",
            r"C:\Users\victo\cafeteria_sistema\cafeteria_sistema.py",
        ]
        
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                archivo_original = ruta
                print(f"✅ Encontrado en: {archivo_original}")
                break
        else:
            print("❌ No se encontró cafeteria_sistema.py")
            print("💡 Asegúrate de que esté en C:\\Users\\victo\\OneDrive\\Escritorio\\cafeteria_sistema\\")
            return False
    
    # Crear backup
    backup_path = archivo_original.replace('.py', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py')
    print(f"💾 Creando backup: {backup_path}")
    shutil.copy2(archivo_original, backup_path)
    
    # Leer archivo original
    print("📖 Leyendo archivo original...")
    with open(archivo_original, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # 1. Agregar imports
    print("📝 Agregando imports...")
    imports_nuevos = """import requests
import threading
import time
import json
"""
    
    # Buscar donde insertar imports (después de otros imports)
    if "import tkinter" in contenido:
        contenido = contenido.replace("import tkinter", imports_nuevos + "import tkinter")
    elif "import pandas" in contenido:
        contenido = contenido.replace("import pandas", imports_nuevos + "import pandas")
    else:
        # Si no encuentra, agregar al principio después del shebang
        lineas = contenido.split('\n')
        if lineas[0].startswith('#!') or lineas[0].startswith('# -*-'):
            lineas.insert(1, imports_nuevos)
        else:
            lineas.insert(0, imports_nuevos)
        contenido = '\n'.join(lineas)
    
    # 2. Agregar clase PedidosOnlineManager
    print("🏗️ Agregando clase PedidosOnlineManager...")
    
    clase_pedidos = '''

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
    
    def process_web_order_to_ticket(self, order):
        """Procesar pedido web y agregarlo como ticket"""
        try:
            customer = order.get('customer', {})
            items = order.get('items', [])
            
            # Crear descripción del pedido
            descripcion_items = []
            total_cantidad = 0
            
            for item in items:
                nombre = item.get('title', item.get('name', 'Producto'))
                cantidad = item.get('quantity', 1)
                precio = item.get('unit_price', 0)
                
                descripcion_items.append(f"{cantidad}x {nombre} (${precio})")
                total_cantidad += cantidad
            
            descripcion_completa = " | ".join(descripcion_items)
            
            # Agregar a la base de datos como ticket
            self.parent_app.agregar_ticket(
                nombre=descripcion_completa[:100],  # Limitar longitud
                cantidad=total_cantidad,
                precio=order.get('total', 0),
                pago='WEB-TARJETA',
                estado='NUEVO-WEB',
                motivo_cancelacion=f"Pedido web - {customer.get('name', 'Cliente')} - Tel: {customer.get('phone', 'N/A')}"
            )
            
            return True
        except Exception as e:
            print(f"Error procesando pedido: {e}")
            return False

'''
    
    # Buscar donde insertar la clase (antes de class AppCafeteria)
    if "class AppCafeteria" in contenido:
        contenido = contenido.replace("class AppCafeteria", clase_pedidos + "class AppCafeteria")
    else:
        # Si no encuentra, agregar antes de la última línea
        contenido = contenido + clase_pedidos
    
    # 3. Modificar __init__ para agregar pedidos_manager
    print("🔧 Modificando __init__...")
    
    # Buscar el __init__ de AppCafeteria y agregar la línea
    if "self.promocion_frappes_activa = False" in contenido:
        contenido = contenido.replace(
            "self.promocion_frappes_activa = False",
            "self.promocion_frappes_activa = False\n        self.pedidos_manager = PedidosOnlineManager(self)"
        )
    elif "__init__(self)" in contenido:
        # Buscar el final del __init__ y agregar antes del último método
        lineas = contenido.split('\n')
        for i, linea in enumerate(lineas):
            if "__init__(self)" in linea:
                # Buscar el final de este método
                j = i + 1
                while j < len(lineas) and (lineas[j].startswith('        ') or lineas[j].strip() == ''):
                    j += 1
                # Insertar antes del siguiente método
                lineas.insert(j - 1, "        self.pedidos_manager = PedidosOnlineManager(self)")
                break
        contenido = '\n'.join(lineas)
    
    # 4. Modificar show_menu para agregar botón de pedidos
    print("🎯 Modificando show_menu...")
    
    # Buscar los botones del menú y agregar el nuevo
    if 'botones = [' in contenido:
        # Encontrar la lista de botones
        inicio_botones = contenido.find('botones = [')
        if inicio_botones != -1:
            # Buscar el primer botón para insertar después
            primer_boton = contenido.find('("', inicio_botones)
            if primer_boton != -1:
                fin_primer_boton = contenido.find('),', primer_boton)
                if fin_primer_boton != -1:
                    # Insertar el nuevo botón
                    nuevo_boton = '\\n        ("🌐 Pedidos en Línea", self.show_pedidos_online),'
                    contenido = contenido[:fin_primer_boton + 2] + nuevo_boton + contenido[fin_primer_boton + 2:]
    
    # 5. Agregar método show_pedidos_online
    print("📋 Agregando método show_pedidos_online...")
    
    metodo_pedidos = '''
    def show_pedidos_online(self):
        """Mostrar pedidos web en línea"""
        # Limpiar frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Título
        tk.Label(
            self.main_frame,
            text="🌐 PEDIDOS EN LÍNEA",
            font=("Segoe UI", 24, "bold"),
            bg="#FFFFFF",
            fg="#E67E22"
        ).pack(pady=(20, 10))
        
        # Frame para contenido
        content_frame = tk.Frame(self.main_frame, bg="#FFFFFF")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Verificar conexión
        if not self.pedidos_manager.test_connection():
            tk.Label(
                content_frame,
                text="❌ No se puede conectar al servidor web\\n\\nAsegúrate de que main.py esté ejecutándose",
                font=("Segoe UI", 14),
                bg="#FFFFFF",
                fg="#E74C3C",
                justify="center"
            ).pack(pady=50)
            
            tk.Button(
                content_frame,
                text="🔄 Reintentar",
                command=self.show_pedidos_online,
                font=("Segoe UI", 12, "bold"),
                bg="#3498DB",
                fg="white",
                relief="flat",
                padx=20,
                pady=10
            ).pack(pady=10)
            
            tk.Button(
                content_frame,
                text="⬅️ Volver al Menú",
                command=self.show_menu,
                font=("Segoe UI", 12),
                bg="#95A5A6",
                fg="white",
                relief="flat",
                padx=20,
                pady=8
            ).pack(pady=5)
            return
        
        # Obtener pedidos
        orders = self.pedidos_manager.get_web_orders()
        
        if not orders:
            tk.Label(
                content_frame,
                text="📭 No hay pedidos web pendientes\\n\\nLos pedidos aparecerán aquí automáticamente",
                font=("Segoe UI", 14),
                bg="#FFFFFF",
                fg="#7F8C8D",
                justify="center"
            ).pack(pady=50)
        else:
            tk.Label(
                content_frame,
                text=f"📦 {len(orders)} pedidos encontrados",
                font=("Segoe UI", 14, "bold"),
                bg="#FFFFFF",
                fg="#27AE60"
            ).pack(pady=(0, 20))
            
            # Scroll frame para pedidos
            canvas = tk.Canvas(content_frame, bg="#FFFFFF")
            scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#FFFFFF")
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Mostrar cada pedido
            for i, order in enumerate(orders):
                self.create_order_widget(scrollable_frame, order, i)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
        
        # Botones de acción
        button_frame = tk.Frame(content_frame, bg="#FFFFFF")
        button_frame.pack(fill="x", pady=(20, 0))
        
        tk.Button(
            button_frame,
            text="🔄 Actualizar",
            command=self.show_pedidos_online,
            font=("Segoe UI", 12, "bold"),
            bg="#3498DB",
            fg="white",
            relief="flat",
            padx=20,
            pady=8
        ).pack(side="left", padx=(0, 10))
        
        tk.Button(
            button_frame,
            text="⬅️ Volver al Menú",
            command=self.show_menu,
            font=("Segoe UI", 12),
            bg="#95A5A6",
            fg="white",
            relief="flat",
            padx=20,
            pady=8
        ).pack(side="right")
    
    def create_order_widget(self, parent, order, index):
        """Crear widget para mostrar un pedido"""
        # Frame principal del pedido
        order_frame = tk.Frame(parent, bg="#ECF0F1", relief="solid", bd=1)
        order_frame.pack(fill="x", pady=5, padx=10)
        
        # Información del cliente
        customer = order.get('customer', {})
        
        # Header con cliente y estado
        header_frame = tk.Frame(order_frame, bg="#34495E")
        header_frame.pack(fill="x")
        
        tk.Label(
            header_frame,
            text=f"👤 {customer.get('name', 'Cliente')} | 📱 {customer.get('phone', 'N/A')}",
            font=("Segoe UI", 12, "bold"),
            bg="#34495E",
            fg="white"
        ).pack(side="left", padx=10, pady=5)
        
        status = order.get('status', 'listo_para_preparar')
        status_color = {"listo_para_preparar": "#F39C12", "preparando": "#E67E22", "listo": "#27AE60"}.get(status, "#95A5A6")
        status_text = {"listo_para_preparar": "📋 Listo para preparar", "preparando": "🔄 Preparando", "listo": "✅ Listo"}.get(status, status)
        
        tk.Label(
            header_frame,
            text=status_text,
            font=("Segoe UI", 10, "bold"),
            bg=status_color,
            fg="white",
            padx=10,
            pady=2
        ).pack(side="right", padx=10, pady=5)
        
        # Información del pedido
        info_frame = tk.Frame(order_frame, bg="#ECF0F1")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        # Items
        items = order.get('items', [])
        items_text = "\\n".join([f"• {item.get('quantity', 1)}x {item.get('title', 'Producto')} - ${item.get('unit_price', 0)}" for item in items])
        
        tk.Label(
            info_frame,
            text=f"📝 PEDIDO:\\n{items_text}",
            font=("Segoe UI", 10),
            bg="#ECF0F1",
            fg="#2C3E50",
            justify="left",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        # Total y fecha
        tk.Label(
            info_frame,
            text=f"💰 Total: ${order.get('total', 0)} | 📅 {order.get('created_at', 'N/A')}",
            font=("Segoe UI", 10, "bold"),
            bg="#ECF0F1",
            fg="#E74C3C"
        ).pack(fill="x")
        
        # Botones de acción
        if status != "listo":
            button_frame = tk.Frame(order_frame, bg="#ECF0F1")
            button_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            if status == "listo_para_preparar":
                tk.Button(
                    button_frame,
                    text="🔄 Marcar como Preparando",
                    command=lambda: self.update_order_status_and_refresh(order.get('id'), 'preparando'),
                    font=("Segoe UI", 9, "bold"),
                    bg="#E67E22",
                    fg="white",
                    relief="flat",
                    padx=15,
                    pady=5
                ).pack(side="left", padx=(0, 5))
            
            elif status == "preparando":
                tk.Button(
                    button_frame,
                    text="✅ Marcar como Listo",
                    command=lambda: self.update_order_status_and_refresh(order.get('id'), 'listo'),
                    font=("Segoe UI", 9, "bold"),
                    bg="#27AE60",
                    fg="white",
                    relief="flat",
                    padx=15,
                    pady=5
                ).pack(side="left", padx=(0, 5))
            
            # Botón para agregar a tickets
            tk.Button(
                button_frame,
                text="📋 Agregar a Tickets",
                command=lambda: self.add_web_order_to_tickets(order),
                font=("Segoe UI", 9),
                bg="#3498DB",
                fg="white",
                relief="flat",
                padx=15,
                pady=5
            ).pack(side="right")
    
    def update_order_status_and_refresh(self, order_id, new_status):
        """Actualizar estado del pedido y refrescar vista"""
        if self.pedidos_manager.update_order_status(order_id, new_status):
            self.show_pedidos_online()  # Refrescar la vista
        else:
            tk.messagebox.showerror("Error", "No se pudo actualizar el estado del pedido")
    
    def add_web_order_to_tickets(self, order):
        """Agregar pedido web a la base de datos de tickets"""
        if self.pedidos_manager.process_web_order_to_ticket(order):
            tk.messagebox.showinfo("Éxito", "Pedido agregado a tickets exitosamente")
        else:
            tk.messagebox.showerror("Error", "No se pudo agregar el pedido a tickets")
'''
    
    # Buscar donde insertar el método (antes del final de la clase AppCafeteria)
    if "if __name__ == '__main__':" in contenido:
        contenido = contenido.replace("if __name__ == '__main__':", metodo_pedidos + "\\n\\nif __name__ == '__main__':")
    else:
        contenido = contenido + metodo_pedidos
    
    # Guardar archivo modificado
    print("💾 Guardando archivo modificado...")
    with open(archivo_original, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("\\n🎉 ¡INTEGRACIÓN APLICADA EXITOSAMENTE!")
    print("=" * 50)
    print("✅ Imports agregados")
    print("✅ Clase PedidosOnlineManager agregada")
    print("✅ Método __init__ modificado")
    print("✅ Botón 'Pedidos en Línea' agregado al menú")
    print("✅ Método show_pedidos_online agregado")
    print(f"💾 Backup creado: {os.path.basename(backup_path)}")
    
    print("\\n🚀 PRÓXIMOS PASOS:")
    print("1. Ejecuta tu cafeteria_sistema.py")
    print("2. Verás el botón '🌐 Pedidos en Línea' en el menú")
    print("3. ¡Los pedidos web aparecerán automáticamente!")
    
    return True

if __name__ == "__main__":
    aplicar_integracion()
