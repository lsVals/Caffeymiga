# INTEGRACIÓN PEDIDOS EN LÍNEA PARA CAFETERIA_SISTEMA.PY
# Agrega estas líneas al inicio de tu archivo, después de los imports existentes

import requests
import threading
import time
import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime

# Agrega esta función si no existe en tu archivo o impórtala si está en otro módulo
def guardar_ticket_sqlite(fecha, producto, cantidad, precio, pago, estado, motivo_cancelacion):
    # Implementa aquí la lógica para guardar el ticket en la base de datos SQLite
    # Por ejemplo:
    # import sqlite3
    # conn = sqlite3.connect('cafeteria.db')
    # cursor = conn.cursor()
    # cursor.execute("INSERT INTO tickets (fecha, producto, cantidad, precio, pago, estado, motivo_cancelacion) VALUES (?, ?, ?, ?, ?, ?, ?)", (fecha, producto, cantidad, precio, pago, estado, motivo_cancelacion))
    # conn.commit()
    # conn.close()
    pass

# Nueva clase para manejar pedidos web
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
            customer = order.get('customer', {})
            items = order.get('items', [])
            
            # Crear descripción de productos
            productos_desc = []
            total_cantidad = 0
            for item in items:
                qty = item.get('quantity', 1)
                title = item.get('title', 'Producto')
                productos_desc.append(f"{qty}x {title}")
                total_cantidad += qty
            productos_str = ", ".join(productos_desc)
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Guardar en base de datos
            guardar_ticket_sqlite(
                fecha=fecha_actual,
                producto=productos_str,
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

# MODIFICACIONES A TU CLASE AppCafeteria:

# 1. En el __init__ de AppCafeteria, agrega después de la línea existente:
# self.promocion_frappes_activa = False
# AGREGAR ESTA LÍNEA:
# self.pedidos_manager = PedidosOnlineManager(self)

# 2. En show_menu(), modifica la lista de botones para incluir pedidos en línea:

def show_menu_modificado(self):
    """Reemplaza tu método show_menu existente con este"""
    self.clear_frames()
    frame = tk.Frame(self, bg="#235A6F")
    frame.pack(fill="both", expand=True)
    self.frames["menu"] = frame

    # Card centrado y adaptable
    card = tk.Frame(frame, bg="#FFFFFF", bd=0, relief="flat",
                    highlightbackground="#235A6F", highlightthickness=4, width=480)
    card.pack(expand=True)

    tk.Label(
        card,
        text="Sistema de Ventas",
        font=("Segoe UI", 32, "bold"),
        bg="#FFFFFF",
        fg="#235A6F"
    ).pack(pady=(40, 30))

    # LISTA MODIFICADA DE BOTONES - INCLUYE PEDIDOS EN LÍNEA
    botones = [
        ("Generar Compra", self.show_compra),
        ("🌐 Pedidos en Línea", self.show_pedidos_online),  # <-- NUEVO BOTÓN
        ("Ver Inventario", self.show_inventario),
        ("Ver Historial de Tickets", self.show_historial),
        ("Resumen de Ventas", self.show_ventas),
        ("Ver Ventas (DB)", self.show_ventas_db),
    ]
    
    for texto, comando in botones:
        # Color especial para pedidos en línea
        color_fondo = "#E67E22" if "🌐" in texto else "#235A6F"
        color_activo = "#D35400" if "🌐" in texto else "#183B4A"
        
        tk.Button(
            card,
            text=texto,
            command=comando,
            font=("Segoe UI", 18, "bold"),
            width=22,
            height=2,
            bg=color_fondo,
            fg="white",
            bd=0,
            activebackground=color_activo,
            activeforeground="white",
            cursor="hand2",
            highlightthickness=0
        ).pack(pady=10)

    tk.Button(
        card,
        text="Salir del Programa",
        command=self.destroy,
        font=("Segoe UI", 18, "bold"),
        width=22,
        height=2,
        bg="#E74C3C",
        fg="white",
        bd=0,
        activebackground="#922B21",
        activeforeground="white",
        cursor="hand2",
        highlightthickness=0
    ).pack(pady=18)

# 3. AGREGAR ESTE NUEVO MÉTODO A TU CLASE AppCafeteria:

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

    def procesar_a_pos(order):
        if self.pedidos_manager.process_web_order(order):
            messagebox.showinfo("Éxito", "Pedido agregado al sistema POS")
            # Marcar como procesado
            order_id = order.get('id')
            if order_id:
                self.pedidos_manager.update_order_status(order_id, "preparando")
            actualizar_pedidos()
        else:
            messagebox.showerror("Error", "No se pudo procesar el pedido")

    # Botones de control
    tk.Button(
        control_frame,
        text="🔄 Actualizar Pedidos",
        command=actualizar_pedidos,
        bg="#3498DB",
        fg="white",
        font=("Segoe UI", 14, "bold"),
        width=20,
        bd=0,
        cursor="hand2"
    ).pack(side="left", padx=10)

    tk.Button(
        control_frame,
        text="🔍 Verificar Conexión",
        command=verificar_conexion,
        bg="#9B59B6",
        fg="white",
        font=("Segoe UI", 14, "bold"),
        width=20,
        bd=0,
        cursor="hand2"
    ).pack(side="left", padx=10)

    # Frame para mostrar pedidos
    self.pedidos_container = tk.Frame(card, bg="#FFFFFF")
    self.pedidos_container.pack(pady=20, padx=20, fill="both", expand=True)

    def mostrar_pedidos():
        # Limpiar pedidos anteriores
        for widget in self.pedidos_container.winfo_children():
            widget.destroy()

        orders = self.pedidos_manager.get_web_orders()
        
        if not orders:
            tk.Label(
                self.pedidos_container,
                text="📭 No hay pedidos pendientes",
                font=("Segoe UI", 16),
                bg="#FFFFFF",
                fg="#7F8C8D"
            ).pack(pady=30)
            return

        for i, order in enumerate(orders):
            # Frame para cada pedido
            order_frame = tk.Frame(
                self.pedidos_container,
                bg="#ECF0F1",
                relief="raised",
                bd=2,
                padx=15,
                pady=15
            )
            order_frame.pack(fill="x", pady=10)

            # Color según estado
            status = order.get('pos_status', 'nuevo')
            if status == 'preparando':
                order_frame.config(bg="#FEF9E7")
            elif status == 'listo':
                order_frame.config(bg="#E8F8F5")
            elif status == 'entregado':
                order_frame.config(bg="#EAEDED")

            # Información del cliente
            customer = order.get('customer', {})
            tk.Label(
                order_frame,
                text=f"👤 Cliente: {customer.get('name', 'Sin nombre')}",
                font=("Segoe UI", 14, "bold"),
                bg=order_frame.cget("bg"),
                fg="#2C3E50"
            ).pack(anchor="w")

            tk.Label(
                order_frame,
                text=f"📞 Teléfono: {customer.get('phone', 'No disponible')}",
                font=("Segoe UI", 12),
                bg=order_frame.cget("bg"),
                fg="#34495E"
            ).pack(anchor="w")

            # Items del pedido
            items = order.get('items', [])
            items_text = "🛍️ Productos: "
            for item in items:
                qty = item.get('quantity', 1)
                title = item.get('title', 'Producto')
                price = item.get('unit_price', 0)
                items_text += f"{qty}x {title} (${price}) • "
            
            tk.Label(
                order_frame,
                text=items_text.rstrip(" • "),
                font=("Segoe UI", 12),
                bg=order_frame.cget("bg"),
                fg="#34495E",
                wraplength=800,
                justify="left"
            ).pack(anchor="w", pady=(5, 0))

            # Total y fecha
            total = order.get('total', 0)
            created_at = order.get('created_at', 'Fecha no disponible')
            
            info_frame = tk.Frame(order_frame, bg=order_frame.cget("bg"))
            info_frame.pack(fill="x", pady=(10, 0))
            
            tk.Label(
                info_frame,
                text=f"💰 Total: ${total}",
                font=("Segoe UI", 14, "bold"),
                bg=order_frame.cget("bg"),
                fg="#E74C3C"
            ).pack(side="left")

            tk.Label(
                info_frame,
                text=f"📅 {created_at}",
                font=("Segoe UI", 10),
                bg=order_frame.cget("bg"),
                fg="#7F8C8D"
            ).pack(side="right")

            # Botones de acción
            button_frame = tk.Frame(order_frame, bg=order_frame.cget("bg"))
            button_frame.pack(fill="x", pady=(15, 0))

            order_id = order.get('id')
            
            # Botón para agregar al POS
            tk.Button(
                button_frame,
                text="➕ Agregar al POS",
                command=lambda o=order: procesar_a_pos(o),
                bg="#27AE60",
                fg="white",
                font=("Segoe UI", 12, "bold"),
                bd=0,
                cursor="hand2",
                width=15
            ).pack(side="left", padx=(0, 10))

            # Botón preparando
            tk.Button(
                button_frame,
                text="🔄 Preparando",
                command=lambda oid=order_id, of=order_frame: marcar_preparando(oid, of),
                bg="#F39C12",
                fg="white",
                font=("Segoe UI", 12, "bold"),
                bd=0,
                cursor="hand2",
                width=15
            ).pack(side="left", padx=(0, 10))

            # Botón listo
            tk.Button(
                button_frame,
                text="✅ Listo",
                command=lambda oid=order_id, of=order_frame: marcar_listo(oid, of),
                bg="#27AE60",
                fg="white",
                font=("Segoe UI", 12, "bold"),
                bd=0,
                cursor="hand2",
                width=15
            ).pack(side="left")

    # Cargar pedidos inicialmente
    actualizar_pedidos()

    # Botón volver al menú
    tk.Button(
        card,
        text="🏠 Volver al Menú",
        command=self.show_menu,
        bg="#235A6F",
        fg="white",
        font=("Segoe UI", 16, "bold"),
        bd=0,
        activebackground="#183B4A",
        activeforeground="white",
        cursor="hand2",
        highlightthickness=0,
        width=20,
        height=2
    ).pack(pady=20)

# INSTRUCCIONES DE INSTALACIÓN:
"""
1. Agrega estos imports al inicio de tu archivo cafeteria_sistema.py:
   import requests
   import threading
   import time
   import json

2. En tu clase AppCafeteria, en el método __init__, después de:
   self.promocion_frappes_activa = False
   
   AGREGA:
   self.pedidos_manager = PedidosOnlineManager(self)

3. Reemplaza tu método show_menu con show_menu_modificado

4. Agrega el método show_pedidos_online a tu clase AppCafeteria

5. ¡Listo! Ahora tendrás un botón "🌐 Pedidos en Línea" en tu menú principal
"""
