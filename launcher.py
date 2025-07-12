#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launcher para Sistema Caffè & Miga
Permite elegir entre versión completa o rápida
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

class Launcher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Caffè & Miga - Selector de Sistema")
        self.root.geometry("600x500")
        self.root.configure(bg="#2C3E50")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.root.eval('tk::PlaceWindow . center')
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crear interfaz del launcher"""
        
        # Logo y título
        titulo_frame = tk.Frame(self.root, bg="#2C3E50")
        titulo_frame.pack(pady=30)
        
        tk.Label(
            titulo_frame,
            text="☕",
            font=("Arial", 80),
            bg="#2C3E50",
            fg="#F39C12"
        ).pack()
        
        tk.Label(
            titulo_frame,
            text="CAFFÈ & MIGA",
            font=("Arial", 32, "bold"),
            bg="#2C3E50",
            fg="#ECF0F1"
        ).pack()
        
        tk.Label(
            titulo_frame,
            text="Sistema de Ventas",
            font=("Arial", 16),
            bg="#2C3E50",
            fg="#BDC3C7"
        ).pack(pady=(5, 0))
        
        # Opciones
        opciones_frame = tk.Frame(self.root, bg="#2C3E50")
        opciones_frame.pack(pady=40, padx=50, fill="both", expand=True)
        
        # Versión Rápida
        rapid_frame = tk.Frame(opciones_frame, bg="#3498DB", relief="raised", bd=3)
        rapid_frame.pack(fill="x", pady=10)
        
        tk.Label(
            rapid_frame,
            text="🚀 VERSIÓN RÁPIDA",
            font=("Arial", 18, "bold"),
            bg="#3498DB",
            fg="white",
            pady=10
        ).pack()
        
        tk.Label(
            rapid_frame,
            text="• Carga en segundos\n• Solo funciones esenciales\n• Ideal para uso diario",
            font=("Arial", 12),
            bg="#3498DB",
            fg="white",
            justify="left"
        ).pack(pady=(0, 10))
        
        tk.Button(
            rapid_frame,
            text="▶️ INICIAR VERSIÓN RÁPIDA",
            command=self.ejecutar_rapido,
            bg="#27AE60",
            fg="white",
            font=("Arial", 14, "bold"),
            width=25,
            height=2
        ).pack(pady=10)
        
        # Versión Completa
        complete_frame = tk.Frame(opciones_frame, bg="#E74C3C", relief="raised", bd=3)
        complete_frame.pack(fill="x", pady=10)
        
        tk.Label(
            complete_frame,
            text="🔧 VERSIÓN COMPLETA",
            font=("Arial", 18, "bold"),
            bg="#E74C3C",
            fg="white",
            pady=10
        ).pack()
        
        tk.Label(
            complete_frame,
            text="• Todas las funciones\n• Gestión completa de inventario\n• Reportes detallados",
            font=("Arial", 12),
            bg="#E74C3C",
            fg="white",
            justify="left"
        ).pack(pady=(0, 10))
        
        tk.Button(
            complete_frame,
            text="⚙️ INICIAR VERSIÓN COMPLETA",
            command=self.ejecutar_completo,
            bg="#8E44AD",
            fg="white",
            font=("Arial", 14, "bold"),
            width=25,
            height=2
        ).pack(pady=10)
        
        # Información adicional
        info_frame = tk.Frame(self.root, bg="#34495E")
        info_frame.pack(fill="x", side="bottom")
        
        tk.Label(
            info_frame,
            text="💡 Recomendado: Usa la versión RÁPIDA para operaciones diarias",
            font=("Arial", 11),
            bg="#34495E",
            fg="#ECF0F1",
            pady=15
        ).pack()
    
    def ejecutar_rapido(self):
        """Ejecutar versión rápida"""
        try:
            self.root.destroy()
            subprocess.run([sys.executable, "pos_rapido.py"])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo ejecutar la versión rápida: {e}")
    
    def ejecutar_completo(self):
        """Ejecutar versión completa"""
        respuesta = messagebox.askyesno(
            "Versión Completa",
            "La versión completa puede tardar más en cargar.\n\n¿Deseas continuar?"
        )
        
        if respuesta:
            try:
                self.root.destroy()
                subprocess.run([sys.executable, "cafeteria_sistema/cafeteria_sistema.py"])
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo ejecutar la versión completa: {e}")
    
    def ejecutar(self):
        """Iniciar el launcher"""
        self.root.mainloop()

if __name__ == "__main__":
    print("🚀 Iniciando Launcher Caffè & Miga...")
    launcher = Launcher()
    launcher.ejecutar()
