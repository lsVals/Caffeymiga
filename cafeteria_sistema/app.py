import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, date, time
import pandas as pd
import os
import sqlite3
import logging

# Archivos base (solo inventario puede seguir en Excel)
ARCHIVO_INVENTARIO = "inventario.xlsx"

# Variables globales
usuario_valido = "admin"
contrasena_valida = "admin"

# Configuración básica de logging
logging.basicConfig(
    filename="cafeteria_log.txt",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s:%(message)s"
)

# Funciones de Inventario (puedes migrar a DB si lo deseas)
def cargar_inventario():
    try:
        if not os.path.exists(ARCHIVO_INVENTARIO):
            df = pd.DataFrame(columns=["Producto", "Unidades", "Precio", "TipoUnidad"])
            df.to_excel(ARCHIVO_INVENTARIO, index=False)
        df = pd.read_excel(ARCHIVO_INVENTARIO)
        if "TipoUnidad" not in df.columns:
            df["TipoUnidad"] = "Unidad"
        return df
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el inventario:\n{e}")
        logging.error(f"Error al cargar inventario: {e}")
        return pd.DataFrame(columns=["Producto", "Unidades", "Precio", "TipoUnidad"])

def guardar_inventario(df):
    try:
        df.to_excel(ARCHIVO_INVENTARIO, index=False)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el inventario:\n{e}")
        logging.error(f"Error al guardar inventario: {e}")

# Inicializar base de datos
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

def guardar_ticket_sqlite(fecha, producto, cantidad, precio, pago, estado="Activo", motivo_cancelacion=""):
    conn = sqlite3.connect('ventas.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO tickets (fecha, producto, cantidad, precio, pago, estado, motivo_cancelacion)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (fecha, producto, cantidad, precio, pago, estado, motivo_cancelacion))
    conn.commit()
    conn.close()

def obtener_ventas():
    conn = sqlite3.connect('ventas.db')
    df = pd.read_sql_query("SELECT * FROM tickets", conn)
    conn.close()
    return df

def ventas_periodo(periodo="dia"):
    df = obtener_ventas()
    if df.empty:
        return df
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df[df["estado"] == "Activo"]
    hoy = pd.Timestamp.now().normalize()
    if periodo == "dia":
        return df[df["fecha"].dt.normalize() == hoy]
    elif periodo == "semana":
        semana = hoy - pd.Timedelta(days=hoy.weekday())
        return df[df["fecha"].dt.normalize() >= semana]
    elif periodo == "mes":
        mes = hoy.replace(day=1)
        return df[df["fecha"].dt.normalize() >= mes]
    else:
        return df

def backup_db():
    import shutil
    origen = "ventas.db"
    destino = filedialog.asksaveasfilename(
        defaultextension=".db",
        filetypes=[("Base de datos SQLite", "*.db")],
        title="Guardar copia de seguridad"
    )
    if destino:
        try:
            shutil.copy(origen, destino)
            messagebox.showinfo("Copia de seguridad", "¡Copia de seguridad guardada correctamente!")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la copia de seguridad:\n{e}")

class AppCafeteria(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Ventas")
        self.geometry("600x700")
        self.configure(bg="#f0f0f0")
        self.frames = {}
        self.promocion_frappes_activa = False
        self.show_login()

    def clear_frames(self):
        for frame in self.frames.values():
            frame.pack_forget()
            frame.place_forget()

    def show_login(self):
        self.clear_frames()
        frame = tk.Frame(self, bg="#235A6F")
        frame.pack(fill="both", expand=True)
        self.frames["login"] = frame

        card = tk.Frame(frame, bg="#FFFFFF", bd=0, relief="flat", highlightbackground="#235A6F", highlightthickness=4)
        card.place(relx=0.5, rely=0, anchor="n", y=40)

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

        botones = [
            ("Generar Compra", self.show_compra),
            ("Ver Inventario", self.show_inventario),
            ("Resumen de Ventas", self.show_resumen_ventas),
            ("Ver Ventas (DB)", self.show_ventas_db),
            ("Guardar copia de seguridad", backup_db),
            ("Salir del Programa", self.destroy)
        ]
        for texto, comando in botones:
            tk.Button(
                card,
                text=texto,
                command=comando,
                font=("Segoe UI", 18, "bold"),
                width=22,
                height=2,
                bg="#235A6F" if "Salir" not in texto else "#E74C3C",
                fg="white",
                bd=0,
                activebackground="#183B4A" if "Salir" not in texto else "#922B21",
                activeforeground="white",
                cursor="hand2",
                highlightthickness=0
            ).pack(pady=10)

    # ...deja aquí tus métodos show_inventario, show_compra, previsualizar_ticket, generar_ticket, etc.
    # Solo asegúrate de que para ventas uses guardar_ticket_sqlite y obtener_ventas, y no Excel.

    def show_ventas_db(self):
        self.clear_frames()
        frame = tk.Frame(self, bg="#FFFFFF")
        frame.pack(fill="both", expand=True)
        self.frames["ventas_db"] = frame

        df = obtener_ventas()
        if df.empty:
            tk.Label(frame, text="No hay ventas registradas aún.", font=("Arial", 14), bg="#FFFFFF").pack(pady=20)
            return

        text_frame = tk.Frame(frame, bg="#FFFFFF")
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(text_frame)
        text = tk.Text(text_frame, font=("Courier", 11), yscrollcommand=scrollbar.set, width=110, height=30, bg="#F2F4F5")
        scrollbar.config(command=text.yview)
        text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        encabezados = df.columns.tolist()
        text.insert(tk.END, "\t".join(encabezados) + "\n")
        text.insert(tk.END, "-" * 120 + "\n")

        for _, row in df.iterrows():
            fila = [str(row[col]) for col in encabezados]
            text.insert(tk.END, "\t".join(fila) + "\n")

        tk.Button(frame, text="Volver al Menú", command=self.show_menu,
                  bg="#3498DB", fg="white", font=("Arial", 12)).pack(pady=10)

    def show_resumen_ventas(self):
        self.clear_frames()
        frame = tk.Frame(self, bg="#FFFFFF")
        frame.pack(fill="both", expand=True)
        self.frames["resumen_ventas"] = frame

        df_dia = ventas_periodo("dia")
        df_semana = ventas_periodo("semana")
        df_mes = ventas_periodo("mes")

        def resumen(df, titulo):
            if df.empty:
                return f"{titulo}\nSin ventas registradas.\n\n"
            total = (df["precio"] * df["cantidad"]).sum()
            productos = df.groupby("producto")["cantidad"].sum()
            resumen = f"{titulo}\nTotal: ${total:.2f}\nProductos vendidos:\n"
            for prod, cant in productos.items():
                resumen += f"  {prod}: {cant}\n"
            return resumen + "\n"

        texto = resumen(df_dia, "Ventas del Día")
        texto += "-"*40 + "\n"
        texto += resumen(df_semana, "Ventas de la Semana")
        texto += "-"*40 + "\n"
        texto += resumen(df_mes, "Ventas del Mes")

        text_frame = tk.Frame(frame, bg="#F2F4F5")
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget = tk.Text(text_frame, font=("Courier", 12), bg="#F2F4F5", wrap="none", height=30)
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar_texto = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        scrollbar_texto.pack(side="right", fill="y")
        text_widget.configure(yscrollcommand=scrollbar_texto.set)
        text_widget.insert(tk.END, texto)

        tk.Button(frame, text="Volver al Menú", command=self.show_menu,
                  bg="#3498DB", fg="white", font=("Arial", 12)).pack(pady=10)

if __name__ == "__main__":
    try:
        app = AppCafeteria()
        app.mainloop()
    except Exception as e:
        logging.error(f"Error inesperado: {e}")
        messagebox.showerror("Error", f"Ocurrió un error inesperado:\n{e}")