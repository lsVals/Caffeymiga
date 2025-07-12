
# INTEGRACIÓN AUTOMÁTICA CAFFE & MIGA
# Este archivo se conecta con tu sistema existente

import sqlite3
import requests
import json
import time
import threading
from datetime import datetime
import os

class CaffeMigaAutoIntegration:
    def __init__(self):
        self.server_url = "http://127.0.0.1:3000"
        self.is_running = False
        
        # Auto-detectar base de datos
        archivos_db = [f for f in os.listdir(".") if f.endswith(".db")]
        if archivos_db:
            self.bd_path = archivos_db[0]  # Usar la primera encontrada
            print(f"✅ Usando base de datos: {self.bd_path}")
        else:
            print("❌ No se encontró base de datos")
            return
        
        # Auto-configurar
        self.configurar_automaticamente()
    
    def configurar_automaticamente(self):
        """Detectar automáticamente tabla y columnas de tu sistema"""
        try:
            conn = sqlite3.connect(self.bd_path)
            cursor = conn.cursor()
            
            # Obtener tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tablas = [tabla[0] for tabla in cursor.fetchall()]
            
            print(f"📊 Tablas encontradas: {', '.join(tablas)}")
            
            # Buscar tabla más probable para pedidos
            tabla_pedidos = None
            for tabla in tablas:
                cursor.execute(f"PRAGMA table_info({tabla})")
                columnas = [col[1].lower() for col in cursor.fetchall()]
                
                # Detectar palabras clave
                if any(palabra in ' '.join(columnas) for palabra in ['cliente', 'total', 'fecha', 'precio']):
                    tabla_pedidos = tabla
                    print(f"🎯 Tabla detectada para pedidos: {tabla}")
                    break
            
            if not tabla_pedidos:
                tabla_pedidos = tablas[0] if tablas else None
                print(f"⚠️ Usando primera tabla como predeterminada: {tabla_pedidos}")
            
            self.tabla = tabla_pedidos
            
            # Obtener columnas de la tabla elegida
            if self.tabla:
                cursor.execute(f"PRAGMA table_info({self.tabla})")
                self.columnas = [col[1] for col in cursor.fetchall()]
                print(f"📋 Columnas disponibles: {', '.join(self.columnas)}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error configurando: {e}")
            return False
    
    def obtener_pedidos_web(self):
        """Obtener pedidos del e-commerce"""
        try:
            response = requests.get(f"{self.server_url}/pos/orders", timeout=5)
            if response.status_code == 200:
                return response.json().get('orders', [])
            return []
        except:
            return []
    
    def insertar_pedido_web(self, pedido):
        """Insertar pedido web en tu sistema"""
        try:
            customer = pedido.get('customer', {})
            items = pedido.get('items', [])
            
            # Verificar si ya existe
            if self.pedido_existe(pedido['id']):
                return False
            
            conn = sqlite3.connect(self.bd_path)
            cursor = conn.cursor()
            
            # Preparar datos básicos
            datos = {
                'cliente': customer.get('name', 'Cliente Web'),
                'telefono': customer.get('phone', ''),
                'total': pedido.get('total', 0),
                'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'estado': 'Nuevo',
                'origen': 'Web',
                'items': ', '.join([f"{item.get('quantity', 1)}x {item.get('title', 'Item')}" for item in items]),
                'notas': f"Pedido e-commerce - ID: {pedido['id'][:8]}"
            }
            
            # Mapear a columnas existentes (básico)
            valores_insertar = []
            columnas_insertar = []
            
            for columna in self.columnas:
                col_lower = columna.lower()
                
                if 'cliente' in col_lower or 'nombre' in col_lower:
                    columnas_insertar.append(columna)
                    valores_insertar.append(datos['cliente'])
                elif 'telefono' in col_lower or 'tel' in col_lower:
                    columnas_insertar.append(columna)
                    valores_insertar.append(datos['telefono'])
                elif 'total' in col_lower or 'precio' in col_lower or 'monto' in col_lower:
                    columnas_insertar.append(columna)
                    valores_insertar.append(datos['total'])
                elif 'fecha' in col_lower or 'date' in col_lower:
                    columnas_insertar.append(columna)
                    valores_insertar.append(datos['fecha'])
                elif 'estado' in col_lower or 'status' in col_lower:
                    columnas_insertar.append(columna)
                    valores_insertar.append(datos['estado'])
                elif 'item' in col_lower or 'producto' in col_lower or 'descripcion' in col_lower:
                    columnas_insertar.append(columna)
                    valores_insertar.append(datos['items'])
                elif 'nota' in col_lower or 'observacion' in col_lower or 'comentario' in col_lower:
                    columnas_insertar.append(columna)
                    valores_insertar.append(datos['notas'])
                elif 'origen' in col_lower or 'tipo' in col_lower:
                    columnas_insertar.append(columna)
                    valores_insertar.append(datos['origen'])
            
            if columnas_insertar:
                placeholders = ', '.join(['?' for _ in valores_insertar])
                query = f"INSERT INTO {self.tabla} ({', '.join(columnas_insertar)}) VALUES ({placeholders})"
                
                cursor.execute(query, valores_insertar)
                conn.commit()
                
                print(f"✅ Pedido web agregado: {datos['cliente']} - ${datos['total']}")
                
                # Marcar como procesado
                requests.put(f"{self.server_url}/pos/orders/{pedido['id']}/status",
                           json={"status": "preparando"}, timeout=5)
                
                conn.close()
                return True
            
            conn.close()
            return False
            
        except Exception as e:
            print(f"❌ Error insertando pedido: {e}")
            return False
    
    def pedido_existe(self, firebase_id):
        """Verificar si pedido ya existe"""
        try:
            conn = sqlite3.connect(self.bd_path)
            cursor = conn.cursor()
            
            # Buscar en notas o descripción
            for columna in self.columnas:
                if 'nota' in columna.lower() or 'descripcion' in columna.lower() or 'observacion' in columna.lower():
                    cursor.execute(f"SELECT COUNT(*) FROM {self.tabla} WHERE {columna} LIKE ?", 
                                 (f"%{firebase_id[:8]}%",))
                    if cursor.fetchone()[0] > 0:
                        conn.close()
                        return True
            
            conn.close()
            return False
        except:
            return False
    
    def sincronizar(self):
        """Sincronizar pedidos web con tu sistema"""
        print("🔄 Sincronizando pedidos web...")
        
        pedidos = self.obtener_pedidos_web()
        
        if not pedidos:
            print("📭 No hay pedidos nuevos")
            return
        
        for pedido in pedidos:
            self.insertar_pedido_web(pedido)
        
        print(f"✅ Sincronización completada: {len(pedidos)} pedidos procesados")
    
    def iniciar_monitoreo(self, intervalo=30):
        """Iniciar monitoreo automático"""
        if self.is_running:
            return
        
        self.is_running = True
        print(f"🔄 Monitoreo iniciado cada {intervalo} segundos")
        
        def monitor():
            while self.is_running:
                try:
                    self.sincronizar()
                    time.sleep(intervalo)
                except:
                    time.sleep(intervalo)
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def detener_monitoreo(self):
        """Detener monitoreo"""
        self.is_running = False
        print("🛑 Monitoreo detenido")

# FUNCIÓN PARA USAR EN TU CÓDIGO EXISTENTE
caffe_miga_integration = None

def inicializar_caffe_miga():
    """Llamar esta función al inicio de tu programa"""
    global caffe_miga_integration
    try:
        caffe_miga_integration = CaffeMigaAutoIntegration()
        print("🔥 Integración Caffe & Miga inicializada")
        return True
    except Exception as e:
        print(f"❌ Error inicializando Caffe & Miga: {e}")
        return False

def sincronizar_pedidos_web():
    """Función para sincronizar manualmente"""
    global caffe_miga_integration
    if caffe_miga_integration:
        caffe_miga_integration.sincronizar()
    else:
        print("⚠️ Integración no inicializada")

def iniciar_monitoreo_web():
    """Función para iniciar monitoreo automático"""
    global caffe_miga_integration
    if caffe_miga_integration:
        caffe_miga_integration.iniciar_monitoreo(30)
    else:
        print("⚠️ Integración no inicializada")

# EJEMPLO DE USO
if __name__ == "__main__":
    # Uso independiente
    integration = CaffeMigaAutoIntegration()
    
    print("\nOpciones:")
    print("1. Sincronizar ahora")
    print("2. Iniciar monitoreo automático")
    
    opcion = input("Selecciona (1-2): ")
    
    if opcion == "1":
        integration.sincronizar()
    elif opcion == "2":
        integration.iniciar_monitoreo(30)
        print("Presiona Ctrl+C para detener...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            integration.detener_monitoreo()
