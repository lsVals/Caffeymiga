import pdfplumber
import pandas as pd
import os
from datetime import datetime

CARPETA_PDFS = "tickets"
ARCHIVO_EXCEL = "tickets.xlsx"

def extraer_datos_ticket(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        texto = ""
        for page in pdf.pages:
            texto += page.extract_text() + "\n"

    # Busca la fecha
    fecha = None
    for linea in texto.splitlines():
        if "Fecha:" in linea:
            fecha = linea.split("Fecha:")[1].strip()
            try:
                fecha = datetime.strptime(fecha, "%d/%m/%Y %H:%M")
            except:
                fecha = None
            break

    # Busca método de pago
    metodo_pago = "Efectivo" if "Efectivo" in texto else "Tarjeta"

    # Busca productos
    productos = []
    captura = False
    for linea in texto.splitlines():
        if "Producto" in linea and "Precio" in linea:
            captura = True
            continue
        if captura:
            if "---" in linea or "TOTAL" in linea:
                break
            partes = linea.strip().split()
            if len(partes) >= 3:
                nombre = " ".join(partes[:-2])
                cantidad = partes[-2]
                precio = partes[-1]
                try:
                    cantidad = int(cantidad)
                    precio = float(precio.replace("$", "").replace(",", ""))
                    productos.append((nombre, cantidad, precio))
                except:
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

def main():
    datos = []
    for archivo in os.listdir(CARPETA_PDFS):
        if archivo.lower().endswith(".pdf"):
            ruta = os.path.join(CARPETA_PDFS, archivo)
            print(f"Procesando: {archivo}")
            fecha, metodo_pago, productos = extraer_datos_ticket(ruta)
            if fecha and productos:
                datos.append((fecha, metodo_pago, productos))
            else:
                print(f"No se pudo extraer datos de {archivo}")
    agregar_a_excel(datos)

if __name__ == "__main__":
    main()