import requests
import threading
import time
import json
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, date, time as dt_time
import pandas as pd
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import tempfile
import win32print
import win32ui
import tkinter.simpledialog as simpledialog
import matplotlib.pyplot as plt
from functools import partial
import logging
import pdfplumber
import sqlite3
import tkinter.ttk as ttk
import shutil
import zipfile
import calendar
from PIL import Image, ImageTk, ImageOps  # Asegúrate de tener Pillow instalado

# Importar configuración de rendimiento
try:
    from config_rendimiento import (
        get_config, optimizar_memoria, verificar_rendimiento,
        configurar_logging_optimizado
    )
    RENDIMIENTO_DISPONIBLE = True
except ImportError:
    RENDIMIENTO_DISPONIBLE = False


class PedidosWebManager:
    def __init__(self):
        self.db_path = "../caffeymiga_pedidos.db"  # NUEVO NOMBRE ÚNICO
        self.monitoring = False
        self.monitor_thread = None
        
        # DEBUG: Mostrar información de la base de datos
        import os
        abs_path = os.path.abspath(self.db_path)
        print(f"🔍 DEBUG BD: Ruta relativa: {self.db_path}")
        print(f"🔍 DEBUG BD: Ruta absoluta: {abs_path}")
        print(f"🔍 DEBUG BD: ¿Existe? {os.path.exists(abs_path)}")
        if os.path.exists(abs_path):
            print(f"🔍 DEBUG BD: Tamaño: {os.path.getsize(abs_path)} bytes")
        
    def test_connection(self):
        """Probar conexión con la base de datos local"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error conectando a pos_pedidos.db: {e}")
            return False
    
    def get_web_orders(self):
        """Obtener pedidos web desde la base de datos local"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # DEBUG: Verificar estructura de la tabla
            c.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = c.fetchall()
            print(f"🔍 DEBUG: Tablas en BD: {tables}")
            
            # DEBUG: Contar pedidos totales
            c.execute("SELECT COUNT(*) FROM pedidos")
            total = c.fetchone()[0]
            print(f"🔍 DEBUG: Total pedidos en BD: {total}")
            
            # DEBUG: Contar pendientes
            c.execute("SELECT COUNT(*) FROM pedidos WHERE estado = 'pendiente'")
            pendientes = c.fetchone()[0]
            print(f"🔍 DEBUG: Pedidos pendientes: {pendientes}")
            
            # Obtener pedidos pendientes
            c.execute("""
                SELECT id, cliente_nombre, cliente_telefono, hora_recogida, 
                       items, total, estado, metodo_pago, fecha_creacion 
                FROM pedidos 
                WHERE estado = 'pendiente'
                ORDER BY fecha_creacion ASC
            """)
            
            pedidos = []
            for row in c.fetchall():
                pedido = {
                    'id': row[0],
                    'cliente_nombre': row[1] if row[1] else 'Cliente Web',
                    'cliente_telefono': row[2] if row[2] else 'No especificado',
                    'hora_recogida': row[3] if row[3] else 'No especificada',
                    'items': row[4] if row[4] else '[]',
                    'total': row[5] if row[5] else 0.0,
                    'estado': row[6],
                    'metodo_pago': row[7] if row[7] else 'No especificado',
                    'fecha_creacion': row[8]
                }
                pedidos.append(pedido)
                print(f"🔍 DEBUG: Pedido cargado: {row[0]} - {row[1]} - ${row[5]}")
            
            conn.close()
            return pedidos
            
        except Exception as e:
            logging.error(f"Error obteniendo pedidos web: {e}")
            return []
    
    def update_order_status(self, order_id, new_status):
        """Actualizar el estado de un pedido en la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            fecha_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            c.execute("""
                UPDATE pedidos 
                SET estado = ?, fecha_actualizacion = ?
                WHERE id = ?
            """, (new_status, fecha_actualizacion, order_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logging.error(f"Error actualizando estado del pedido {order_id}: {e}")
            return False
    
    def iniciar_monitoreo(self):
        """Iniciar monitoreo automático de nuevos pedidos"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            return True
        return False
    
    def detener_monitoreo(self):
        """Detener monitoreo automático"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread = None
        return True
    
    def _monitor_loop(self):
        """Loop de monitoreo que se ejecuta en segundo plano"""
        while self.monitoring:
            try:
                self.verificar_nuevos_pedidos()
                time.sleep(30)  # Verificar cada 30 segundos
            except Exception as e:
                logging.error(f"Error en monitoreo de pedidos: {e}")
                time.sleep(60)  # Esperar más tiempo si hay error
    
    def verificar_nuevos_pedidos(self):
        """Verificar si hay nuevos pedidos pendientes"""
        try:
            pedidos = self.get_web_orders()
            if pedidos:
                # Aquí se puede agregar lógica para notificar sobre nuevos pedidos
                logging.info(f"Se encontraron {len(pedidos)} pedidos pendientes")
            return len(pedidos)
        except Exception as e:
            logging.error(f"Error verificando nuevos pedidos: {e}")
            return 0


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

class AppCafeteria(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Ventas - Caffè & Miga")
        
        # Obtener dimensiones de la pantalla
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Configurar ventana para que use el 90% de la pantalla
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        
        # Centrar la ventana
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.configure(bg="#f0f0f0")
        
        # Hacer que la ventana sea redimensionable
        self.resizable(True, True)
        
        # Configurar mínimo tamaño
        self.minsize(800, 600)
        
        self.frames = {}
        self.promocion_frappes_activa = False
        self.pedidos_manager = PedidosOnlineManager(self)
        self.pedidos_web_manager = PedidosWebManager()  # NUEVO

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

        # Contenedor principal centrado que se adapta al tamaño
        container = tk.Frame(frame, bg="#235A6F")
        container.pack(fill="both", expand=True)

        # Card de login más grande y responsivo
        card = tk.Frame(container, bg="#FFFFFF", bd=0, relief="flat", 
                       highlightbackground="#235A6F", highlightthickness=6)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Ícono de café más grande
        tk.Label(card, text="☕", font=("Segoe UI Emoji", 120, "bold"), 
                bg="#FFFFFF", fg="#235A6F").pack(pady=(50, 20))

        tk.Label(card, text="CAFFÈ & MIGA", font=("Segoe UI", 42, "bold"), 
                bg="#FFFFFF", fg="#235A6F").pack(pady=(0, 10))
        
        tk.Label(card, text="Sistema de Ventas", font=("Segoe UI", 28, "bold"), 
                bg="#FFFFFF", fg="#7F8C8D").pack(pady=(0, 40))

        # Campos de entrada más grandes
        tk.Label(card, text="Usuario", font=("Segoe UI", 22, "bold"), 
                bg="#FFFFFF", fg="#235A6F", anchor="w").pack(fill="x", padx=80)
        entry_usuario = tk.Entry(card, font=("Segoe UI", 24), width=20, bd=0, relief="flat", 
                               highlightbackground="#235A6F", justify="center", 
                               bg="#F4F6F7", fg="#222", highlightthickness=3)
        entry_usuario.pack(padx=80, pady=(10, 25))
        
        tk.Label(card, text="Contraseña", font=("Segoe UI", 22, "bold"), 
                bg="#FFFFFF", fg="#235A6F", anchor="w").pack(fill="x", padx=80)
        entry_contrasena = tk.Entry(card, show="*", font=("Segoe UI", 24), width=20, bd=0, relief="flat", 
                                  highlightbackground="#235A6F", justify="center", 
                                  bg="#F4F6F7", fg="#222", highlightthickness=3)
        entry_contrasena.pack(padx=80, pady=(10, 40))

        def verificar_login(event=None):
            if entry_usuario.get() == usuario_valido and entry_contrasena.get() == contrasena_valida:
                self.show_menu()
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

        entry_usuario.bind("<Return>", verificar_login)
        entry_contrasena.bind("<Return>", verificar_login)

        # Botón de entrada más grande
        tk.Button(
            card, text="🔑 ENTRAR AL SISTEMA", command=verificar_login,
            bg="#235A6F", fg="white", font=("Segoe UI", 28, "bold"),
            width=20, height=2, bd=0, activebackground="#183B4A", activeforeground="white",
            cursor="hand2", relief="raised", highlightthickness=0
        ).pack(pady=30)

        # Información adicional
        tk.Label(card, text="Presiona Enter para acceder", font=("Segoe UI", 12), 
                bg="#FFFFFF", fg="#95A5A6").pack(pady=(0, 50))

    def show_menu(self):
        self.clear_frames()
        frame = tk.Frame(self, bg="#235A6F")
        frame.pack(fill="both", expand=True)
        self.frames["menu"] = frame

        # Frame principal que se ajusta al tamaño completo
        main_frame = tk.Frame(frame, bg="#235A6F")
        main_frame.pack(fill="both", expand=True, padx=40, pady=30)

        # Título principal
        title_frame = tk.Frame(main_frame, bg="#FFFFFF", relief="flat", bd=0)
        title_frame.pack(fill="x", pady=(0, 30))

        tk.Label(
            title_frame,
            text="☕ CAFFÈ & MIGA - SISTEMA DE VENTAS ☕",
            font=("Segoe UI", 32, "bold"),
            bg="#FFFFFF",
            fg="#235A6F",
            pady=20
        ).pack()

        # Contenedor principal con dos columnas responsivas
        content_container = tk.Frame(main_frame, bg="#235A6F")
        content_container.pack(fill="both", expand=True)

        # Columna izquierda - Funciones principales (60% del ancho)
        left_section = tk.Frame(content_container, bg="#FFFFFF", relief="groove", bd=3)
        left_section.pack(side="left", fill="both", expand=True, padx=(0, 20))

        tk.Label(
            left_section,
            text="📋 FUNCIONES PRINCIPALES",
            font=("Segoe UI", 20, "bold"),
            bg="#FFFFFF",
            fg="#235A6F",
            pady=15
        ).pack()

        # Grid de botones principales más grande
        buttons_frame = tk.Frame(left_section, bg="#FFFFFF")
        buttons_frame.pack(fill="both", expand=True, padx=30, pady=20)

        botones = [
            ("🛒 Generar Compra", self.show_compra, "#27AE60"),
            ("🌐 Pedidos en Línea", self.show_pedidos_online, "#3498DB"),
            ("📦 Ver Inventario", self.show_inventario, "#9B59B6"),
            ("📋 Historial de Tickets", self.show_historial, "#E67E22"),
            ("📊 Resumen de Ventas", self.show_ventas, "#F39C12"),
            ("💾 Ver Ventas (DB)", self.show_ventas_db, "#34495E"),
        ]
        
        # Organizar botones en grid 2x3 para mejor uso del espacio
        for idx, (texto, comando, color) in enumerate(botones):
            row = idx // 2
            col = idx % 2
            
            tk.Button(
                buttons_frame,
                text=texto,
                command=comando,
                font=("Segoe UI", 18, "bold"),
                width=20,
                height=3,
                bg=color,
                fg="white",
                bd=0,
                activebackground="#2C3E50",
                activeforeground="white",
                cursor="hand2",
                highlightthickness=0,
                relief="raised"
            ).grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

        # Configurar peso de las columnas para que se expandan
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)

        # Columna derecha - Monitoreo y salir (40% del ancho)
        right_section = tk.Frame(content_container, bg="#FFFFFF", relief="groove", bd=3)
        right_section.pack(side="right", fill="both", expand=True)

        # SECCIÓN DE MONITOREO
        monitor_section = tk.Frame(right_section, bg="#FFFFFF")
        monitor_section.pack(fill="x", padx=20, pady=20)

        tk.Label(
            monitor_section,
            text="🔔 MONITOREO DE PEDIDOS WEB",
            font=("Segoe UI", 16, "bold"),
            bg="#FFFFFF",
            fg="#E67E22",
            pady=10
        ).pack()

        # Frame para botones de monitoreo más grandes
        monitor_buttons = tk.Frame(monitor_section, bg="#FFFFFF")
        monitor_buttons.pack(pady=15)

        tk.Button(
            monitor_buttons,
            text="▶️ INICIAR\nMONITOREO",
            command=self.iniciar_monitoreo_pedidos,
            font=("Segoe UI", 14, "bold"),
            width=15,
            height=4,
            bg="#27AE60",
            fg="white",
            bd=0,
            activebackground="#229954",
            activeforeground="white",
            cursor="hand2",
            highlightthickness=0,
            relief="raised"
        ).pack(side="left", padx=10)

        tk.Button(
            monitor_buttons,
            text="⏹️ DETENER\nMONITOREO",
            command=self.detener_monitoreo_pedidos,
            font=("Segoe UI", 14, "bold"),
            width=15,
            height=4,
            bg="#E74C3C",
            fg="white",
            bd=0,
            activebackground="#922B21",
            activeforeground="white",
            cursor="hand2",
            highlightthickness=0,
            relief="raised"
        ).pack(side="left", padx=10)

        # Estado del monitoreo más visible
        self.estado_monitoreo_label = tk.Label(
            monitor_section,
            text="⭕ MONITOREO: DETENIDO",
            font=("Segoe UI", 14, "bold"),
            bg="#FFFFFF",
            fg="#95A5A6",
            pady=10
        )
        self.estado_monitoreo_label.pack()

        # SECCIÓN DE SALIR más prominente
        exit_section = tk.Frame(right_section, bg="#E74C3C", relief="groove", bd=3)
        exit_section.pack(fill="x", padx=20, pady=(50, 20))

        tk.Label(
            exit_section,
            text="⚠️ SALIR DEL SISTEMA ⚠️",
            font=("Segoe UI", 18, "bold"),
            bg="#E74C3C",
            fg="white",
            pady=15
        ).pack()

        tk.Button(
            exit_section,
            text="🚪 SALIR DEL PROGRAMA",
            command=self.destroy,
            font=("Segoe UI", 20, "bold"),
            width=20,
            height=3,
            bg="#C0392B",
            fg="white",
            bd=0,
            activebackground="#922B21",
            activeforeground="white",
            cursor="hand2",
            highlightthickness=0,
            relief="raised"
        ).pack(pady=20)

        # Información del sistema en la parte inferior
        info_frame = tk.Frame(right_section, bg="#FFFFFF")
        info_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(
            info_frame,
            text=f"Sistema iniciado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            font=("Segoe UI", 10),
            bg="#FFFFFF",
            fg="#7F8C8D"
        ).pack()

        # Configurar el peso de las columnas principales
        content_container.grid_rowconfigure(0, weight=1)
        content_container.grid_columnconfigure(0, weight=3)  # Columna izquierda más ancha
        content_container.grid_columnconfigure(1, weight=2)  # Columna derecha

    def show_inventario(self):
        self.clear_frames()
        frame = tk.Frame(self, bg="#F4F6F7")
        frame.pack(fill="both", expand=True)
        self.frames["inventario"] = frame

        # Canvas + scrollbar para inventario
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

        # Card centrado y ancho fijo
        card = tk.Frame(
            scrollable_frame,
            bg="#FFFFFF",
            bd=0,
            relief="flat",
            highlightbackground="#235A6F",
            highlightthickness=4,
            width=900  # O prueba con 800 si tu ventana es más pequeña
        )
        card.pack(pady=40)
        # No uses card.pack_propagate(False)

        tk.Label(card, text="Inventario", font=("Segoe UI", 28, "bold"), bg="#FFFFFF", fg="#235A6F").pack(pady=20)

        form_frame = tk.Frame(card, bg="#FFFFFF")
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Producto:", bg="#FFFFFF", font=("Segoe UI", 16, "bold"), fg="#235A6F", anchor="center", width=14).grid(row=0, column=0, padx=8, pady=8)
        entry_producto = tk.Entry(form_frame, font=("Segoe UI", 15), justify="center", bd=0, relief="flat", bg="#F4F6F7", fg="#222", highlightthickness=2, highlightbackground="#235A6F")
        entry_producto.grid(row=0, column=1, padx=8, pady=8)

        tk.Label(form_frame, text="Unidades:", bg="#FFFFFF", font=("Segoe UI", 16, "bold"), fg="#235A6F", anchor="center", width=14).grid(row=1, column=0, padx=8, pady=8)
        entry_unidades = tk.Entry(form_frame, font=("Segoe UI", 15), justify="center", bd=0, relief="flat", bg="#F4F6F7", fg="#222", highlightthickness=2, highlightbackground="#235A6F")
        entry_unidades.grid(row=1, column=1, padx=8, pady=8)

        tk.Label(form_frame, text="Precio:", bg="#FFFFFF", font=("Segoe UI", 16, "bold"), fg="#235A6F", anchor="center", width=14).grid(row=2, column=0, padx=8, pady=8)
        entry_precio = tk.Entry(form_frame, font=("Segoe UI", 15), justify="center", bd=0, relief="flat", bg="#F4F6F7", fg="#222", highlightthickness=2, highlightbackground="#235A6F")
        entry_precio.grid(row=2, column=1, padx=8, pady=8)

        tk.Label(form_frame, text="Tipo de Unidad:", bg="#FFFFFF", font=("Segoe UI", 16, "bold"), fg="#235A6F", anchor="center", width=14).grid(row=3, column=0, padx=8, pady=8)
        unidad_var = tk.StringVar(value="Unidad")
        opciones_unidad = ["Unidad", "Sin control"]
        tk.OptionMenu(form_frame, unidad_var, *opciones_unidad).grid(row=3, column=1, padx=8, pady=8)

        def agregar_producto():
            producto = entry_producto.get().strip()
            try:
                unidades = int(entry_unidades.get())
                precio = float(entry_precio.get())
            except ValueError:
                messagebox.showerror("Error", "Unidades o precio inválidos.")
                return

            if not producto:
                messagebox.showerror("Error", "Nombre de producto vacío.")
                return

            tipo_unidad = unidad_var.get()
            df = cargar_inventario()
            if "TipoUnidad" not in df.columns:
                df["TipoUnidad"] = "Unidad"
            if producto in df["Producto"].values:
                df.loc[df["Producto"] == producto, "Unidades"] += unidades
                df.loc[df["Producto"] == producto, "TipoUnidad"] = tipo_unidad
                df.loc[df["Producto"] == producto, "Precio"] = precio
            else:
                nueva_fila = pd.DataFrame([[producto, unidades, precio, tipo_unidad]], columns=["Producto", "Unidades", "Precio", "TipoUnidad"])
                df = pd.concat([df, nueva_fila], ignore_index=True)

            guardar_inventario(df)
            messagebox.showinfo("Éxito", "Producto agregado correctamente.")
            entry_producto.delete(0, tk.END)
            entry_unidades.delete(0, tk.END)
            entry_precio.delete(0, tk.END)
            unidad_var.set("Unidad")
            mostrar_tabla()

        tk.Button(card, text="Agregar", command=agregar_producto,
                  bg="#27AE60", fg="white", font=("Segoe UI", 16, "bold"), width=15, bd=0, activebackground="#229954", activeforeground="white", cursor="hand2").pack(pady=10)

        # --- Tabla con scroll propio ---
        tabla_canvas = tk.Canvas(card, bg="#F4F6F7", highlightthickness=0, width=940, height=260)
        tabla_scroll = tk.Scrollbar(card, orient="vertical", command=tabla_canvas.yview)
        tabla_canvas.pack(side="left", fill="both", expand=False, padx=(20,0), pady=10)
        tabla_scroll.pack(side="right", fill="y", pady=10)
        tabla_canvas.configure(yscrollcommand=tabla_scroll.set)

        tabla_frame = tk.Frame(tabla_canvas, bg="#F4F6F7")
        tabla_canvas.create_window((0, 0), window=tabla_frame, anchor="nw")

        def on_tabla_configure(event):
            tabla_canvas.configure(scrollregion=tabla_canvas.bbox("all"))
        tabla_frame.bind("<Configure>", on_tabla_configure)

        def mostrar_tabla():
            for widget in tabla_frame.winfo_children():
                widget.destroy()
            df = cargar_inventario()
            if "TipoUnidad" not in df.columns:
                df["TipoUnidad"] = "Unidad"
            df = df[df["Producto"].notna() & (df["Producto"].astype(str).str.strip() != "")]
            encabezados = ["Producto", "Unidades", "Precio", "Tipo de Unidad"]
            for col, texto in enumerate(encabezados):
                tk.Label(tabla_frame, text=texto, font=("Segoe UI", 14, "bold"), bg="#235A6F", fg="white", width=22, borderwidth=0, relief="flat", pady=8).grid(row=0, column=col, padx=1, pady=1, sticky="nsew")
                tabla_frame.grid_columnconfigure(col, weight=1)
            for i, row in df.iterrows():
                color_fila = "#FFFFFF" if i % 2 == 0 else "#F4F6F7"
                tk.Label(tabla_frame, text=row["Producto"], font=("Segoe UI", 12), bg=color_fila, fg="#222", width=22, borderwidth=0, relief="flat", pady=6).grid(row=i+1, column=0, padx=1, pady=1, sticky="nsew")
                tk.Label(tabla_frame, text=row["Unidades"], font=("Segoe UI", 12), bg=color_fila, fg="#222", width=22, borderwidth=0, relief="flat", pady=6).grid(row=i+1, column=1, padx=1, pady=1, sticky="nsew")
                tk.Label(tabla_frame, text=row["Precio"], font=("Segoe UI", 12), bg=color_fila, fg="#222", width=22, borderwidth=0, relief="flat", pady=6).grid(row=i+1, column=2, padx=1, pady=1, sticky="nsew")
                tk.Label(tabla_frame, text=row["TipoUnidad"], font=("Segoe UI", 12), bg=color_fila, fg="#222", width=22, borderwidth=0, relief="flat", pady=6).grid(row=i+1, column=3, padx=1, pady=1, sticky="nsew")

        mostrar_tabla()

        # --- Botón siempre abajo ---
        tk.Button(
            card,
            text="Volver al Menú",
            command=self.show_menu,
            bg="#235A6F",
            fg="white",
            font=("Segoe UI", 16, "bold"),
            bd=0,
            activebackground="#183B4A",
            activeforeground="white",
            cursor="hand2",
            highlightthickness=0
        ).pack(pady=18)

    def show_compra(self):
        self.clear_frames()
        frame = tk.Frame(self, bg="#FFFFFF")
        frame.pack(fill="both", expand=True)
        self.frames["compra"] = frame

        # Carga el inventario solo una vez y guárdalo en memoria
        self.productos = cargar_inventario()

        # Canvas + scrollbar para productos y ticket
        canvas = tk.Canvas(frame, bg="#FFFFFF", highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        scrollable_frame = tk.Frame(canvas, bg="#FFFFFF")
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scrollable_frame.bind("<Configure>", on_configure)

        productos = cargar_inventario()
        self.entradas_productos = {}

        tk.Label(scrollable_frame, text="Seleccione los productos:", font=("Arial", 16, "bold"), bg="#FFFFFF").pack(pady=10)

        productos_por_fila = 3  # Cambia a 2 o 4 si prefieres más o menos columnas
        productos_frame = tk.Frame(scrollable_frame, bg="#FFFFFF")
        productos_frame.pack(pady=10)

        for idx, row in productos.iterrows():
            col = idx % productos_por_fila
            fila = idx // productos_por_fila
            frame_prod = tk.Frame(productos_frame, bg="#FFFFFF", pady=5, padx=5, relief="groove", bd=1)
            frame_prod.grid(row=fila, column=col, padx=8, pady=8, sticky="nsew")
            tk.Label(frame_prod, text=f"{row['Producto']} (${row['Precio']})", font=("Arial", 14),
                     bg="#FFFFFF", width=18, anchor="w").pack(side="top", pady=2)

            cantidad_var = tk.IntVar(value=0)

            def aumentar(cvar=cantidad_var):
                cvar.set(cvar.get() + 1)
                self.previsualizar_ticket()  # <-- Esto es lo importante

            def disminuir(cvar=cantidad_var):
                if cvar.get() > 0:
                    cvar.set(cvar.get() - 1)
                    self.previsualizar_ticket()

            tk.Button(frame_prod, text="-", font=("Arial", 12), width=2,
                      command=disminuir).pack(side="left", padx=2)
            tk.Label(frame_prod, textvariable=cantidad_var, font=("Arial", 14), width=4, bg="#F0F0F0").pack(side="left", padx=2)
            tk.Button(frame_prod, text="+", font=("Arial", 12), width=2,
                      command=aumentar).pack(side="left", padx=2)

            self.entradas_productos[row["Producto"]] = cantidad_var

        tk.Label(scrollable_frame, text="Método de Pago:", font=("Arial", 14), bg="#FFFFFF").pack(pady=10)
        self.metodo_pago = tk.StringVar(value="Efectivo")
        for pago in ["Efectivo", "Tarjeta"]:
            tk.Radiobutton(scrollable_frame, text=pago, variable=self.metodo_pago, value=pago,
                           font=("Arial", 13), bg="#FFFFFF", command=self.previsualizar_ticket).pack()

        # Campo para billete recibido y cambio
        self.billete_recibido_var = tk.StringVar()
        self.cambio_var = tk.StringVar(value="Cambio: $0.00")

        def actualizar_cambio(*args):
            self.previsualizar_ticket()

        frame_pago = tk.Frame(scrollable_frame, bg="#FFFFFF")
        frame_pago.pack(pady=5)
        tk.Label(frame_pago, text="Billete recibido:", font=("Arial", 13), bg="#FFFFFF").pack(side="left")
        entry_billete = tk.Entry(frame_pago, textvariable=self.billete_recibido_var, font=("Arial", 13), width=10)
        entry_billete.pack(side="left", padx=5)
        tk.Label(frame_pago, textvariable=self.cambio_var, font=("Arial", 13), bg="#FFFFFF", fg="#229954").pack(side="left", padx=10)
        self.billete_recibido_var.trace_add("write", actualizar_cambio)

        # Vista previa del ticket
        ticket_frame = tk.Frame(scrollable_frame, bg="#FFFFFF")
        ticket_frame.pack(pady=10)

        scroll_ticket = tk.Scrollbar(ticket_frame, orient="vertical")
        self.ticket_texto = tk.Text(ticket_frame, width=60, height=15, font=("Courier", 12), bg="#F2F4F5", yscrollcommand=scroll_ticket.set)
        scroll_ticket.config(command=self.ticket_texto.yview)
        self.ticket_texto.pack(side="left", fill="both", expand=True)
        scroll_ticket.pack(side="right", fill="y")
        self.ticket_texto.lift()

        tk.Button(scrollable_frame, text="Generar Ticket", command=self.generar_ticket,
                  bg="#27AE60", fg="white", font=("Arial", 16)).pack(pady=15)

        tk.Button(
            scrollable_frame,
            text="Registrar Venta SIN Imprimir",
            command=lambda: self.generar_ticket(imprimir=False),
            bg="#F1C40F",
            fg="black",
            font=("Arial", 16)
        ).pack(pady=5)

        tk.Button(
            scrollable_frame,
            text="Volver al Menú",
            command=self.show_menu,
            bg="#3498DB",
            fg="white",
            font=("Arial", 16, "bold"),
            width=25,
            height=2
        ).pack(pady=10)

        self.previsualizar_ticket()

        from datetime import datetime

        def aplicar_promocion_frappes():
            hoy = datetime.now().weekday()
            if hoy not in [1, 4]:
                messagebox.showinfo("Promoción no disponible", "La promoción solo aplica los martes y viernes.")
                return

            frappes = [k for k in self.entradas_productos if "frappe" in k.lower()]
            total_frappes = sum(self.entradas_productos[k].get() for k in frappes)
            if total_frappes < 2:
                messagebox.showinfo("Promoción", "Debes seleccionar al menos 2 frappes para aplicar la promoción.")
                return

            self.promocion_frappes_activa = True
            messagebox.showinfo("Promoción aplicada", "¡Promoción 2x$100 activada para frappes!\nRecuerda que solo aplica a pares de frappes.")
            self.previsualizar_ticket()

        tk.Button(scrollable_frame, text="Aplicar Promoción 2x$100 Frappes (Mar/Vie)", font=("Arial", 13), bg="#229954", fg="white", command=aplicar_promocion_frappes).pack(pady=10)

    def previsualizar_ticket(self):
        try:
            productos = self.productos  # Usa el inventario ya cargado en memoria
            total = 0
            ancho_ticket = 32  # caracteres aprox para 58mm

            ticket = self.centrar("Caffè & Miga", ancho_ticket) + "\n"
            ticket += self.centrar("--- TICKET DE COMPRA ---", ancho_ticket) + "\n"
            ticket += self.centrar(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ancho_ticket) + "\n\n"
            ticket += f"{'Producto':<12}{'Cant':>5}{'Precio':>8}\n"
            ticket += "-" * ancho_ticket + "\n"

            # --- BLOQUE PARA PROMO ---
            if getattr(self, "promocion_frappes_activa", False):
                frappes = []
                otros_productos = []
                for producto, cantidad_var in self.entradas_productos.items():
                    cantidad = cantidad_var.get()
                    if cantidad > 0:
                        if "frappe" in producto.lower():
                            frappes.extend([producto] * cantidad)
                        else:
                            otros_productos.append((producto, cantidad))
                pares = len(frappes) // 2

                # Frappes en promo
                for i in range(pares * 2):
                    frappe_nombre = frappes[i]
                    ticket += f"{frappe_nombre[:12]:<12}{1:>5}{'PROMO':>8}\n"
                    total += 50

                # Frappes restantes a precio normal
                for i in range(pares * 2, len(frappes)):
                    frappe_nombre = frappes[i]
                    precio_normal = float(productos[productos["Producto"] == frappe_nombre]["Precio"])
                    ticket += f"{frappe_nombre[:12]:<12}{1:>5}{precio_normal:>8.2f}\n"
                    total += precio_normal

                # Otros productos
                for producto, cantidad in otros_productos:
                    precio = float(productos[productos["Producto"] == producto]["Precio"])
                    ticket += f"{producto[:12]:<12}{cantidad:>5}{precio:>8.2f}\n"
                    total += cantidad * precio
            else:
                for producto, cantidad_var in self.entradas_productos.items():
                    cantidad = cantidad_var.get()
                    if cantidad > 0:
                        fila = productos[productos["Producto"] == producto]
                        if not fila.empty:
                            fila = fila.iloc[0]
                            precio = fila["Precio"] if "Precio" in fila and pd.notna(fila["Precio"]) else 0
                            ticket += f"{producto[:12]:<12}{cantidad:>5}{precio:>8.2f}\n"
                            total += cantidad * precio

            ticket += "-" * ancho_ticket + "\n"
            ticket += self.centrar(f"TOTAL: ${total:.2f}", ancho_ticket) + "\n"
            ticket += self.centrar(f"Método de Pago: {self.metodo_pago.get()}", ancho_ticket) + "\n"

            # Mostrar cambio solo si es efectivo
            cambio = 0
            if self.metodo_pago.get() == "Efectivo":
                try:
                    billete = float(self.billete_recibido_var.get())
                    cambio = billete - total
                    if cambio < 0:
                        self.cambio_var.set("Cambio: $0.00")
                        ticket += self.centrar("Recibido: $0.00", ancho_ticket) + "\n"
                        ticket += self.centrar("Cambio: $0.00", ancho_ticket) + "\n"
                    else:
                        self.cambio_var.set(f"Cambio: ${cambio:.2f}")
                        ticket += self.centrar(f"Recibido: ${billete:.2f}", ancho_ticket) + "\n\n"
                        ticket += self.centrar(f"Cambio: ${cambio:.2f}", ancho_ticket) + "\n"
                except ValueError:
                    self.cambio_var.set("Cambio: $0.00")
                    ticket += self.centrar("Recibido: $0.00", ancho_ticket) + "\n"
                    ticket += self.centrar("Cambio: $0.00", ancho_ticket) + "\n"
            else:
                self.cambio_var.set("Cambio: $0.00")

            ticket += "-" * ancho_ticket + "\n\n"
            ticket += self.centrar("¡Gracias por su compra!", ancho_ticket) + "\n"

            self.ticket_texto.delete("1.0", tk.END)
            self.ticket_texto.insert(tk.END, ticket)
        except Exception as e:
            messagebox.showerror("Error", f"Error en previsualizar_ticket:\n{e}")
            logging.error(f"Error en previsualizar_ticket: {e}")

    def centrar(self, texto, ancho=32):
        return texto.center(ancho)

    def generar_ticket(self, imprimir=True):
        productos = cargar_inventario()
        total = 0
        ancho_ticket = 32

        # Prepara filas_actualizar para guardar en la base de datos
        filas_actualizar = []
        for producto, cantidad_var in self.entradas_productos.items():
            cantidad = cantidad_var.get()
            if cantidad > 0:
                filas_actualizar.append((producto, cantidad))

        # --- GUARDAR EN BASE DE DATOS ---
        fecha_venta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.promocion_frappes_activa:
            from collections import Counter
            frappes = []
            otros_productos = []
            for producto, cantidad in filas_actualizar:
                if "frappe" in producto.lower():
                    frappes.extend([producto] * cantidad)
                else:
                    otros_productos.append((producto, cantidad))
            pares = len(frappes) // 2

            # Agrupa frappes en promo
            frappe_counter = Counter(frappes[:pares * 2])
            for frappe_nombre, cantidad in frappe_counter.items():
                guardar_ticket_sqlite(fecha_venta, frappe_nombre, cantidad, 50, self.metodo_pago.get())

            # Frappes restantes a precio normal
            for frappe_nombre in frappes[pares * 2:]:
                precio_normal = float(productos[productos["Producto"] == frappe_nombre]["Precio"])
                guardar_ticket_sqlite(fecha_venta, frappe_nombre, 1, precio_normal, self.metodo_pago.get())

            # Otros productos
            for producto, cantidad in otros_productos:
                precio = float(productos[productos["Producto"] == producto]["Precio"])
                guardar_ticket_sqlite(fecha_venta, producto, cantidad, precio, self.metodo_pago.get())
        else:
            for producto, cantidad in filas_actualizar:
                precio = float(productos[productos["Producto"] == producto]["Precio"])
                guardar_ticket_sqlite(fecha_venta, producto, cantidad, precio, self.metodo_pago.get())

        # Solo imprime y guarda PDF si imprimir=True
        if imprimir:
            try:
                # Crear lista de productos vendidos para el ticket
                productos_vendidos = []
                for producto, cantidad in filas_actualizar:
                    precio = float(productos[productos["Producto"] == producto]["Precio"])
                    productos_vendidos.append((producto, cantidad, precio))
                
                self.generar_e_imprimir_ticket(fecha_venta, productos_vendidos, total, self.metodo_pago.get())
                self.actualizar_inventario(filas_actualizar)
            except Exception as e:
                logging.error(f"Error en impresión o actualización de inventario: {e}")
                messagebox.showwarning("Error", f"Error al imprimir o actualizar inventario: {e}")

        # Limpiar selección de productos y promoción
        for cantidad_var in self.entradas_productos.values():
            cantidad_var.set(0)
        self.promocion_frappes_activa = False
        # ELIMINADO: self.pedidos_manager = PedidosOnlineManager(self)
        self.billete_recibido_var.set("")
        self.cambio_var.set("Cambio: $0.00")

        self.alerta_bajo_inventario()
        self.show_compra()

    def show_historial(self):
        self.clear_frames()
        frame = tk.Frame(self, bg="#FFFFFF")
        frame.pack(fill="both", expand=True)
        self.frames["historial"] = frame

        # Filtros para el historial
        filtro_frame = tk.Frame(frame, bg="#E8F8F5")
        filtro_frame.pack(fill="x", pady=5)

        tk.Label(filtro_frame, text="Producto:", bg="#E8F8F5").pack(side="left")
        entry_producto = tk.Entry(filtro_frame, width=15)
        entry_producto.pack(side="left", padx=2)
        tk.Label(filtro_frame, text="Pago:", bg="#E8F8F5").pack(side="left")
        entry_pago = tk.Entry(filtro_frame, width=10)
        entry_pago.pack(side="left", padx=2)

        # Frame para la tabla
        tabla_frame = tk.Frame(frame, bg="#FFFFFF")
        tabla_frame.pack(fill="both", expand=True)

        def cargar_historial():
            for widget in tabla_frame.winfo_children():
                widget.destroy()
            df = obtener_ventas()
            if entry_producto.get():
                df = df[df["producto"].str.contains(entry_producto.get(), case=False, na=False)]
            if entry_pago.get():
                df = df[df["pago"].str.contains(entry_pago.get(), case=False, na=False)]
            if df.empty:
                tk.Label(tabla_frame, text="No hay tickets registrados.", font=("Arial", 14), bg="#FFFFFF").pack(pady=20)
                return

            columns = ["id", "fecha", "producto", "cantidad", "precio", "pago", "estado", "motivo_cancelacion"]
            tree = ttk.Treeview(tabla_frame, columns=columns, show="headings", height=20)
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor="center")
            for _, row in df.iterrows():
                tree.insert("", "end", values=[row.get(col, "") for col in columns])
            tree.pack(fill="both", expand=True)

            scrollbar = tk.Scrollbar(tabla_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")

            def abrir_pdf_seleccion():
                selected = tree.selection()
                if not selected:
                    messagebox.showwarning("Selecciona un ticket", "Selecciona un ticket para abrir su PDF.")
                    return
                item = tree.item(selected[0])
                fecha_str = item["values"][1]  # El campo fecha
                try:
                    # Intenta con segundos
                    fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
                    nombre_pdf = f"ticket_{fecha_dt.strftime('%Y%m%d_%H%M%S')}.pdf"
                except Exception:
                    try:
                        # Intenta sin segundos
                        fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
                        nombre_pdf = f"ticket_{fecha_dt.strftime('%Y%m%d_%H%M')}.pdf"
                    except Exception as e:
                        messagebox.showerror("Error al abrir PDF", f"No se pudo interpretar la fecha:\n{e}")
                        return

                ruta_pdf = os.path.join("tickets", nombre_pdf)
                if os.path.exists(ruta_pdf):
                    os.startfile(ruta_pdf)
                    return
                else:
                    # Si no existe, busca cualquier PDF que empiece con ticket_YYYYMMDD_HHMM
                    carpeta = "tickets"
                    base = f"ticket_{fecha_dt.strftime('%Y%m%d_%H%M')}"
                    candidatos = [f for f in os.listdir(carpeta) if f.startswith(base) and f.endswith(".pdf")]
                    if candidatos:
                        os.startfile(os.path.join(carpeta, candidatos[0]))
                        return
                    else:
                        messagebox.showwarning("PDF no encontrado", f"No se encontró el PDF:\n{ruta_pdf}")

            def eliminar_seleccion():
                selected = tree.selection()
                if not selected:
                    messagebox.showwarning("Selecciona una venta", "Selecciona una venta para eliminar.")
                    return
                item = tree.item(selected[0])
                id_ticket = item["values"][0]
                confirm = messagebox.askyesno("Eliminar venta", "¿Seguro que deseas eliminar esta venta?\nEsta acción no se puede deshacer.")
                if confirm:
                    eliminar_venta_db(id_ticket)
                    messagebox.showinfo("Venta eliminada", "La venta ha sido eliminada (marcada como cancelada).")
                    cargar_historial()

            btn_frame = tk.Frame(tabla_frame, bg="#FFFFFF")
            btn_frame.pack(pady=10)
            tk.Button(btn_frame, text="Abrir Ticket en PDF", command=abrir_pdf_seleccion,
                      bg="#58D68D", fg="white", font=("Arial", 12)).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Eliminar Venta Seleccionada", command=eliminar_seleccion,
                      bg="#E74C3C", fg="white", font=("Arial", 12)).pack(side="left", padx=5)

        tk.Button(filtro_frame, text="Buscar", command=cargar_historial, bg="#85C1E9").pack(side="left", padx=5)

        cargar_historial()

        tk.Button(frame, text="Volver al Menú", command=self.show_menu,
                  bg="#3498DB", fg="white", font=("Arial", 12)).pack(pady=10)

    def show_ventas(self):
        self.clear_frames()
        frame = tk.Frame(self, bg="#FFFFFF")
        frame.pack(fill="both", expand=True)
        self.frames["ventas"] = frame

        df = obtener_ventas()
        if df.empty:
            tk.Label(frame, text="No hay ventas registradas aún.", font=("Arial", 14), bg="#FFFFFF").pack(pady=20)
        else:
            df["fecha"] = pd.to_datetime(df["fecha"])
            hoy = pd.Timestamp.now().normalize()
            semana = hoy - pd.Timedelta(days=hoy.weekday())
            mes = hoy.replace(day=1)

            ventas_dia = df[df["fecha"].dt.normalize() == hoy]
            ventas_semana = df[df["fecha"].dt.normalize() >= semana]
            ventas_mes = df[df["fecha"].dt.normalize() >= mes]

            def resumen_ventas(df_ventas, titulo):
                df_ventas = df_ventas[df_ventas["estado"] == "Activo"]
                total = (df_ventas["precio"] * df_ventas["cantidad"]).sum()
                productos = df_ventas.groupby("producto")["cantidad"].sum()
                resumen = f"{titulo}\nTotal: ${total:.2f}\nProductos vendidos:\n"
                for prod, cant in productos.items():
                    resumen += f"  {prod}: {cant}\n"
                return resumen + "\n"

            # --- Cuadro de texto con scrollbar ---
            texto_frame = tk.Frame(frame, bg="#F2F4F5")
            texto_frame.pack(fill="both", expand=True, padx=10, pady=10)

            texto = tk.Text(texto_frame, font=("Courier", 12), bg="#F2F4F5", wrap="none", height=30)
            texto.pack(side="left", fill="both", expand=True)

            scrollbar_texto = tk.Scrollbar(texto_frame, orient="vertical", command=texto.yview)
            scrollbar_texto.pack(side="right", fill="y")
            texto.configure(yscrollcommand=scrollbar_texto.set)

            # Resúmenes con separación visual
            texto.insert(tk.END, resumen_ventas(ventas_dia, "Ventas del Día"))
            texto.insert(tk.END, "-"*40 + "\n")
            texto.insert(tk.END, resumen_ventas(ventas_semana, "Ventas de la Semana"))
            texto.insert(tk.END, "-"*40 + "\n")
            mes_actual = datetime.now().strftime("%B %Y").capitalize()
            texto.insert(tk.END, resumen_ventas(ventas_mes, f"Ventas del Mes ({mes_actual})"))
            texto.insert(tk.END, "-"*40 + "\n")

            # --- RESUMEN ACUMULADO ---
            texto.insert(tk.END, resumen_ventas(df, "Ventas Totales Acumuladas"))
            texto.insert(tk.END, "-"*40 + "\n")

        tk.Button(frame, text="Volver al Menú", command=self.show_menu,
                  bg="#3498DB", fg="white", font=("Arial", 12)).pack(pady=10)

    def show_ventas_db(self):
        self.clear_frames()
        frame = tk.Frame(self, bg="#FFFFFF")
        frame.pack(fill="both", expand=True)
        self.frames["ventas_db"] = frame

        df = obtener_ventas()
        df = df[df["estado"] == "Activo"]

        if df.empty:
            tk.Label(frame, text="No hay ventas registradas aún.", font=("Arial", 14), bg="#FFFFFF").pack(pady=20)
            tk.Button(frame, text="Volver al Menú", command=self.show_menu,
                      bg="#3498DB", fg="white", font=("Arial", 12)).pack(pady=10)
            return

        columns = list(df.columns)
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=25)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        for _, row in df.iterrows():
            tree.insert("", "end", values=[row[col] for col in columns])
        tree.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        def eliminar_seleccion():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Selecciona una venta", "Selecciona una venta para eliminar.")
                return
            item = tree.item(selected[0])
            id_ticket = item["values"][0]  # El primer valor es el ID
            confirm = messagebox.askyesno("Eliminar venta", "¿Seguro que deseas eliminar esta venta?\nEsta acción no se puede deshacer.")
            if confirm:
                eliminar_venta_db(id_ticket)
                messagebox.showinfo("Venta eliminada", "La venta ha sido eliminada (marcada como cancelada).")
                self.show_ventas_db()  # Refresca la vista

        tk.Button(frame, text="Eliminar Venta Seleccionada", command=eliminar_seleccion,
                  bg="#E74C3C", fg="white", font=("Arial", 12)).pack(pady=10)

        tk.Button(frame, text="Volver al Menú", command=self.show_menu,
                  bg="#3498DB", fg="white", font=("Arial", 12)).pack(pady=10)

    def respaldar_db(self):
        origen = "ventas.db"
        destino = os.path.join("backups", f"ventas_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        if not os.path.exists("backups"):
            os.makedirs("backups")
        shutil.copy(origen, destino)
        messagebox.showinfo("Respaldo", f"Respaldo guardado en {destino}")

    def respaldo_completo():
        """
        Realiza un respaldo de la base de datos, tickets PDF, inventario y el código fuente en la carpeta 'backups'.
        El archivo generado incluye: ventas.db, inventario.xlsx, todos los PDFs de tickets y cafeteria_sistema.py.
        """
        fecha_respaldo = datetime.now().strftime("%Y%m%d_%H%M%S")
        carpeta_backups = "backups"
        if not os.path.exists(carpeta_backups):
            os.makedirs(carpeta_backups)
        nombre_zip = os.path.join(carpeta_backups, f"respaldo_completo_{fecha_respaldo}.zip")
        with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
            # Base de datos
            if os.path.exists("ventas.db"):
                backup_zip.write("ventas.db")
            # Inventario
            if os.path.exists("inventario.xlsx"):
                backup_zip.write("inventario.xlsx")
            # Código fuente
            if os.path.exists("cafeteria_sistema.py"):
                backup_zip.write("cafeteria_sistema.py")
            # Tickets PDF
            carpeta_tickets = "tickets"
            if os.path.exists(carpeta_tickets):
                for archivo in os.listdir(carpeta_tickets):
                    ruta = os.path.join(carpeta_tickets, archivo)
                    if os.path.isfile(ruta) and archivo.lower().endswith(".pdf"):
                        backup_zip.write(ruta, os.path.join("tickets", archivo))
        messagebox.showinfo("Respaldo completo", f"Respaldo guardado en:\n{nombre_zip}")

    def respaldo_completo_semanal():
        """
        Realiza un respaldo semanal de la base de datos, tickets PDF, inventario y el código fuente en la carpeta 'backups'.
        El archivo generado incluye: ventas.db, inventario.xlsx, todos los PDFs de tickets y cafeteria_sistema.py.
        El nombre del archivo incluye el rango de la semana (ejemplo: semana_2024-06-24_a_2024-06-30.zip).
        """
        hoy = datetime.now()
        # Lunes de la semana actual
        inicio_semana = hoy - pd.Timedelta(days=hoy.weekday())
        # Domingo de la semana actual
        fin_semana = inicio_semana + pd.Timedelta(days=6)
        fecha_inicio = inicio_semana.strftime("%Y-%m-%d")
        fecha_fin = fin_semana.strftime("%Y-%m-%d")
        carpeta_backups = "backups"
        if not os.path.exists(carpeta_backups):
            os.makedirs(carpeta_backups)
        nombre_zip = os.path.join(
            carpeta_backups,
            f"respaldo_semana_{fecha_inicio}_a_{fecha_fin}.zip"
        )
        with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
            # Base de datos
            if os.path.exists("ventas.db"):
                backup_zip.write("ventas.db")
            # Inventario
            if os.path.exists("inventario.xlsx"):
                backup_zip.write("inventario.xlsx")
            # Código fuente
            if os.path.exists("cafeteria_sistema.py"):
                backup_zip.write("cafeteria_sistema.py")
            # Tickets PDF
            carpeta_tickets = "tickets"
            if os.path.exists(carpeta_tickets):
                for archivo in os.listdir(carpeta_tickets):
                    ruta = os.path.join(carpeta_tickets, archivo)
                    if os.path.isfile(ruta) and archivo.lower().endswith(".pdf"):
                        backup_zip.write(ruta, os.path.join("tickets", archivo))
        messagebox.showinfo(
            "Respaldo semanal",
            f"Respaldo de la semana {fecha_inicio} a {fecha_fin} guardado en:\n{nombre_zip}"
        )

    def show_pedidos_online(self):
        """Mostrar pedidos web desde la base de datos local"""
        # DEBUG: Agregar logs para diagnosticar
        try:
            print("🔍 DEBUG: Iniciando show_pedidos_online")
            
            self.clear_frames()
            frame = tk.Frame(self, bg="#F4F6F7")
            frame.pack(fill="both", expand=True)
            self.frames["pedidos_online"] = frame

            # Canvas + scrollbar para pedidos
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

            # Título principal
            tk.Label(scrollable_frame, text="🌐 PEDIDOS WEB EN LÍNEA", 
                    font=("Segoe UI", 28, "bold"), bg="#F4F6F7", fg="#E67E22").pack(pady=(20, 10))
            
            print("🔍 DEBUG: Verificando conexión BD...")
            # Verificar conexión con la base de datos
            if not self.pedidos_web_manager.test_connection():
                print("❌ DEBUG: Falló test_connection")
                error_frame = tk.Frame(scrollable_frame, bg="#FFFFFF", relief="groove", bd=3)
                error_frame.pack(fill="x", padx=40, pady=20)
                
                tk.Label(error_frame, text="❌ ERROR DE CONEXIÓN", 
                        font=("Segoe UI", 20, "bold"), bg="#FFFFFF", fg="#E74C3C").pack(pady=20)
                tk.Label(error_frame, text="No se puede acceder a la base de datos pos_pedidos.db", 
                        font=("Segoe UI", 14), bg="#FFFFFF", fg="#7F8C8D").pack(pady=10)
                tk.Button(error_frame, text="⬅️ Volver al Menú", command=self.show_menu,
                         bg="#95A5A6", fg="white", font=("Segoe UI", 16, "bold")).pack(pady=20)
                return

            print("✅ DEBUG: Conexión BD OK")
            
            # Obtener pedidos pendientes
            print("🔍 DEBUG: Obteniendo pedidos...")
            pedidos = self.pedidos_web_manager.get_web_orders()
            print(f"✅ DEBUG: Obtenidos {len(pedidos)} pedidos")
            
            # Panel de control
            control_frame = tk.Frame(scrollable_frame, bg="#FFFFFF", relief="groove", bd=3)
            control_frame.pack(fill="x", padx=40, pady=(0, 20))
            
            tk.Label(control_frame, text="🎛️ PANEL DE CONTROL", 
                    font=("Segoe UI", 18, "bold"), bg="#FFFFFF", fg="#235A6F").pack(pady=15)
            
            info_frame = tk.Frame(control_frame, bg="#FFFFFF")
            info_frame.pack(pady=10)
            
            tk.Label(info_frame, text=f"📊 Pedidos pendientes: {len(pedidos)}", 
                    font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg="#27AE60").pack(side="left", padx=20)
            
            tk.Button(info_frame, text="🔄 Actualizar", command=self.show_pedidos_online,
                     bg="#3498DB", fg="white", font=("Segoe UI", 12, "bold")).pack(side="left", padx=10)
            
            tk.Button(control_frame, text="⬅️ Volver al Menú", command=self.show_menu,
                     bg="#95A5A6", fg="white", font=("Segoe UI", 14, "bold")).pack(pady=15)

            if not pedidos:
                print("⚠️ DEBUG: No hay pedidos - mostrando mensaje")
                # No hay pedidos
                no_orders_frame = tk.Frame(scrollable_frame, bg="#FFFFFF", relief="groove", bd=3)
                no_orders_frame.pack(fill="x", padx=40, pady=20)
                
                tk.Label(no_orders_frame, text="✅ NO HAY PEDIDOS PENDIENTES", 
                        font=("Segoe UI", 20, "bold"), bg="#FFFFFF", fg="#27AE60").pack(pady=30)
                tk.Label(no_orders_frame, text="Todos los pedidos web han sido procesados", 
                        font=("Segoe UI", 14), bg="#FFFFFF", fg="#7F8C8D").pack(pady=10)
                return

            # Mostrar pedidos
            print(f"🔍 DEBUG: Creando widgets para {len(pedidos)} pedidos...")
            for idx, pedido in enumerate(pedidos):
                print(f"   Creando widget para pedido #{idx + 1}: {pedido['id']}")
                try:
                    self.create_order_widget(scrollable_frame, pedido, idx)
                    print(f"   ✅ Widget #{idx + 1} creado OK")
                except Exception as widget_error:
                    print(f"   ❌ Error en widget #{idx + 1}: {widget_error}")
            
            print("✅ DEBUG: show_pedidos_online completado")
            
        except Exception as e:
            print(f"❌ DEBUG: Error crítico en show_pedidos_online: {e}")
            import traceback
            traceback.print_exc()

    def create_order_widget(self, parent, order, index):
        """Crear widget para mostrar un pedido individual"""
        # DEBUG: Log del pedido que se está procesando
        print(f"🔍 DEBUG: Procesando pedido #{index + 1}")
        print(f"   ID: {order.get('id', 'SIN ID')}")
        print(f"   Cliente: {order.get('cliente_nombre', 'SIN NOMBRE')}")
        print(f"   Total: ${order.get('total', 0)}")
        print(f"   Items raw: {order.get('items', 'VACIO')[:100]}...")
        
        # Frame principal del pedido
        order_frame = tk.Frame(parent, bg="#FFFFFF", relief="groove", bd=3)
        order_frame.pack(fill="x", padx=40, pady=15)

        # Header del pedido
        header_frame = tk.Frame(order_frame, bg="#235A6F")
        header_frame.pack(fill="x")

        tk.Label(header_frame, text=f"📝 PEDIDO #{index + 1}", 
                font=("Segoe UI", 16, "bold"), bg="#235A6F", fg="white").pack(side="left", padx=20, pady=10)
        
        tk.Label(header_frame, text=f"💰 Total: ${order['total']:.2f}", 
                font=("Segoe UI", 14, "bold"), bg="#235A6F", fg="#F1C40F").pack(side="right", padx=20, pady=10)

        # Información del cliente
        info_frame = tk.Frame(order_frame, bg="#FFFFFF")
        info_frame.pack(fill="x", padx=20, pady=15)

        cliente_frame = tk.Frame(info_frame, bg="#F8F9FA", relief="flat", bd=2)
        cliente_frame.pack(fill="x", pady=(0, 10))

        # Mejorar el manejo de datos del cliente
        cliente_nombre = order.get('cliente_nombre', '') or 'Cliente Web'
        if not cliente_nombre or cliente_nombre.strip() == '':
            cliente_nombre = 'Cliente Web'
            
        cliente_telefono = order.get('cliente_telefono', '') or 'No especificado'
        if not cliente_telefono or cliente_telefono.strip() == '':
            cliente_telefono = 'No especificado'
            
        hora_recogida = order.get('hora_recogida', '') or 'No especificada'
        if not hora_recogida or hora_recogida.strip() == '':
            hora_recogida = 'No especificada'
            
        metodo_pago = order.get('metodo_pago', '') or 'mercado_pago'

        tk.Label(cliente_frame, text=f"👤 Cliente: {cliente_nombre}", 
                font=("Segoe UI", 12, "bold"), bg="#F8F9FA", fg="#235A6F").pack(anchor="w", padx=15, pady=5)
        tk.Label(cliente_frame, text=f"📞 Teléfono: {cliente_telefono}", 
                font=("Segoe UI", 12), bg="#F8F9FA", fg="#7F8C8D").pack(anchor="w", padx=15)
        tk.Label(cliente_frame, text=f"🕐 Hora de recogida: {hora_recogida}", 
                font=("Segoe UI", 12), bg="#F8F9FA", fg="#7F8C8D").pack(anchor="w", padx=15)
        tk.Label(cliente_frame, text=f"💳 Método de pago: {metodo_pago}", 
                font=("Segoe UI", 12), bg="#F8F9FA", fg="#7F8C8D").pack(anchor="w", padx=15, pady=(0, 5))

        # Items del pedido
        items_frame = tk.Frame(info_frame, bg="#FFFFFF")
        items_frame.pack(fill="x", pady=(0, 15))

        tk.Label(items_frame, text="🛍️ PRODUCTOS PEDIDOS:", 
                font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#E67E22").pack(anchor="w")

        try:
            import json
            # Parsear los items desde JSON
            items_str = order.get('items', '') or '[]'
            print(f"🔍 DEBUG: Items string: {items_str[:200]}...")
            
            if items_str and items_str.strip():
                items = json.loads(items_str)
                print(f"🔍 DEBUG: Items parseados: {len(items)} productos")
            else:
                items = []
                print("🔍 DEBUG: No hay items o string vacío")
            
            if items and len(items) > 0:
                for i, item in enumerate(items, 1):
                    # Obtener información del producto de manera más robusta
                    name = item.get('name', item.get('title', 'Producto sin nombre'))
                    quantity = item.get('quantity', item.get('cantidad', 1))
                    price = float(item.get('price', item.get('precio', item.get('unit_price', 0))))
                    description = item.get('description', item.get('descripcion', ''))
                    
                    print(f"   Producto {i}: {name} x{quantity} = ${price}")
                    
                    # Crear texto del producto más detallado
                    item_text = f"   {i}. {name}"
                    if quantity > 1:
                        item_text += f" x{quantity}"
                    item_text += f" = ${price:.2f}"
                    
                    # Label principal del producto
                    product_label = tk.Label(items_frame, text=item_text, 
                            font=("Segoe UI", 11, "bold"), bg="#FFFFFF", fg="#2C3E50")
                    product_label.pack(anchor="w", padx=20)
                    
                    # Si hay descripción, mostrarla
                    if description and description.strip():
                        desc_text = f"      {description}"
                        tk.Label(items_frame, text=desc_text, 
                                font=("Segoe UI", 10), bg="#FFFFFF", fg="#7F8C8D").pack(anchor="w", padx=20)
            else:
                tk.Label(items_frame, text="• Pedido sin productos especificados", 
                        font=("Segoe UI", 11), bg="#FFFFFF", fg="#E67E22").pack(anchor="w", padx=20)
                        
        except json.JSONDecodeError as e:
            print(f"❌ DEBUG: Error JSON: {e}")
            tk.Label(items_frame, text=f"• Error JSON: {str(e)}", 
                    font=("Segoe UI", 11), bg="#FFFFFF", fg="#E74C3C").pack(anchor="w", padx=20)
        except Exception as e:
            print(f"❌ DEBUG: Error productos: {e}")
            tk.Label(items_frame, text=f"• Error al procesar productos: {str(e)}", 
                    font=("Segoe UI", 11), bg="#FFFFFF", fg="#E74C3C").pack(anchor="w", padx=20)

        # Botones de acción
        buttons_frame = tk.Frame(order_frame, bg="#FFFFFF")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))

        tk.Button(buttons_frame, text="✅ MARCAR COMO COMPLETADO", 
                 command=lambda: self.update_order_status_and_refresh(order['id'], 'completado'),
                 bg="#27AE60", fg="white", font=("Segoe UI", 12, "bold")).pack(side="left", padx=(0, 10))
        
        tk.Button(buttons_frame, text="🎫 AGREGAR A TICKETS", 
                 command=lambda: self.add_web_order_to_tickets(order),
                 bg="#3498DB", fg="white", font=("Segoe UI", 12, "bold")).pack(side="left", padx=(0, 10))
        
        tk.Button(buttons_frame, text="❌ CANCELAR PEDIDO", 
                 command=lambda: self.update_order_status_and_refresh(order['id'], 'cancelado'),
                 bg="#E74C3C", fg="white", font=("Segoe UI", 12, "bold")).pack(side="right")

    def update_order_status_and_refresh(self, order_id, new_status):
        """Actualizar estado de pedido y refrescar la vista"""
        try:
            if self.pedidos_web_manager.update_order_status(order_id, new_status):
                status_text = {
                    'completado': 'completado',
                    'cancelado': 'cancelado'
                }.get(new_status, new_status)
                
                messagebox.showinfo("Estado actualizado", 
                                   f"El pedido ha sido marcado como {status_text}")
                self.show_pedidos_online()  # Refrescar la vista
            else:
                messagebox.showerror("Error", "No se pudo actualizar el estado del pedido")
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar pedido: {e}")

    def add_web_order_to_tickets(self, order):
        """Agregar pedido web al sistema de tickets"""
        try:
            import json
            fecha_venta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Procesar items del pedido
            items = json.loads(order['items']) if order['items'] else []
            
            if not items:
                messagebox.showwarning("Sin productos", "Este pedido no tiene productos válidos")
                return
            
            # Agregar cada item como un ticket separado
            for item in items:
                producto = item.get('name', 'Producto Web')
                cantidad = item.get('quantity', 1)
                precio = item.get('price', 0)
                
                # Guardar en la base de datos de tickets
                conn = sqlite3.connect('ventas.db')
                c = conn.cursor()
                c.execute("""
                    INSERT INTO tickets (fecha, producto, cantidad, precio, pago, estado, motivo_cancelacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (fecha_venta, f"{producto} (Web)", cantidad, precio, 
                      order.get('metodo_pago', 'Web'), 'Activo', ''))
                conn.commit()
                conn.close()
            
            # Marcar el pedido como completado
            self.pedidos_web_manager.update_order_status(order['id'], 'completado')
            
            messagebox.showinfo("Pedido procesado", 
                               f"El pedido de {order['cliente_nombre']} ha sido agregado al sistema de tickets")
            self.show_pedidos_online()  # Refrescar la vista
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar pedido: {e}")
            logging.error(f"Error procesando pedido web: {e}")

    def iniciar_monitoreo_pedidos(self):
        """Iniciar el monitoreo automático de pedidos web"""
        try:
            self.pedidos_web_manager.iniciar_monitoreo()
            self.estado_monitoreo_label.config(
                text="🟢 Monitoreo: Activo",
                fg="#27AE60"
            )
            messagebox.showinfo("Monitoreo", "🔄 Monitoreo de pedidos web iniciado")
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar monitoreo: {e}")

    def detener_monitoreo_pedidos(self):
        """Detener el monitoreo automático de pedidos web"""
        try:
            self.pedidos_web_manager.detener_monitoreo()
            self.estado_monitoreo_label.config(
                text="⭕ Monitoreo: Detenido",
                fg="#95A5A6"
            )
            messagebox.showinfo("Monitoreo", "🛑 Monitoreo de pedidos web detenido")
        except Exception as e:
            messagebox.showerror("Error", f"Error al detener monitoreo: {e}")

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

    def alerta_bajo_inventario(self):
        """Alertar cuando hay productos con bajo inventario"""
        try:
            productos = cargar_inventario()
            productos_bajos = productos[productos["Unidades"] < 5]
            if not productos_bajos.empty:
                mensaje = "⚠️ PRODUCTOS CON BAJO INVENTARIO:\n\n"
                for _, row in productos_bajos.iterrows():
                    mensaje += f"• {row['Producto']}: {row['Unidades']} unidades\n"
                messagebox.showwarning("Inventario Bajo", mensaje)
        except Exception as e:
            logging.error(f"Error en alerta_bajo_inventario: {e}")

# FUERA DE LA CLASE - funciones que están bien aquí
def extraer_datos_ticket(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        texto = ""
        for page in pdf.pages:
            texto += page.extract_text() + "\n"

    # Busca la fecha
    fecha = None
    for linea in texto.splitlines():
        if "Fecha:" in linea:
            fecha_txt = linea.split("Fecha:")[1].strip()
            try:
                fecha = datetime.strptime(fecha_txt, "%d/%m/%Y %H:%M")
            except Exception:
                fecha = None
            break

    # Busca método de pago
    metodo_pago = "Efectivo" if "Efectivo" in texto else "Tarjeta"

    # Busca productos
    productos = []
    captura = False
    for linea in texto.splitlines():
        if "Producto" in linea and "Cant" in linea and "Precio" in linea:
            captura = True
            continue
        if captura:
            if "TOTAL:" in linea or "Método de Pago" in linea or "---" in linea:
                break
            if linea.strip() == "":
                continue
            partes = linea.strip().split()
            if len(partes) >= 4:
                nombre = " ".join(partes[:-3])
                cantidad = partes[-3]
                precio = partes[-2].replace("$", "").replace(",", "")
                # subtotal = partes[-1]  # No lo usamos
                try:
                    cantidad = int(cantidad)
                    precio = float(precio)
                    productos.append((nombre, cantidad, precio))
                except Exception:
                    continue

    return fecha, metodo_pago, productos

def agregar_a_excel(datos):
    if os.path.exists(ARCHIVO_EXCEL):
        df = pd.read_excel(ARCHIVO_EXCEL)
    else:
        df = pd.DataFrame(columns=["Fecha", "Producto", "Cantidad", "Precio", "Pago", "Estado", "MotivoCancelacion"])

    for fecha, metodo_pago, productos in datos:
        for nombre, cantidad, precio in productos:
            df.loc[len(df)] = [fecha, nombre, cantidad, precio, metodo_pago, "Activo", ""]
    df.to_excel(ARCHIVO_EXCEL, index=False)
    print("¡Tickets agregados al Excel!")

def guardar_ticket_sqlite(fecha, producto, cantidad, precio, pago, estado="Activo", motivo_cancelacion=""):
    conn = sqlite3.connect('ventas.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO tickets (fecha, producto, cantidad, precio, pago, estado, motivo_cancelacion)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (fecha, producto, cantidad, precio, pago, estado, motivo_cancelacion))
    conn.commit()
    conn.close()

def invertir_logo():
    """
    Invierte los colores del logo original (suponiendo que el logo está en blanco sobre fondo negro)
    y guarda el logo invertido como 'logo_invertido.png'.
    """
    from PIL import Image

    # Cargar imagen original
    logo_path = "logo.png"
    logo = Image.open(logo_path)

    # Invertir colores
    logo_invertido = Image.eval(logo, lambda x: 255 - x)

    # Guardar imagen invertida
    logo_invertido_path = "logo_invertido.png"
    logo_invertido.save(logo_invertido_path)

    messagebox.showinfo("Logo Invertido", f"El logo ha sido invertido y guardado como:\n{logo_invertido_path}")

if __name__ == "__main__":
    try:
        app = AppCafeteria()
        app.mainloop()
    except Exception as e:
        logging.critical(f"Error crítico al iniciar la aplicación: {e}")
        messagebox.showerror("Error crítico", f"No se pudo iniciar la aplicación:\n{e}")
