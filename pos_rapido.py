#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema POS Rápido - Caffè & Miga
Versión optimizada para carga rápida
"""

import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import json
from datetime import datetime
import os

class POSRapido:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 POS RÁPIDO - Caffè & Miga")
        
        # Configurar ventana
        self.root.geometry("1200x800")
        self.root.configure(bg="#2C3E50")
        
        # Inicializar base de datos
        self.init_db()
        
        # Crear interfaz
        self.crear_interfaz()
        
    def init_db(self):
        """Inicializar base de datos"""
        try:
            # Base de datos POS
            conn = sqlite3.connect('pos_pedidos.db')
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS pedidos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_nombre TEXT,
                    cliente_telefono TEXT,
                    hora_recogida TEXT,
                    items TEXT,
                    total REAL,
                    estado TEXT DEFAULT 'pendiente',
                    metodo_pago TEXT,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
            
            # Base de datos ventas locales
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
                    estado TEXT DEFAULT 'Activo',
                    motivo_cancelacion TEXT
                )
            ''')
            conn.commit()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error DB", f"Error inicializando base de datos: {e}")
    
    def crear_interfaz(self):
        """Crear interfaz principal"""
        # Título
        titulo = tk.Label(
            self.root,
            text="🚀 POS RÁPIDO - CAFFÈ & MIGA 🚀",
            font=("Arial", 24, "bold"),
            bg="#2C3E50",
            fg="#ECF0F1",
            pady=20
        )
        titulo.pack()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#2C3E50")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Panel izquierdo - Pedidos Web
        left_panel = tk.Frame(main_frame, bg="#3498DB", relief="raised", bd=2)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(
            left_panel,
            text="🌐 PEDIDOS WEB",
            font=("Arial", 18, "bold"),
            bg="#3498DB",
            fg="white",
            pady=10
        ).pack()
        
        # Lista de pedidos web
        self.tree_web = ttk.Treeview(
            left_panel,
            columns=("id", "cliente", "total", "metodo", "estado"),
            show="headings",
            height=15
        )
        
        # Configurar columnas
        self.tree_web.heading("id", text="ID")
        self.tree_web.heading("cliente", text="Cliente")
        self.tree_web.heading("total", text="Total")
        self.tree_web.heading("metodo", text="Pago")
        self.tree_web.heading("estado", text="Estado")
        
        self.tree_web.column("id", width=50)
        self.tree_web.column("cliente", width=150)
        self.tree_web.column("total", width=80)
        self.tree_web.column("metodo", width=100)
        self.tree_web.column("estado", width=100)
        
        self.tree_web.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Botones para pedidos web
        btn_frame_web = tk.Frame(left_panel, bg="#3498DB")
        btn_frame_web.pack(pady=10)
        
        tk.Button(
            btn_frame_web,
            text="🔄 ACTUALIZAR",
            command=self.cargar_pedidos_web,
            bg="#27AE60",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame_web,
            text="✅ COMPLETAR",
            command=self.completar_pedido,
            bg="#E67E22",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15
        ).pack(side="left", padx=5)
        
        # Panel derecho - Ventas Locales
        right_panel = tk.Frame(main_frame, bg="#E74C3C", relief="raised", bd=2)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        tk.Label(
            right_panel,
            text="💰 VENTAS LOCALES",
            font=("Arial", 18, "bold"),
            bg="#E74C3C",
            fg="white",
            pady=10
        ).pack()
        
        # Lista de ventas locales
        self.tree_local = ttk.Treeview(
            right_panel,
            columns=("id", "fecha", "producto", "cantidad", "precio", "pago"),
            show="headings",
            height=15
        )
        
        # Configurar columnas
        self.tree_local.heading("id", text="ID")
        self.tree_local.heading("fecha", text="Fecha")
        self.tree_local.heading("producto", text="Producto")
        self.tree_local.heading("cantidad", text="Cant")
        self.tree_local.heading("precio", text="Precio")
        self.tree_local.heading("pago", text="Pago")
        
        self.tree_local.column("id", width=50)
        self.tree_local.column("fecha", width=100)
        self.tree_local.column("producto", width=150)
        self.tree_local.column("cantidad", width=60)
        self.tree_local.column("precio", width=80)
        self.tree_local.column("pago", width=80)
        
        self.tree_local.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Botones para ventas locales
        btn_frame_local = tk.Frame(right_panel, bg="#E74C3C")
        btn_frame_local.pack(pady=10)
        
        tk.Button(
            btn_frame_local,
            text="🔄 ACTUALIZAR",
            command=self.cargar_ventas_locales,
            bg="#27AE60",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame_local,
            text="➕ NUEVA VENTA",
            command=self.nueva_venta_rapida,
            bg="#9B59B6",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15
        ).pack(side="left", padx=5)
        
        # Panel inferior - Estado y controles
        bottom_panel = tk.Frame(self.root, bg="#34495E", height=80)
        bottom_panel.pack(fill="x", side="bottom")
        bottom_panel.pack_propagate(False)
        
        # Estado
        self.label_estado = tk.Label(
            bottom_panel,
            text="✅ SISTEMA LISTO",
            font=("Arial", 16, "bold"),
            bg="#34495E",
            fg="#2ECC71",
            pady=10
        )
        self.label_estado.pack(side="left", padx=20)
        
        # Botón de sincronización
        tk.Button(
            bottom_panel,
            text="🔄 SINCRONIZAR TODO",
            command=self.sincronizar_todo,
            bg="#F39C12",
            fg="white",
            font=("Arial", 14, "bold"),
            height=2
        ).pack(side="right", padx=20, pady=10)
        
        # Cargar datos iniciales
        self.cargar_pedidos_web()
        self.cargar_ventas_locales()
        
    def cargar_pedidos_web(self):
        """Cargar pedidos web pendientes"""
        try:
            # Limpiar tabla
            for item in self.tree_web.get_children():
                self.tree_web.delete(item)
            
            conn = sqlite3.connect('pos_pedidos.db')
            c = conn.cursor()
            c.execute("""
                SELECT id, cliente_nombre, total, metodo_pago, estado 
                FROM pedidos 
                WHERE estado = 'pendiente' 
                ORDER BY fecha_creacion DESC
                LIMIT 50
            """)
            
            pedidos = c.fetchall()
            conn.close()
            
            for pedido in pedidos:
                self.tree_web.insert("", "end", values=pedido)
            
            self.label_estado.config(
                text=f"📥 {len(pedidos)} pedidos web pendientes",
                fg="#3498DB"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando pedidos web: {e}")
    
    def cargar_ventas_locales(self):
        """Cargar ventas locales recientes"""
        try:
            # Limpiar tabla
            for item in self.tree_local.get_children():
                self.tree_local.delete(item)
            
            conn = sqlite3.connect('ventas.db')
            c = conn.cursor()
            c.execute("""
                SELECT id, fecha, producto, cantidad, precio, pago 
                FROM tickets 
                WHERE estado = 'Activo' 
                ORDER BY fecha DESC 
                LIMIT 50
            """)
            
            ventas = c.fetchall()
            conn.close()
            
            for venta in ventas:
                self.tree_local.insert("", "end", values=venta)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando ventas locales: {e}")
    
    def completar_pedido(self):
        """Completar pedido web seleccionado"""
        selection = self.tree_web.selection()
        if not selection:
            messagebox.showwarning("Selección", "Selecciona un pedido para completar")
            return
        
        item = self.tree_web.item(selection[0])
        pedido_id = item['values'][0]
        
        try:
            conn = sqlite3.connect('pos_pedidos.db')
            c = conn.cursor()
            c.execute("""
                UPDATE pedidos 
                SET estado = 'completado', fecha_actualizacion = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (pedido_id,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Éxito", f"Pedido #{pedido_id} completado")
            self.cargar_pedidos_web()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error completando pedido: {e}")
    
    def nueva_venta_rapida(self):
        """Ventana para nueva venta rápida"""
        ventana = tk.Toplevel(self.root)
        ventana.title("💰 Nueva Venta Rápida")
        ventana.geometry("400x300")
        ventana.configure(bg="#ECF0F1")
        
        # Campos
        tk.Label(ventana, text="Producto:", bg="#ECF0F1", font=("Arial", 12)).pack(pady=5)
        entry_producto = tk.Entry(ventana, font=("Arial", 12), width=30)
        entry_producto.pack(pady=5)
        
        tk.Label(ventana, text="Cantidad:", bg="#ECF0F1", font=("Arial", 12)).pack(pady=5)
        entry_cantidad = tk.Entry(ventana, font=("Arial", 12), width=30)
        entry_cantidad.pack(pady=5)
        
        tk.Label(ventana, text="Precio:", bg="#ECF0F1", font=("Arial", 12)).pack(pady=5)
        entry_precio = tk.Entry(ventana, font=("Arial", 12), width=30)
        entry_precio.pack(pady=5)
        
        tk.Label(ventana, text="Método de Pago:", bg="#ECF0F1", font=("Arial", 12)).pack(pady=5)
        pago_var = tk.StringVar(value="Efectivo")
        pago_combo = ttk.Combobox(ventana, textvariable=pago_var, values=["Efectivo", "Tarjeta"], width=27)
        pago_combo.pack(pady=5)
        
        def guardar_venta():
            try:
                producto = entry_producto.get().strip()
                cantidad = int(entry_cantidad.get())
                precio = float(entry_precio.get())
                pago = pago_var.get()
                
                if not producto:
                    messagebox.showerror("Error", "Ingresa el nombre del producto")
                    return
                
                conn = sqlite3.connect('ventas.db')
                c = conn.cursor()
                c.execute("""
                    INSERT INTO tickets (fecha, producto, cantidad, precio, pago, estado)
                    VALUES (?, ?, ?, ?, ?, 'Activo')
                """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), producto, cantidad, precio, pago))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Éxito", "Venta registrada correctamente")
                ventana.destroy()
                self.cargar_ventas_locales()
                
            except ValueError:
                messagebox.showerror("Error", "Verifica que cantidad y precio sean números válidos")
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando venta: {e}")
        
        tk.Button(
            ventana,
            text="💾 GUARDAR VENTA",
            command=guardar_venta,
            bg="#27AE60",
            fg="white",
            font=("Arial", 14, "bold"),
            width=20
        ).pack(pady=20)
    
    def sincronizar_todo(self):
        """Sincronizar todos los datos"""
        self.label_estado.config(text="🔄 Sincronizando...", fg="#F39C12")
        self.root.update()
        
        self.cargar_pedidos_web()
        self.cargar_ventas_locales()
        
        self.label_estado.config(text="✅ Sincronización completa", fg="#27AE60")
    
    def ejecutar(self):
        """Iniciar la aplicación"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n🛑 Sistema cerrado por el usuario")
        except Exception as e:
            messagebox.showerror("Error Fatal", f"Error en la aplicación: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando POS Rápido - Caffè & Miga...")
    app = POSRapido()
    app.ejecutar()
