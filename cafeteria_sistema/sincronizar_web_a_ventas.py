#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SINCRONIZADOR DE PEDIDOS WEB A SISTEMA DE VENTAS
===============================================

Este script sincroniza automáticamente los pedidos web pendientes
desde la base de datos pos_pedidos.db hacia el sistema de ventas
principal en ventas.db.

Funcionalidades:
- Detecta pedidos pendientes en pos_pedidos.db
- Los convierte a tickets en ventas.db
- Marca los pedidos como 'procesados' 
- Genera logs de actividad
- Puede ejecutarse manualmente o como servicio

Autor: Sistema Caffè & Miga
Fecha: Julio 2025
"""

import sqlite3
import json
import logging
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sincronizacion_web.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class SincronizadorWebVentas:
    """Clase principal para sincronizar pedidos web con sistema de ventas"""
    
    def __init__(self, db_web_path: str = "pos_pedidos.db", db_ventas_path: str = "ventas.db"):
        """
        Inicializar sincronizador
        
        Args:
            db_web_path: Ruta a la base de datos de pedidos web
            db_ventas_path: Ruta a la base de datos de ventas
        """
        self.db_web_path = db_web_path
        self.db_ventas_path = db_ventas_path
        
        # Verificar que las bases de datos existan
        self._verificar_bases_datos()
        
        # Inicializar base de datos de ventas si es necesario
        self._inicializar_db_ventas()
        
        logger.info("✅ Sincronizador inicializado correctamente")
    
    def _verificar_bases_datos(self) -> None:
        """Verificar que las bases de datos existan"""
        if not os.path.exists(self.db_web_path):
            raise FileNotFoundError(f"❌ No se encontró la base de datos web: {self.db_web_path}")
        
        if not os.path.exists(self.db_ventas_path):
            logger.warning(f"⚠️ Base de datos de ventas no existe, se creará: {self.db_ventas_path}")
    
    def _inicializar_db_ventas(self) -> None:
        """Inicializar la base de datos de ventas si no existe"""
        try:
            conn = sqlite3.connect(self.db_ventas_path)
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
                    motivo_cancelacion TEXT,
                    origen TEXT DEFAULT 'LOCAL',
                    pedido_web_id TEXT
                )
            ''')
            
            # Agregar columnas nuevas si no existen
            try:
                c.execute("ALTER TABLE tickets ADD COLUMN origen TEXT DEFAULT 'LOCAL'")
            except sqlite3.OperationalError:
                pass  # La columna ya existe
            
            try:
                c.execute("ALTER TABLE tickets ADD COLUMN pedido_web_id TEXT")
            except sqlite3.OperationalError:
                pass  # La columna ya existe
            
            conn.commit()
            conn.close()
            logger.info("✅ Base de datos de ventas inicializada")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos de ventas: {e}")
            raise
    
    def obtener_pedidos_pendientes(self) -> List[Dict[str, Any]]:
        """
        Obtener pedidos pendientes de la base de datos web
        
        Returns:
            Lista de diccionarios con los pedidos pendientes
        """
        try:
            conn = sqlite3.connect(self.db_web_path)
            c = conn.cursor()
            
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
                    'metodo_pago': row[7] if row[7] else 'Web',
                    'fecha_creacion': row[8]
                }
                pedidos.append(pedido)
            
            conn.close()
            logger.info(f"📋 Encontrados {len(pedidos)} pedidos pendientes")
            return pedidos
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo pedidos pendientes: {e}")
            return []
    
    def procesar_items_pedido(self, items_json: str) -> List[Dict[str, Any]]:
        """
        Procesar los items de un pedido desde JSON
        
        Args:
            items_json: String JSON con los items del pedido
            
        Returns:
            Lista de items procesados
        """
        try:
            if not items_json or items_json == '[]':
                return []
            
            items = json.loads(items_json)
            items_procesados = []
            
            for item in items:
                item_procesado = {
                    'nombre': item.get('name', item.get('nombre', 'Producto Web')),
                    'cantidad': int(item.get('quantity', item.get('cantidad', 1))),
                    'precio': float(item.get('price', item.get('precio', 0)))
                }
                items_procesados.append(item_procesado)
            
            return items_procesados
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"⚠️ Error procesando items del pedido: {e}")
            return [{'nombre': 'Pedido Web (Error en items)', 'cantidad': 1, 'precio': 0}]
    
    def agregar_ticket_ventas(self, pedido: Dict[str, Any]) -> bool:
        """
        Agregar un pedido como tickets en la base de datos de ventas
        
        Args:
            pedido: Diccionario con los datos del pedido
            
        Returns:
            True si se agregó correctamente, False en caso contrario
        """
        try:
            items = self.procesar_items_pedido(pedido['items'])
            
            if not items:
                logger.warning(f"⚠️ Pedido {pedido['id']} no tiene items válidos")
                return False
            
            conn = sqlite3.connect(self.db_ventas_path)
            c = conn.cursor()
            
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            tickets_agregados = 0
            
            for item in items:
                # Crear descripción del producto con información del cliente
                producto_desc = f"{item['nombre']} (WEB)"
                if pedido['cliente_nombre'] != 'Cliente Web':
                    producto_desc += f" - {pedido['cliente_nombre']}"
                
                # Información adicional en motivo_cancelacion para referencia
                info_adicional = (
                    f"Pedido web ID: {pedido['id']} | "
                    f"Cliente: {pedido['cliente_nombre']} | "
                    f"Tel: {pedido['cliente_telefono']} | "
                    f"Recogida: {pedido['hora_recogida']}"
                )
                
                c.execute("""
                    INSERT INTO tickets 
                    (fecha, producto, cantidad, precio, pago, estado, motivo_cancelacion, origen, pedido_web_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    fecha_actual,
                    producto_desc,
                    item['cantidad'],
                    item['precio'],
                    f"WEB-{pedido['metodo_pago']}",
                    'Activo',
                    info_adicional,
                    'WEB',
                    pedido['id']
                ))
                
                tickets_agregados += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Pedido {pedido['id']} convertido a {tickets_agregados} tickets")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error agregando pedido {pedido['id']} a ventas: {e}")
            return False
    
    def marcar_pedido_procesado(self, pedido_id: str) -> bool:
        """
        Marcar un pedido como procesado en la base de datos web
        
        Args:
            pedido_id: ID del pedido a marcar como procesado
            
        Returns:
            True si se marcó correctamente, False en caso contrario
        """
        try:
            conn = sqlite3.connect(self.db_web_path)
            c = conn.cursor()
            
            fecha_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            c.execute("""
                UPDATE pedidos 
                SET estado = 'procesado', fecha_actualizacion = ?
                WHERE id = ?
            """, (fecha_actualizacion, pedido_id))
            
            if c.rowcount > 0:
                conn.commit()
                conn.close()
                logger.info(f"✅ Pedido {pedido_id} marcado como procesado")
                return True
            else:
                conn.close()
                logger.warning(f"⚠️ No se encontró el pedido {pedido_id} para actualizar")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error marcando pedido {pedido_id} como procesado: {e}")
            return False
    
    def sincronizar_pedidos(self) -> Tuple[int, int]:
        """
        Sincronizar todos los pedidos pendientes
        
        Returns:
            Tupla con (pedidos_procesados, pedidos_fallidos)
        """
        logger.info("🔄 Iniciando sincronización de pedidos web...")
        
        pedidos = self.obtener_pedidos_pendientes()
        
        if not pedidos:
            logger.info("✅ No hay pedidos pendientes para sincronizar")
            return (0, 0)
        
        pedidos_procesados = 0
        pedidos_fallidos = 0
        
        for pedido in pedidos:
            try:
                logger.info(f"🔄 Procesando pedido {pedido['id']} - Cliente: {pedido['cliente_nombre']}")
                
                # Agregar a la base de datos de ventas
                if self.agregar_ticket_ventas(pedido):
                    # Marcar como procesado en la base de datos web
                    if self.marcar_pedido_procesado(pedido['id']):
                        pedidos_procesados += 1
                        logger.info(f"✅ Pedido {pedido['id']} sincronizado exitosamente")
                    else:
                        logger.warning(f"⚠️ Pedido {pedido['id']} agregado a ventas pero no se pudo marcar como procesado")
                        pedidos_fallidos += 1
                else:
                    pedidos_fallidos += 1
                    logger.error(f"❌ Error procesando pedido {pedido['id']}")
                    
            except Exception as e:
                pedidos_fallidos += 1
                logger.error(f"❌ Error inesperado procesando pedido {pedido['id']}: {e}")
        
        logger.info(f"🏁 Sincronización completada: {pedidos_procesados} exitosos, {pedidos_fallidos} fallidos")
        return (pedidos_procesados, pedidos_fallidos)
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de sincronización
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            # Estadísticas de pedidos web
            conn_web = sqlite3.connect(self.db_web_path)
            c_web = conn_web.cursor()
            
            c_web.execute("SELECT COUNT(*) FROM pedidos WHERE estado = 'pendiente'")
            pendientes = c_web.fetchone()[0]
            
            c_web.execute("SELECT COUNT(*) FROM pedidos WHERE estado = 'procesado'")
            procesados = c_web.fetchone()[0]
            
            c_web.execute("SELECT COUNT(*) FROM pedidos")
            total_web = c_web.fetchone()[0]
            
            conn_web.close()
            
            # Estadísticas de ventas
            conn_ventas = sqlite3.connect(self.db_ventas_path)
            c_ventas = conn_ventas.cursor()
            
            c_ventas.execute("SELECT COUNT(*) FROM tickets WHERE origen = 'WEB'")
            tickets_web = c_ventas.fetchone()[0]
            
            c_ventas.execute("SELECT COUNT(*) FROM tickets WHERE origen = 'LOCAL' OR origen IS NULL")
            tickets_local = c_ventas.fetchone()[0]
            
            c_ventas.execute("SELECT COUNT(*) FROM tickets")
            total_tickets = c_ventas.fetchone()[0]
            
            conn_ventas.close()
            
            estadisticas = {
                'pedidos_web': {
                    'pendientes': pendientes,
                    'procesados': procesados,
                    'total': total_web
                },
                'tickets_ventas': {
                    'web': tickets_web,
                    'local': tickets_local,
                    'total': total_tickets
                },
                'fecha_consulta': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return estadisticas
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}
    
    def mostrar_estadisticas(self) -> None:
        """Mostrar estadísticas de sincronización"""
        estadisticas = self.obtener_estadisticas()
        
        if not estadisticas:
            print("❌ No se pudieron obtener las estadísticas")
            return
        
        print("\n" + "="*60)
        print("📊 ESTADÍSTICAS DE SINCRONIZACIÓN")
        print("="*60)
        print(f"📅 Fecha de consulta: {estadisticas['fecha_consulta']}")
        print()
        print("🌐 PEDIDOS WEB:")
        print(f"   • Pendientes: {estadisticas['pedidos_web']['pendientes']}")
        print(f"   • Procesados: {estadisticas['pedidos_web']['procesados']}")
        print(f"   • Total: {estadisticas['pedidos_web']['total']}")
        print()
        print("🎫 TICKETS DE VENTAS:")
        print(f"   • Desde web: {estadisticas['tickets_ventas']['web']}")
        print(f"   • Locales: {estadisticas['tickets_ventas']['local']}")
        print(f"   • Total: {estadisticas['tickets_ventas']['total']}")
        print("="*60)

def main():
    """Función principal del script"""
    print("🚀 SINCRONIZADOR DE PEDIDOS WEB - CAFFÈ & MIGA")
    print("=" * 50)
    
    try:
        # Crear instancia del sincronizador
        sincronizador = SincronizadorWebVentas()
        
        # Mostrar estadísticas iniciales
        print("\n📊 Estado inicial:")
        sincronizador.mostrar_estadisticas()
        
        # Realizar sincronización
        print("\n🔄 Iniciando sincronización...")
        procesados, fallidos = sincronizador.sincronizar_pedidos()
        
        # Mostrar resultados
        print(f"\n✅ Sincronización completada:")
        print(f"   • Pedidos procesados: {procesados}")
        print(f"   • Pedidos fallidos: {fallidos}")
        
        if procesados > 0:
            print("\n📊 Estado final:")
            sincronizador.mostrar_estadisticas()
        
        print("\n🏁 Proceso terminado exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error crítico en sincronización: {e}")
        print(f"\n❌ Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
