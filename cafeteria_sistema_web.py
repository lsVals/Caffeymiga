import requests
import threading
import time
import json
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, date, time as dt_time  # <-- CORREGIDO AQUÍ
import pandas as pd
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import tempfile
import win32print
import win32ui
import requests
import threading
import time
import json
import tkinter.simpledialog as simpledialog
import matplotlib.pyplot as plt
from functools import partial
import logging
import pdfplumber
import sqlite3
import requests
import threading
import time
import json
import tkinter.ttk as ttk
import shutil
import zipfile
import calendar
from PIL import Image, ImageTk, ImageOps  # Asegúrate de tener Pillow instalado

# Archivos base
ARCHIVO_INVENTARIO = "inventario.xlsx"
ARCHIVO_TICKETS = "tickets.xlsx"
ARCHIVO_EXCEL = "tickets.xlsx"  # Usado para agregar_a_excel

# Variables globales
usuario_valido = "admin"
contrasena_valida = "admin"
ventanas_abiertas = {"menu": False, "inventario": False, "compra": False, "historial": False}

# Configuración básica de logging
logging.basicConfig(
    filename="cafeteria_log.txt",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s:%(message)s"
)

# Funciones de Inventario
def cargar_inventario():
    try:
        if not os.path.exists(ARCHIVO_INVENTARIO):
            df = pd.DataFrame(columns=["Producto", "Unidades", "Precio", "TipoUnidad"])
            df.to_excel(ARCHIVO_INVENTARIO, index=False)
        df = pd.read_excel(ARCHIVO_INVENTARIO)
        if "TipoUnidad" not in df.columns:
            df["TipoUnidad"] = "Unidad"
        return df
    except PermissionError:
        messagebox.showerror(
            "Archivo en uso",
            "El archivo de inventario está abierto en otro programa (por ejemplo, Excel). Ciérralo e inténtalo de nuevo."
        )
        logging.error("Permiso denegado al acceder a inventario.xlsx")
        return pd.DataFrame(columns=["Producto", "Unidades", "Precio", "TipoUnidad"])
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el inventario:\n{e}")
        logging.error(f"Error al cargar inventario: {e}")
        return pd.DataFrame(columns=["Producto", "Unidades", "Precio", "TipoUnidad"])

def guardar_inventario(df):
    try:
        df.to_excel(ARCHIVO_INVENTARIO, index=False)
    except PermissionError:
        messagebox.showerror(
            "Archivo en uso",
            "El archivo de inventario está abierto en otro programa (por ejemplo, Excel). Ciérralo e inténtalo de nuevo."
        )
        logging.error("Permiso denegado al guardar inventario.xlsx")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el inventario:\n{e}")
        logging.error(f"Error al guardar inventario: {e}")

def inicializar_db():
    conn = sqlite3.connect('ventas.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            producto TEXT,
            cantidad INTEGER,
            precio REAL,
            pago TEXT,
            estado TEXT,
            motivo_cancelacion TEXT
        )
    ''')
    conn.commit()
    conn.close()

inicializar_db()

def obtener_ventas():
    conn = sqlite3.connect('ventas.db')
    df = pd.read_sql_query("SELECT * FROM tickets", conn)
    conn.close()
    return df

def eliminar_venta_db(id_ticket):
    """Marca como 'Cancelado' una venta en la base de datos por su ID."""
    conn = sqlite3.connect('ventas.db')
    c = conn.cursor()
    c.execute("UPDATE tickets SET estado = 'Cancelado', motivo_cancelacion = 'Eliminado manualmente' WHERE id = ?", (id_ticket,))
    conn.commit()
    conn.close()

class PedidosOnlineManager:
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.server_url = "http://localhost:3000"
        self.monitoring = False
        self.monitor_thread = None
        self.pedidos_procesados = set()  # Para evitar duplicados
        
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
    
    def iniciar_monitoreo_automatico(self):
        """Iniciar monitoreo automático de pedidos web"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("🔄 Monitoreo automático de pedidos web iniciado")
        messagebox.showinfo("Pedidos Web", "¡Monitoreo automático de pedidos web iniciado!\n\nLos pedidos llegarán automáticamente cada 15 segundos.")
    
    def detener_monitoreo(self):
        """Detener monitoreo automático"""
        self.monitoring = False
        print("🛑 Monitoreo automático detenido")
    
    def _monitor_loop(self):
        """Bucle de monitoreo en segundo plano"""
        while self.monitoring:
            try:
                self.verificar_nuevos_pedidos()
                time.sleep(15)  # Verificar cada 15 segundos
            except Exception as e:
                print(f"Error en monitoreo: {e}")
                time.sleep(30)  # Esperar más si hay error
    
    def verificar_nuevos_pedidos(self):
        """Verificar y procesar nuevos pedidos web"""
        if not self.test_connection():
            return
            
        try:
            pedidos = self.get_web_orders()
            nuevos_procesados = 0
            
            for pedido in pedidos:
                pedido_id = pedido.get('id', '')
                if pedido_id and pedido_id not in self.pedidos_procesados:
                    if self.process_web_order_to_ticket(pedido):
                        self.pedidos_procesados.add(pedido_id)
                        nuevos_procesados += 1
                        print(f"✅ Pedido web procesado: {pedido_id[:8]}...")
            
            if nuevos_procesados > 0:
                print(f"🆕 {nuevos_procesados} pedidos web nuevos procesados")
                # Mostrar notificación completa
                self.mostrar_notificacion_pedido(nuevos_procesados)
                    
        except Exception as e:
            print(f"Error verificando pedidos: {e}")
    
    def process_web_order_to_ticket(self, order):
        """Procesar pedido web y agregarlo como ticket"""
        try:
            cliente = order.get('cliente', {})
            productos = order.get('productos', [])
            
            # Procesar cada producto del pedido por separado
            for producto in productos:
                nombre = producto.get('nombre', 'Producto Web')
                cantidad = producto.get('cantidad', 1)
                precio = producto.get('precio', 0)
                
                # Crear descripción con info del cliente
                descripcion = f"🌐 WEB: {nombre}"
                if cliente.get('nombre'):
                    motivo = f"Cliente: {cliente['nombre']} - Tel: {cliente.get('telefono', 'N/A')}"
                else:
                    motivo = "Pedido web sin datos de cliente"
                
                # Agregar a la base de datos
                self.parent_app.agregar_ticket(
                    nombre=descripcion,
                    cantidad=cantidad,
                    precio=precio,
                    pago='WEB-PAGO',
                    estado='NUEVO-WEB',
                    motivo_cancelacion=motivo
                )
            
            return True
        except Exception as e:
            print(f"Error procesando pedido: {e}")
            return False

class AppCafeteria(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Ventas")
        self.geometry("600x700")
        self.configure(bg="#f0f0f0")
        self.frames = {}
        self.promocion_frappes_activa = False
        
        # ✅ AQUÍ SE INICIALIZA EL MANAGER DE PEDIDOS WEB
        self.pedidos_manager = PedidosOnlineManager(self)

        # Reinicio automático antes de las 9:00 am
        self.reiniciar_dia_si_corresponde()

        self.show_login()

    def reiniciar_dia_si_corresponde(self):
        archivo_reinicio = "ultimo_reinicio.txt"
        hoy = date.today()
        ahora = datetime.now().time()
        hora_limite = dt_time(9, 0)  # 9:00 am

        if os.path.exists(archivo_reinicio):
            with open(archivo_reinicio, "r") as f:
                ultima_fecha = f.read().strip()
        else:
            ultima_fecha = ""

    def clear_frames(self):
        for frame in self.frames.values():
            try:
                frame.pack_forget()
                frame.place_forget()  # <-- Añade esto para limpiar también los frames con place
            except Exception:
                pass

    def show_login(self):
        self.clear_frames()
        frame = tk.Frame(self, bg="#235A6F")
        frame.pack(fill="both", expand=True)
        self.frames["login"] = frame

        # Card grande y centrado para el login
        card = tk.Frame(frame, bg="#FFFFFF", bd=0, relief="flat", highlightbackground="#235A6F", highlightthickness=4)
        card.place(relx=0.5, rely=0, anchor="n", y=40)

        # Ícono de café (como antes)
        tk.Label(card, text="☕", font=("Segoe UI Emoji", 80, "bold"), bg="#FFFFFF", fg="#235A6F").pack(pady=(35, 10))

        tk.Label(card, text="Sistema de Ventas", font=("Segoe UI", 32, "bold"), bg="#FFFFFF", fg="#235A6F").pack(pady=(0, 30))

        tk.Label(card, text="Usuario", font=("Segoe UI", 18, "bold"), bg="#FFFFFF", fg="#235A6F", anchor="w").pack(fill="x", padx=60)
        entry_usuario = tk.Entry(card, font=("Segoe UI", 20), width=22, bd=0, relief="flat", highlightbackground="#235A6F", justify="center", bg="#F4F6F7", fg="#222", highlightthickness=2)
        entry_usuario.pack(padx=60, pady=(0, 18))
        tk.Label(card, text="Contraseña", font=("Segoe UI", 18, "bold"), bg="#FFFFFF", fg="#235A6F", anchor="w").pack(fill="x", padx=60)
        entry_contrasena = tk.Entry(card, show="*", font=("Segoe UI", 20), width=22, bd=0, relief="flat", highlightbackground="#235A6F", justify="center", bg="#F4F6F7", fg="#222", highlightthickness=2)
        entry_contrasena.pack(padx=60, pady=(0, 30))

        def verificar_login(event=None):
            if entry_usuario.get() == usuario_valido and entry_contrasena.get() == contrasena_valida:
                self.show_menu()
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

        entry_usuario.bind("<Return>", verificar_login)
        entry_contrasena.bind("<Return>", verificar_login)

        tk.Button(
            card, text="Entrar", command=verificar_login,
            bg="#235A6F", fg="white", font=("Segoe UI", 24, "bold"),
            width=18, height=2, bd=0, activebackground="#183B4A", activeforeground="white",
            cursor="hand2", relief="flat", highlightthickness=0
        ).pack(pady=18)

    def show_menu(self):
        self.clear_frames()
        frame = tk.Frame(self, bg="#235A6F")
        frame.pack(fill="both", expand=True)
        self.frames["menu"] = frame

        # Card centrado y adaptable
        card = tk.Frame(frame, bg="#FFFFFF", bd=0, relief="flat",
                        highlightbackground="#235A6F", highlightthickness=4, width=480)
        card.pack(expand=True)
        # No uses pack_propagate(False) aquí

        tk.Label(
            card,
            text="Sistema de Ventas",
            font=("Segoe UI", 32, "bold"),
            bg="#FFFFFF",
            fg="#235A6F"
        ).pack(pady=(40, 30))

        botones = [
            ("Generar Compra", self.show_compra),
            ("🌐 Pedidos en Línea", self.show_pedidos_online),
            ("Ver Inventario", self.show_inventario),
            ("Ver Historial de Tickets", self.show_historial),
            ("Resumen de Ventas", self.show_ventas),
            ("Ver Ventas (DB)", self.show_ventas_db),
        ]
        for texto, comando in botones:
            tk.Button(
                card,
                text=texto,
                command=comando,
                font=("Segoe UI", 18, "bold"),
                width=22,
                height=2,
                bg="#235A6F",
                fg="white",
                bd=0,
                activebackground="#183B4A",
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

    def show_pedidos_online(self):
        """Mostrar pedidos web en línea"""
        self.clear_frames()
        frame = tk.Frame(self, bg="#FFFFFF")
        frame.pack(fill="both", expand=True)
        self.frames["pedidos_online"] = frame
        
        # Card centrado
        card = tk.Frame(frame, bg="#FFFFFF", bd=0, relief="flat",
                        highlightbackground="#E67E22", highlightthickness=4, width=600)
        card.pack(expand=True, pady=40)
        
        tk.Label(card, text="🌐 PEDIDOS EN LÍNEA", font=("Segoe UI", 28, "bold"), 
                bg="#FFFFFF", fg="#E67E22").pack(pady=(30, 20))
        
        # Estado de conexión
        if self.pedidos_manager.test_connection():
            tk.Label(card, text="✅ Conectado al servidor web", 
                    font=("Segoe UI", 16), bg="#FFFFFF", fg="#27AE60").pack(pady=10)
            
            # Botones de control
            btn_frame = tk.Frame(card, bg="#FFFFFF")
            btn_frame.pack(pady=20)
            
            def iniciar_monitoreo():
                self.pedidos_manager.iniciar_monitoreo_automatico()
            
            def detener_monitoreo():
                self.pedidos_manager.detener_monitoreo()
                messagebox.showinfo("Pedidos Web", "Monitoreo automático detenido")
            
            def verificar_ahora():
                self.pedidos_manager.verificar_nuevos_pedidos()
                messagebox.showinfo("Verificación", "Verificación manual completada")
            
            tk.Button(btn_frame, text="🚀 Iniciar Monitoreo Automático", 
                     command=iniciar_monitoreo,
                     bg="#27AE60", fg="white", font=("Segoe UI", 14, "bold"),
                     width=25, height=2, bd=0, cursor="hand2").pack(pady=5)
            
            tk.Button(btn_frame, text="🛑 Detener Monitoreo", 
                     command=detener_monitoreo,
                     bg="#E74C3C", fg="white", font=("Segoe UI", 14, "bold"),
                     width=25, height=2, bd=0, cursor="hand2").pack(pady=5)
            
            tk.Button(btn_frame, text="🔄 Verificar Pedidos Ahora", 
                     command=verificar_ahora,
                     bg="#3498DB", fg="white", font=("Segoe UI", 14, "bold"),
                     width=25, height=2, bd=0, cursor="hand2").pack(pady=5)
            
            # Estado del monitoreo
            estado_texto = "🔄 Activo" if self.pedidos_manager.monitoring else "⏸️ Detenido"
            tk.Label(card, text=f"Estado del monitoreo: {estado_texto}", 
                    font=("Segoe UI", 14), bg="#FFFFFF", fg="#7F8C8D").pack(pady=10)
            
            # Información
            info_frame = tk.Frame(card, bg="#F8F9FA", relief="groove", bd=2)
            info_frame.pack(pady=20, padx=40, fill="x")
            
            tk.Label(info_frame, text="ℹ️ INFORMACIÓN", font=("Segoe UI", 14, "bold"), 
                    bg="#F8F9FA", fg="#2C3E50").pack(pady=(10, 5))
            
            info_text = """• Los pedidos web llegan automáticamente cada 15 segundos
• Se guardan en la base de datos con estado 'NUEVO-WEB'
• Puedes verlos en 'Ver Ventas (DB)'
• Se reproduce un sonido cuando llegan nuevos pedidos
• El servidor web debe estar ejecutándose en localhost:3000"""
            
            tk.Label(info_frame, text=info_text, font=("Segoe UI", 11), 
                    bg="#F8F9FA", fg="#34495E", justify="left").pack(pady=(5, 15), padx=20)
        else:
            tk.Label(card, text="❌ No se puede conectar al servidor web", 
                    font=("Segoe UI", 16), bg="#FFFFFF", fg="#E74C3C").pack(pady=20)
            
            tk.Label(card, text="Asegúrate de que el servidor esté ejecutándose:\npython main.py", 
                    font=("Segoe UI", 12), bg="#FFFFFF", fg="#7F8C8D").pack(pady=10)
        
        tk.Button(card, text="⬅️ Volver al Menú", command=self.show_menu,
                 bg="#95A5A6", fg="white", font=("Segoe UI", 16, "bold"),
                 width=20, height=2, bd=0, cursor="hand2").pack(pady=30)

    def agregar_ticket(self, nombre, cantidad, precio, pago, estado="Completado", motivo_cancelacion=""):
        """Agregar ticket a la base de datos"""
        try:
            conn = sqlite3.connect('ventas.db')
            c = conn.cursor()
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            c.execute("""
                INSERT INTO tickets (fecha, producto, cantidad, precio, pago, estado, motivo_cancelacion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (fecha_actual, nombre, cantidad, precio, pago, estado, motivo_cancelacion))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error agregando ticket: {e}")
            return False

    def show_inventario(self):
        """Mostrar y gestionar inventario"""
        self.clear_frames()
        frame = tk.Frame(self, bg="#FFFFFF")
        frame.pack(fill="both", expand=True)
        self.frames["inventario"] = frame

        card = tk.Frame(frame, bg="#FFFFFF", bd=0, relief="flat",
                        highlightbackground="#27AE60", highlightthickness=4, width=700)
        card.pack(expand=True, pady=20)

        tk.Label(card, text="📦 GESTIÓN DE INVENTARIO", font=("Segoe UI", 24, "bold"), 
                bg="#FFFFFF", fg="#27AE60").pack(pady=(20, 15))

        # Botones principales
        btn_frame = tk.Frame(card, bg="#FFFFFF")
        btn_frame.pack(pady=15)

        def agregar_producto():
            # Ventana para agregar producto
            add_window = tk.Toplevel(self)
            add_window.title("Agregar Producto")
            add_window.geometry("400x300")
            add_window.configure(bg="#FFFFFF")
            add_window.transient(self)
            add_window.grab_set()

            tk.Label(add_window, text="Nombre del Producto:", font=("Segoe UI", 12), 
                    bg="#FFFFFF").pack(pady=10)
            entry_nombre = tk.Entry(add_window, font=("Segoe UI", 12), width=30)
            entry_nombre.pack(pady=5)

            tk.Label(add_window, text="Cantidad:", font=("Segoe UI", 12), 
                    bg="#FFFFFF").pack(pady=10)
            entry_cantidad = tk.Entry(add_window, font=("Segoe UI", 12), width=30)
            entry_cantidad.pack(pady=5)

            tk.Label(add_window, text="Precio:", font=("Segoe UI", 12), 
                    bg="#FFFFFF").pack(pady=10)
            entry_precio = tk.Entry(add_window, font=("Segoe UI", 12), width=30)
            entry_precio.pack(pady=5)

            def guardar_producto():
                try:
                    df = cargar_inventario()
                    nuevo_producto = pd.DataFrame({
                        "Producto": [entry_nombre.get()],
                        "Unidades": [int(entry_cantidad.get())],
                        "Precio": [float(entry_precio.get())],
                        "TipoUnidad": ["Unidad"]
                    })
                    df = pd.concat([df, nuevo_producto], ignore_index=True)
                    guardar_inventario(df)
                    add_window.destroy()
                    messagebox.showinfo("Éxito", "Producto agregado correctamente")
                except Exception as e:
                    messagebox.showerror("Error", f"Error al agregar producto: {e}")

            tk.Button(add_window, text="Guardar", command=guardar_producto,
                     bg="#27AE60", fg="white", font=("Segoe UI", 12, "bold"),
                     width=20, height=2).pack(pady=20)

        tk.Button(btn_frame, text="➕ Agregar Producto", command=agregar_producto,
                 bg="#27AE60", fg="white", font=("Segoe UI", 12, "bold"),
                 width=18, height=2, bd=0, cursor="hand2").pack(side="left", padx=10)

        def ver_inventario():
            try:
                df = cargar_inventario()
                if df.empty:
                    messagebox.showinfo("Inventario", "No hay productos en el inventario")
                    return
                
                # Crear ventana para mostrar inventario
                inv_window = tk.Toplevel(self)
                inv_window.title("Inventario Actual")
                inv_window.geometry("600x400")
                inv_window.configure(bg="#FFFFFF")

                # Crear tabla
                columns = ("Producto", "Cantidad", "Precio", "Tipo")
                tree = ttk.Treeview(inv_window, columns=columns, show="headings", height=15)
                
                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=120)

                for _, row in df.iterrows():
                    tree.insert("", "end", values=(
                        row['Producto'],
                        row['Unidades'],
                        f"${row['Precio']:.2f}",
                        row.get('TipoUnidad', 'Unidad')
                    ))

                tree.pack(pady=20, padx=20, fill="both", expand=True)

            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar inventario: {e}")

        tk.Button(btn_frame, text="👁️ Ver Inventario", command=ver_inventario,
                 bg="#3498DB", fg="white", font=("Segoe UI", 12, "bold"),
                 width=18, height=2, bd=0, cursor="hand2").pack(side="left", padx=10)

        tk.Button(btn_frame, text="⬅️ Volver", command=self.show_menu,
                 bg="#95A5A6", fg="white", font=("Segoe UI", 12, "bold"),
                 width=18, height=2, bd=0, cursor="hand2").pack(side="left", padx=10)

    def show_compra(self):
        """Mostrar interfaz de compra/venta"""
        self.clear_frames()
        frame = tk.Frame(self, bg="#FFFFFF")
        frame.pack(fill="both", expand=True)
        self.frames["compra"] = frame

        card = tk.Frame(frame, bg="#FFFFFF", bd=0, relief="flat",
                        highlightbackground="#E67E22", highlightthickness=4, width=600)
        card.pack(expand=True, pady=20)

        tk.Label(card, text="🛒 GENERAR VENTA", font=("Segoe UI", 24, "bold"), 
                bg="#FFFFFF", fg="#E67E22").pack(pady=(20, 15))

        # Campos de entrada
        tk.Label(card, text="Producto:", font=("Segoe UI", 14, "bold"), 
                bg="#FFFFFF", fg="#2C3E50").pack(pady=(10, 5))
        entry_producto = tk.Entry(card, font=("Segoe UI", 12), width=30)
        entry_producto.pack(pady=5)

        tk.Label(card, text="Cantidad:", font=("Segoe UI", 14, "bold"), 
                bg="#FFFFFF", fg="#2C3E50").pack(pady=(10, 5))
        entry_cantidad = tk.Entry(card, font=("Segoe UI", 12), width=30)
        entry_cantidad.pack(pady=5)

        tk.Label(card, text="Precio:", font=("Segoe UI", 14, "bold"), 
                bg="#FFFFFF", fg="#2C3E50").pack(pady=(10, 5))
        entry_precio = tk.Entry(card, font=("Segoe UI", 12), width=30)
        entry_precio.pack(pady=5)

        tk.Label(card, text="Método de Pago:", font=("Segoe UI", 14, "bold"), 
                bg="#FFFFFF", fg="#2C3E50").pack(pady=(10, 5))
        
        pago_var = tk.StringVar(value="Efectivo")
        pago_frame = tk.Frame(card, bg="#FFFFFF")
        pago_frame.pack(pady=10)
        
        for pago in ["Efectivo", "Tarjeta", "Transferencia"]:
            tk.Radiobutton(pago_frame, text=pago, variable=pago_var, value=pago,
                          font=("Segoe UI", 11), bg="#FFFFFF").pack(side="left", padx=10)

        def procesar_venta():
            try:
                producto = entry_producto.get().strip()
                cantidad = int(entry_cantidad.get())
                precio = float(entry_precio.get())
                pago = pago_var.get()

                if not producto:
                    messagebox.showerror("Error", "El nombre del producto es requerido")
                    return

                # Agregar a la base de datos
                if self.agregar_ticket(producto, cantidad, precio, pago):
                    messagebox.showinfo("Éxito", "Venta registrada correctamente")
                    # Limpiar campos
                    entry_producto.delete(0, tk.END)
                    entry_cantidad.delete(0, tk.END)
                    entry_precio.delete(0, tk.END)
                else:
                    messagebox.showerror("Error", "No se pudo registrar la venta")

            except ValueError:
                messagebox.showerror("Error", "Cantidad y precio deben ser números válidos")
            except Exception as e:
                messagebox.showerror("Error", f"Error al procesar venta: {e}")

        tk.Button(card, text="💰 Procesar Venta", command=procesar_venta,
                 bg="#E67E22", fg="white", font=("Segoe UI", 16, "bold"),
                 width=20, height=2, bd=0, cursor="hand2").pack(pady=20)

        tk.Button(card, text="⬅️ Volver al Menú", command=self.show_menu,
                 bg="#95A5A6", fg="white", font=("Segoe UI", 14, "bold"),
                 width=20, height=2, bd=0, cursor="hand2").pack(pady=10)

    def show_historial(self):
        """Mostrar historial de tickets (Excel)"""
        self.clear_frames()
        frame = tk.Frame(self, bg="#FFFFFF")
        frame.pack(fill="both", expand=True)
        self.frames["historial"] = frame

        card = tk.Frame(frame, bg="#FFFFFF", bd=0, relief="flat",
                        highlightbackground="#9B59B6", highlightthickness=4, width=600)
        card.pack(expand=True, pady=40)

        tk.Label(card, text="📋 HISTORIAL DE TICKETS", font=("Segoe UI", 24, "bold"), 
                bg="#FFFFFF", fg="#9B59B6").pack(pady=(30, 20))

        def abrir_excel():
            try:
                if os.path.exists(ARCHIVO_EXCEL):
                    os.startfile(ARCHIVO_EXCEL)
                else:
                    messagebox.showinfo("Información", "No se encontró el archivo de tickets Excel")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")

        tk.Button(card, text="📊 Abrir Excel", command=abrir_excel,
                 bg="#27AE60", fg="white", font=("Segoe UI", 16, "bold"),
                 width=20, height=2, bd=0, cursor="hand2").pack(pady=15)

        tk.Button(card, text="⬅️ Volver al Menú", command=self.show_menu,
                 bg="#95A5A6", fg="white", font=("Segoe UI", 16, "bold"),
                 width=20, height=2, bd=0, cursor="hand2").pack(pady=15)

    def show_ventas(self):
        """Mostrar resumen de ventas"""
        self.clear_frames()
        frame = tk.Frame(self, bg="#FFFFFF")
        frame.pack(fill="both", expand=True)
        self.frames["ventas"] = frame

        card = tk.Frame(frame, bg="#FFFFFF", bd=0, relief="flat",
                        highlightbackground="#E74C3C", highlightthickness=4, width=600)
        card.pack(expand=True, pady=40)

        tk.Label(card, text="📈 RESUMEN DE VENTAS", font=("Segoe UI", 24, "bold"), 
                bg="#FFFFFF", fg="#E74C3C").pack(pady=(30, 20))

        try:
            df = obtener_ventas()
            if not df.empty:
                # Filtrar solo ventas completadas
                df_completadas = df[df['estado'].isin(['Completado', 'NUEVO-WEB'])]
                
                total_ventas = len(df_completadas)
                total_ingresos = df_completadas['precio'].sum()
                
                # Ventas por método de pago
                ventas_pago = df_completadas.groupby('pago')['precio'].sum()
                
                # Mostrar estadísticas
                stats_frame = tk.Frame(card, bg="#F8F9FA", relief="groove", bd=2)
                stats_frame.pack(pady=20, padx=40, fill="x")
                
                tk.Label(stats_frame, text=f"Total de Ventas: {total_ventas}", 
                        font=("Segoe UI", 14, "bold"), bg="#F8F9FA").pack(pady=5)
                tk.Label(stats_frame, text=f"Ingresos Totales: ${total_ingresos:.2f}", 
                        font=("Segoe UI", 14, "bold"), bg="#F8F9FA").pack(pady=5)
                
                tk.Label(stats_frame, text="Ventas por Método de Pago:", 
                        font=("Segoe UI", 12, "bold"), bg="#F8F9FA").pack(pady=(10, 5))
                
                for pago, total in ventas_pago.items():
                    tk.Label(stats_frame, text=f"{pago}: ${total:.2f}", 
                            font=("Segoe UI", 11), bg="#F8F9FA").pack(pady=2)
            else:
                tk.Label(card, text="No hay ventas registradas", 
                        font=("Segoe UI", 16), bg="#FFFFFF", fg="#7F8C8D").pack(pady=20)
                
        except Exception as e:
            tk.Label(card, text=f"Error al cargar estadísticas: {e}", 
                    font=("Segoe UI", 14), bg="#FFFFFF", fg="#E74C3C").pack(pady=20)

        tk.Button(card, text="⬅️ Volver al Menú", command=self.show_menu,
                 bg="#95A5A6", fg="white", font=("Segoe UI", 16, "bold"),
                 width=20, height=2, bd=0, cursor="hand2").pack(pady=30)

    def mostrar_notificacion_pedido(self, cantidad_pedidos):
        """Mostrar notificación completa cuando llegan nuevos pedidos"""
        try:
            # 1. Reproducir sonido distintivo (triple beep)
            import winsound
            for _ in range(3):
                winsound.Beep(1500, 300)  # Beep agudo
                time.sleep(0.1)
                winsound.Beep(1000, 300)  # Beep grave
                time.sleep(0.2)
        except:
            pass
        
        # 2. Crear ventana de notificación personalizada
        self.crear_ventana_notificacion(cantidad_pedidos)
        
        # 3. Hacer parpadear la ventana principal si está minimizada
        try:
            self.parent_app.attributes('-topmost', True)
            self.parent_app.after(100, lambda: self.parent_app.attributes('-topmost', False))
        except:
            pass
    
    def crear_ventana_notificacion(self, cantidad_pedidos):
        """Crear ventana de notificación personalizada"""
        # Crear ventana emergente
        notif_window = tk.Toplevel(self.parent_app)
        notif_window.title("🆕 NUEVOS PEDIDOS WEB")
        notif_window.geometry("400x300")
        notif_window.configure(bg="#E74C3C")
        notif_window.resizable(False, False)
        
        # Centrar en pantalla
        notif_window.transient(self.parent_app)
        notif_window.grab_set()
        
        # Configurar ventana siempre al frente
        notif_window.attributes('-topmost', True)
        
        # Contenido de la notificación
        tk.Label(notif_window, text="🚨", font=("Segoe UI Emoji", 60), 
                bg="#E74C3C", fg="white").pack(pady=(20, 10))
        
        tk.Label(notif_window, text="¡NUEVOS PEDIDOS WEB!", 
                font=("Segoe UI", 18, "bold"), bg="#E74C3C", fg="white").pack(pady=5)
        
        tk.Label(notif_window, text=f"{cantidad_pedidos} pedido{'s' if cantidad_pedidos > 1 else ''} recibido{'s' if cantidad_pedidos > 1 else ''}", 
                font=("Segoe UI", 14), bg="#E74C3C", fg="white").pack(pady=10)
        
        # Botones de acción
        btn_frame = tk.Frame(notif_window, bg="#E74C3C")
        btn_frame.pack(pady=20)
        
        def ver_pedidos():
            notif_window.destroy()
            self.parent_app.show_ventas_db()
        
        def cerrar_notificacion():
            notif_window.destroy()
        
        tk.Button(btn_frame, text="📋 Ver Pedidos", command=ver_pedidos,
                 bg="white", fg="#E74C3C", font=("Segoe UI", 12, "bold"),
                 width=12, height=2, bd=0, cursor="hand2").pack(side="left", padx=10)
        
        tk.Button(btn_frame, text="✖️ Cerrar", command=cerrar_notificacion,
                 bg="#C0392B", fg="white", font=("Segoe UI", 12, "bold"),
                 width=12, height=2, bd=0, cursor="hand2").pack(side="left", padx=10)
        
        # Auto-cerrar después de 10 segundos
        notif_window.after(10000, cerrar_notificacion)
        
        # Efecto de parpadeo
        self.animar_notificacion(notif_window)
    
    def animar_notificacion(self, window):
        """Crear efecto de parpadeo para la notificación"""
        def parpadear():
            try:
                for _ in range(6):  # 3 parpadeos
                    window.configure(bg="#F39C12")
                    window.update()
                    time.sleep(0.2)
                    window.configure(bg="#E74C3C")
                    window.update()
                    time.sleep(0.2)
            except:
                pass
        
        # Ejecutar parpadeo en thread separado para no bloquear UI
        threading.Thread(target=parpadear, daemon=True).start()

if __name__ == "__main__":
    try:
        app = AppCafeteria()
        app.mainloop()
    except Exception as e:
        logging.critical(f"Error crítico al iniciar la aplicación: {e}")
        messagebox.showerror("Error crítico", f"No se pudo iniciar la aplicación:\n{e}")
