# Integración INTERNA para tu sistema cafeteria_sistema
# Este script se ejecuta en segundo plano y agrega pedidos directamente a tu BD

import sqlite3
import requests
import json
import time
import threading
from datetime import datetime
import os
import logging

class CafeteriaSystemIntegration:
    def __init__(self, ruta_base_datos="cafeteria.db"):
        """
        Integración que inserta pedidos web directamente en tu sistema
        
        Args:
            ruta_base_datos: Ruta a tu base de datos SQLite
        """
        self.server_url = "http://127.0.0.1:3000"
        self.ruta_bd = ruta_base_datos
        self.is_running = False
        
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
        
        # Verificar que existe la base de datos
        if not os.path.exists(self.ruta_bd):
            self.logger.error(f"❌ Base de datos no encontrada: {self.ruta_bd}")
            self.logger.info("📋 Bases de datos disponibles:")
            for archivo in os.listdir("."):
                if archivo.endswith(".db"):
                    self.logger.info(f"   - {archivo}")
        else:
            self.logger.info(f"✅ Base de datos encontrada: {self.ruta_bd}")
            
    def analizar_estructura_bd(self):
        """Analizar la estructura de tu base de datos para entender cómo insertar"""
        try:
            conn = sqlite3.connect(self.ruta_bd)
            cursor = conn.cursor()
            
            # Obtener todas las tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tablas = cursor.fetchall()
            
            self.logger.info(f"📊 Tablas encontradas en {self.ruta_bd}:")
            
            estructura = {}
            for tabla in tablas:
                nombre_tabla = tabla[0]
                
                # Obtener columnas de cada tabla
                cursor.execute(f"PRAGMA table_info({nombre_tabla})")
                columnas = cursor.fetchall()
                
                estructura[nombre_tabla] = {
                    'columnas': [col[1] for col in columnas],
                    'tipos': [col[2] for col in columnas]
                }
                
                self.logger.info(f"   📋 {nombre_tabla}:")
                for col in columnas:
                    self.logger.info(f"      - {col[1]} ({col[2]})")
                
                # Contar registros
                cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
                count = cursor.fetchone()[0]
                self.logger.info(f"      📊 {count} registros")
                
            conn.close()
            return estructura
            
        except Exception as e:
            self.logger.error(f"❌ Error analizando BD: {e}")
            return {}
    
    def detectar_tabla_pedidos(self, estructura):
        """Detectar automáticamente cuál tabla usar para pedidos"""
        posibles_tablas = []
        
        for tabla, info in estructura.items():
            columnas = [col.lower() for col in info['columnas']]
            
            # Buscar palabras clave que indiquen tabla de pedidos/ventas
            palabras_clave = ['cliente', 'total', 'precio', 'venta', 'pedido', 'fecha']
            score = sum(1 for palabra in palabras_clave if any(palabra in col for col in columnas))
            
            if score >= 2:  # Si tiene al menos 2 palabras clave
                posibles_tablas.append((tabla, score, info))
        
        if posibles_tablas:
            # Ordenar por score (más palabras clave = más probable)
            posibles_tablas.sort(key=lambda x: x[1], reverse=True)
            tabla_elegida = posibles_tablas[0]
            
            self.logger.info(f"🎯 Tabla detectada para pedidos: {tabla_elegida[0]}")
            self.logger.info(f"   📊 Score de confianza: {tabla_elegida[1]}")
            
            return tabla_elegida[0], tabla_elegida[2]
        
        return None, None
    
    def crear_mapeo_columnas(self, columnas_disponibles):
        """Crear mapeo automático de columnas"""
        mapeo = {}
        
        columnas_lower = [col.lower() for col in columnas_disponibles]
        
        # Mapear campos comunes
        mapeos_posibles = {
            'cliente': ['cliente', 'nombre', 'name', 'customer', 'client'],
            'telefono': ['telefono', 'tel', 'phone', 'celular', 'movil'],
            'total': ['total', 'precio', 'amount', 'monto', 'importe'],
            'fecha': ['fecha', 'date', 'timestamp', 'created', 'hora'],
            'estado': ['estado', 'status', 'estatus', 'situacion'],
            'items': ['items', 'productos', 'products', 'detalle', 'descripcion'],
            'origen': ['origen', 'source', 'tipo', 'canal'],
            'email': ['email', 'correo', 'mail'],
            'notas': ['notas', 'notes', 'observaciones', 'comentarios']
        }
        
        for campo, posibles_nombres in mapeos_posibles.items():
            for posible in posibles_nombres:
                for i, col in enumerate(columnas_lower):
                    if posible in col:
                        mapeo[campo] = columnas_disponibles[i]
                        break
                if campo in mapeo:
                    break
        
        self.logger.info("🗺️ Mapeo de columnas detectado:")
        for campo, columna in mapeo.items():
            self.logger.info(f"   {campo} → {columna}")
        
        return mapeo
    
    def obtener_pedidos_nuevos(self):
        """Obtener pedidos nuevos desde Caffe & Miga"""
        try:
            response = requests.get(f"{self.server_url}/pos/orders", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('orders', [])
            else:
                self.logger.error(f"❌ Error obteniendo pedidos: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Error de conexión: {e}")
            return []
    
    def insertar_pedido_en_sistema(self, pedido, tabla, mapeo):
        """Insertar pedido directamente en tu sistema"""
        try:
            customer = pedido.get('customer', {})
            items = pedido.get('items', [])
            
            # Verificar si ya existe
            if self.pedido_ya_existe(pedido['id'], tabla, mapeo):
                self.logger.info(f"⚠️ Pedido ya existe: {pedido['id'][:8]}...")
                return False
            
            conn = sqlite3.connect(self.ruta_bd)
            cursor = conn.cursor()
            
            # Preparar datos según el mapeo
            datos_pedido = {}
            
            if 'cliente' in mapeo:
                datos_pedido[mapeo['cliente']] = customer.get('name', 'Cliente Web')
            
            if 'telefono' in mapeo:
                datos_pedido[mapeo['telefono']] = customer.get('phone', '')
            
            if 'email' in mapeo:
                datos_pedido[mapeo['email']] = customer.get('email', '')
            
            if 'total' in mapeo:
                datos_pedido[mapeo['total']] = pedido.get('total', 0)
            
            if 'fecha' in mapeo:
                datos_pedido[mapeo['fecha']] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if 'estado' in mapeo:
                datos_pedido[mapeo['estado']] = 'Nuevo'
            
            if 'items' in mapeo:
                # Crear descripción de items
                items_texto = []
                for item in items:
                    items_texto.append(f"{item.get('quantity', 1)}x {item.get('title', 'Item')} (${item.get('unit_price', 0)})")
                datos_pedido[mapeo['items']] = " | ".join(items_texto)
            
            if 'origen' in mapeo:
                datos_pedido[mapeo['origen']] = 'E-commerce'
            
            if 'notas' in mapeo:
                datos_pedido[mapeo['notas']] = f"Pedido web - ID: {pedido['id'][:8]} - Método: {customer.get('payment_method', 'tarjeta')}"
            
            # Agregar campo para identificar pedidos web
            datos_pedido['id_web'] = pedido['id']  # Si esta columna existe
            
            # Construir query dinámicamente
            columnas = list(datos_pedido.keys())
            valores = list(datos_pedido.values())
            placeholders = ['?' for _ in valores]
            
            query = f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES ({', '.join(placeholders)})"
            
            cursor.execute(query, valores)
            conn.commit()
            pedido_id = cursor.lastrowid
            conn.close()
            
            self.logger.info(f"✅ Pedido insertado en {tabla}: {customer.get('name', 'Cliente')} - ${pedido.get('total', 0)}")
            
            # Marcar como procesado en Firebase
            self.marcar_como_procesado(pedido['id'])
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error insertando pedido: {e}")
            return False
    
    def pedido_ya_existe(self, firebase_id, tabla, mapeo):
        """Verificar si un pedido ya existe"""
        try:
            conn = sqlite3.connect(self.ruta_bd)
            cursor = conn.cursor()
            
            # Buscar por id_web si existe esa columna
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla} WHERE id_web = ?", (firebase_id,))
                count = cursor.fetchone()[0]
                conn.close()
                return count > 0
            except:
                # Si no existe id_web, buscar por otros campos
                if 'notas' in mapeo:
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla} WHERE {mapeo['notas']} LIKE ?", 
                                 (f"%{firebase_id[:8]}%",))
                    count = cursor.fetchone()[0]
                    conn.close()
                    return count > 0
                
            conn.close()
            return False
            
        except:
            return False
    
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
    
    def configurar_automaticamente(self):
        """Configurar automáticamente analizando tu base de datos"""
        self.logger.info("🔍 Analizando tu sistema automáticamente...")
        
        # Analizar estructura
        estructura = self.analizar_estructura_bd()
        
        if not estructura:
            self.logger.error("❌ No se pudo analizar la base de datos")
            return False
        
        # Detectar tabla de pedidos
        tabla, info_tabla = self.detectar_tabla_pedidos(estructura)
        
        if not tabla:
            self.logger.error("❌ No se pudo detectar tabla de pedidos automáticamente")
            self.logger.info("📋 Tablas disponibles:")
            for t in estructura.keys():
                self.logger.info(f"   - {t}")
            return False
        
        # Crear mapeo de columnas
        mapeo = self.crear_mapeo_columnas(info_tabla['columnas'])
        
        if not mapeo:
            self.logger.error("❌ No se pudo crear mapeo de columnas")
            return False
        
        # Guardar configuración
        self.tabla_pedidos = tabla
        self.mapeo_columnas = mapeo
        
        self.logger.info("✅ Configuración automática completada")
        return True
    
    def sincronizar_una_vez(self):
        """Sincronizar pedidos una vez"""
        if not hasattr(self, 'tabla_pedidos'):
            if not self.configurar_automaticamente():
                return False
        
        self.logger.info("🔄 Sincronizando pedidos...")
        
        pedidos = self.obtener_pedidos_nuevos()
        
        if not pedidos:
            self.logger.info("📭 No hay pedidos nuevos")
            return True
        
        procesados = 0
        for pedido in pedidos:
            if self.insertar_pedido_en_sistema(pedido, self.tabla_pedidos, self.mapeo_columnas):
                procesados += 1
        
        self.logger.info(f"✅ {procesados}/{len(pedidos)} pedidos procesados")
        return True
    
    def iniciar_monitoreo_automatico(self, intervalo=30):
        """Iniciar monitoreo automático en segundo plano"""
        if self.is_running:
            self.logger.warning("⚠️ El monitoreo ya está ejecutándose")
            return
        
        self.is_running = True
        self.logger.info(f"🔄 Iniciando monitoreo automático cada {intervalo} segundos...")
        
        def monitor_loop():
            while self.is_running:
                try:
                    self.sincronizar_una_vez()
                    time.sleep(intervalo)
                except Exception as e:
                    self.logger.error(f"❌ Error en monitoreo: {e}")
                    time.sleep(intervalo)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def detener_monitoreo(self):
        """Detener monitoreo automático"""
        self.is_running = False
        self.logger.info("🛑 Monitoreo detenido")

def main():
    """Función principal"""
    print("🔥 Integración Caffe & Miga - Cafetería Sistema")
    print("=" * 50)
    
    # Buscar archivo de base de datos automáticamente
    archivos_db = [f for f in os.listdir(".") if f.endswith(".db")]
    
    if not archivos_db:
        print("❌ No se encontraron archivos .db en la carpeta actual")
        print("💡 Asegúrate de ejecutar este script desde la carpeta de tu sistema")
        return
    
    if len(archivos_db) == 1:
        bd_elegida = archivos_db[0]
        print(f"✅ Base de datos detectada automáticamente: {bd_elegida}")
    else:
        print("📋 Múltiples bases de datos encontradas:")
        for i, db in enumerate(archivos_db):
            print(f"   {i+1}. {db}")
        
        try:
            opcion = int(input("Selecciona el número de tu base de datos: ")) - 1
            bd_elegida = archivos_db[opcion]
        except:
            print("❌ Opción inválida, usando la primera")
            bd_elegida = archivos_db[0]
    
    # Crear integración
    integration = CafeteriaSystemIntegration(bd_elegida)
    
    print("\nOpciones:")
    print("1. 🔍 Analizar mi sistema automáticamente")
    print("2. 🔄 Sincronizar pedidos ahora")
    print("3. ▶️ Iniciar monitoreo automático")
    print("4. 🛑 Salir")
    
    while True:
        try:
            opcion = input("\nSelecciona una opción (1-4): ")
            
            if opcion == "1":
                integration.configurar_automaticamente()
                
            elif opcion == "2":
                integration.sincronizar_una_vez()
                
            elif opcion == "3":
                integration.iniciar_monitoreo_automatico(30)
                print("🔄 Monitoreo iniciado. Presiona Ctrl+C para detener...")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    integration.detener_monitoreo()
                    print("\n🛑 Monitoreo detenido")
                    break
                    
            elif opcion == "4":
                print("👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción inválida")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break

if __name__ == "__main__":
    main()
