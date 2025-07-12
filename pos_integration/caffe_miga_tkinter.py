# Integración Caffe & Miga con sistema Tkinter + SQLite
# Copia este archivo a: C:\Users\victo\OneDrive\Escritorio\cafeteria_sistema\

import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import requests
import json
import threading
import time
from datetime import datetime
import logging

class CaffeYMigaIntegration:
    def __init__(self, master=None):
        """
        Integración para sistema POS con Tkinter
        
        Args:
            master: Ventana principal de tkinter (opcional)
        """
        self.master = master
        self.server_url = "http://127.0.0.1:3000"
        
        # CONFIGURACIÓN - AJUSTA SEGÚN TU SISTEMA
        self.mi_base_datos = "cafeteria.db"  # ← Cambia por tu BD
        self.tabla_pedidos = "pedidos"       # ← Cambia por tu tabla
        
        # Estado de la integración
        self.is_running = False
        self.last_check = datetime.now()
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('caffe_miga_integration.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def verificar_conexion_servidor(self):
        """Verificar si el servidor de Caffe & Miga está disponible"""
        try:
            response = requests.get(f"{self.server_url}/pos/dashboard", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def obtener_pedidos_nuevos(self):
        """Obtener pedidos nuevos desde Caffe & Miga"""
        try:
            response = requests.get(f"{self.server_url}/pos/orders", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('orders', [])
            else:
                self.logger.error(f"Error obteniendo pedidos: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error de conexión: {e}")
            return []
    
    def adaptar_pedido_a_mi_sistema(self, pedido_firebase):
        """
        Convertir pedido de Firebase al formato de tu sistema
        PERSONALIZA ESTA FUNCIÓN según tu base de datos
        """
        customer = pedido_firebase.get('customer', {})
        items = pedido_firebase.get('items', [])
        
        # Formato adaptado a tu sistema
        pedido_local = {
            'id_externo': pedido_firebase['id'],
            'cliente': customer.get('name', 'Cliente Web'),
            'telefono': customer.get('phone', ''),
            'email': customer.get('email', ''),
            'total': pedido_firebase.get('total', 0),
            'metodo_pago': customer.get('payment_method', 'tarjeta'),
            'items': json.dumps(items),
            'estado': 'nuevo',
            'origen': 'web_ecommerce',
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'notas': f"Pedido web - Total: ${pedido_firebase.get('total', 0)} MXN"
        }
        
        return pedido_local
    
    def insertar_en_mi_base_datos(self, pedido_local):
        """
        Insertar pedido en tu base de datos SQLite
        AJUSTA LA QUERY según tu esquema de base de datos
        """
        try:
            conn = sqlite3.connect(self.mi_base_datos)
            cursor = conn.cursor()
            
            # EJEMPLO - Ajusta según tu tabla
            query = """
                INSERT INTO pedidos (
                    id_externo, cliente, telefono, total, metodo_pago, 
                    items, estado, origen, fecha, notas
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            valores = (
                pedido_local['id_externo'],
                pedido_local['cliente'],
                pedido_local['telefono'],
                pedido_local['total'],
                pedido_local['metodo_pago'],
                pedido_local['items'],
                pedido_local['estado'],
                pedido_local['origen'],
                pedido_local['fecha'],
                pedido_local['notas']
            )
            
            cursor.execute(query, valores)
            conn.commit()
            pedido_id = cursor.lastrowid
            conn.close()
            
            self.logger.info(f"✅ Pedido insertado: {pedido_local['cliente']} - ${pedido_local['total']}")
            return pedido_id
            
        except sqlite3.Error as e:
            self.logger.error(f"❌ Error insertando en BD: {e}")
            return None
    
    def marcar_como_procesado(self, firebase_id):
        """Marcar pedido como procesado en Firebase"""
        try:
            response = requests.put(
                f"{self.server_url}/pos/orders/{firebase_id}/status",
                json={"status": "preparando"},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def procesar_pedido_completo(self, pedido_firebase):
        """Procesar un pedido completo: insertar en BD y marcar como procesado"""
        try:
            # 1. Adaptar al formato local
            pedido_local = self.adaptar_pedido_a_mi_sistema(pedido_firebase)
            
            # 2. Verificar si ya existe
            if self.pedido_ya_existe(pedido_firebase['id']):
                self.logger.info(f"⚠️ Pedido ya existe: {pedido_firebase['id'][:8]}...")
                return False
            
            # 3. Insertar en tu base de datos
            pedido_id = self.insertar_en_mi_base_datos(pedido_local)
            
            if not pedido_id:
                return False
            
            # 4. Marcar como procesado en Firebase
            if self.marcar_como_procesado(pedido_firebase['id']):
                self.logger.info(f"🔥 Pedido procesado completamente: {pedido_local['cliente']}")
            
            # 5. Notificar en la interfaz (si hay ventana)
            if self.master:
                self.mostrar_notificacion_pedido(pedido_local)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error procesando pedido: {e}")
            return False
    
    def pedido_ya_existe(self, firebase_id):
        """Verificar si un pedido ya existe en la base de datos"""
        try:
            conn = sqlite3.connect(self.mi_base_datos)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT COUNT(*) FROM pedidos WHERE id_externo = ?",
                (firebase_id,)
            )
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
            
        except:
            return False
    
    def mostrar_notificacion_pedido(self, pedido):
        """Mostrar notificación en la interfaz tkinter"""
        if self.master:
            try:
                # Notificación visual
                messagebox.showinfo(
                    "🔥 Nuevo Pedido Web",
                    f"Cliente: {pedido['cliente']}\n"
                    f"Total: ${pedido['total']:.2f}\n"
                    f"Teléfono: {pedido['telefono']}\n\n"
                    f"¡Revisar sistema para procesar!"
                )
                
                # Actualizar ventana si está disponible
                if hasattr(self.master, 'actualizar_pedidos'):
                    self.master.actualizar_pedidos()
                    
            except Exception as e:
                self.logger.error(f"Error mostrando notificación: {e}")
    
    def sincronizar_una_vez(self):
        """Sincronizar pedidos una sola vez"""
        self.logger.info("🔄 Sincronizando con Caffe & Miga...")
        
        # Verificar conexión
        if not self.verificar_conexion_servidor():
            self.logger.error("❌ No se puede conectar al servidor de Caffe & Miga")
            return False
        
        # Obtener pedidos nuevos
        pedidos = self.obtener_pedidos_nuevos()
        
        if not pedidos:
            self.logger.info("📭 No hay pedidos nuevos")
            return True
        
        # Procesar cada pedido
        procesados = 0
        for pedido in pedidos:
            if self.procesar_pedido_completo(pedido):
                procesados += 1
        
        self.logger.info(f"✅ {procesados}/{len(pedidos)} pedidos procesados")
        return True
    
    def iniciar_monitoreo_automatico(self, intervalo=30):
        """Iniciar monitoreo automático en hilo separado"""
        if self.is_running:
            self.logger.warning("⚠️ El monitoreo ya está en ejecución")
            return
        
        self.is_running = True
        self.logger.info(f"🔄 Iniciando monitoreo automático cada {intervalo} segundos")
        
        def monitor_loop():
            while self.is_running:
                try:
                    self.sincronizar_una_vez()
                    time.sleep(intervalo)
                except Exception as e:
                    self.logger.error(f"❌ Error en monitoreo: {e}")
                    time.sleep(intervalo)
        
        # Ejecutar en hilo separado para no bloquear tkinter
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def detener_monitoreo(self):
        """Detener monitoreo automático"""
        self.is_running = False
        self.logger.info("🛑 Monitoreo detenido")
    
    def crear_ventana_control(self):
        """Crear ventana de control para la integración"""
        if not self.master:
            root = tk.Tk()
            self.master = root
        
        # Ventana de control
        control_window = tk.Toplevel(self.master)
        control_window.title("🔥 Caffe & Miga - Integración")
        control_window.geometry("400x300")
        
        # Frame principal
        main_frame = ttk.Frame(control_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="🔥 Integración Caffe & Miga", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Estado de conexión
        self.status_label = ttk.Label(main_frame, text="🔄 Verificando conexión...")
        self.status_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="🔄 Sincronizar Ahora", 
                  command=self.sincronizar_una_vez).pack(pady=5, fill=tk.X)
        
        ttk.Button(btn_frame, text="▶️ Iniciar Monitoreo", 
                  command=lambda: self.iniciar_monitoreo_automatico(30)).pack(pady=5, fill=tk.X)
        
        ttk.Button(btn_frame, text="⏹️ Detener Monitoreo", 
                  command=self.detener_monitoreo).pack(pady=5, fill=tk.X)
        
        # Log de actividad
        log_frame = ttk.LabelFrame(main_frame, text="📄 Actividad Reciente", padding="5")
        log_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = tk.Text(log_frame, height=8, width=50)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Actualizar estado
        self.actualizar_estado_conexion()
        
        return control_window
    
    def actualizar_estado_conexion(self):
        """Actualizar estado de conexión en la ventana"""
        if hasattr(self, 'status_label'):
            if self.verificar_conexion_servidor():
                self.status_label.config(text="✅ Conectado al servidor")
            else:
                self.status_label.config(text="❌ Servidor no disponible")

# Funciones de utilidad para integrar en tu sistema existente

def agregar_menu_caffe_miga(menu_principal, ventana_principal):
    """
    Agregar menú de Caffe & Miga a tu sistema existente
    
    Args:
        menu_principal: Tu menú principal de tkinter
        ventana_principal: Tu ventana principal
    """
    # Crear menú de integración
    caffe_menu = tk.Menu(menu_principal, tearoff=0)
    menu_principal.add_cascade(label="🔥 Caffe & Miga", menu=caffe_menu)
    
    # Crear instancia de integración
    integration = CaffeYMigaIntegration(ventana_principal)
    
    # Agregar opciones al menú
    caffe_menu.add_command(label="🔄 Sincronizar Pedidos", 
                          command=integration.sincronizar_una_vez)
    caffe_menu.add_command(label="⚙️ Panel de Control", 
                          command=integration.crear_ventana_control)
    caffe_menu.add_command(label="▶️ Iniciar Monitoreo", 
                          command=lambda: integration.iniciar_monitoreo_automatico(30))
    caffe_menu.add_command(label="⏹️ Detener Monitoreo", 
                          command=integration.detener_monitoreo)

def crear_boton_caffe_miga(parent_frame, ventana_principal):
    """
    Crear botón de Caffe & Miga en tu interfaz existente
    
    Args:
        parent_frame: Frame donde agregar el botón
        ventana_principal: Tu ventana principal
    """
    integration = CaffeYMigaIntegration(ventana_principal)
    
    # Botón principal
    btn_caffe = ttk.Button(
        parent_frame, 
        text="🔥 Pedidos Web", 
        command=integration.crear_ventana_control
    )
    btn_caffe.pack(pady=5, padx=10, fill=tk.X)
    
    return integration

# Ejemplo de uso independiente
if __name__ == "__main__":
    # Crear ventana principal
    root = tk.Tk()
    root.title("Sistema Cafetería + Caffe & Miga")
    root.geometry("600x400")
    
    # Crear integración
    integration = CaffeYMigaIntegration(root)
    
    # Crear interfaz básica
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="🏪 Sistema de Cafetería", 
             font=('Arial', 16, 'bold')).pack(pady=10)
    
    ttk.Button(main_frame, text="🔥 Abrir Panel Caffe & Miga", 
              command=integration.crear_ventana_control).pack(pady=10)
    
    ttk.Button(main_frame, text="🔄 Sincronizar Ahora", 
              command=integration.sincronizar_una_vez).pack(pady=5)
    
    # Iniciar aplicación
    root.mainloop()
