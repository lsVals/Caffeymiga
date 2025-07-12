# -*- coding: utf-8 -*-
"""
Configuración de rendimiento para el sistema de cafetería
Optimizaciones para mejorar la velocidad y estabilidad del sistema
"""

# Configuraciones de rendimiento
CONFIGURACION_RENDIMIENTO = {
    # Interfaz gráfica
    'GUI': {
        'UPDATE_DELAY': 100,  # ms entre actualizaciones de interfaz
        'REFRESH_INTERVAL': 1000,  # ms para refrescar datos
        'ANIMATION_SPEED': 250,  # ms para animaciones
        'BATCH_SIZE': 50  # elementos procesados por lote
    },
    
    # Base de datos
    'DATABASE': {
        'CONNECTION_TIMEOUT': 30,  # segundos
        'BATCH_INSERT_SIZE': 100,  # registros por lote
        'VACUUM_FREQUENCY': 7,  # días entre VACUUM
        'BACKUP_FREQUENCY': 24  # horas entre backups automáticos
    },
    
    # Monitoreo web
    'WEB_MONITORING': {
        'CHECK_INTERVAL': 30,  # segundos entre verificaciones
        'REQUEST_TIMEOUT': 10,  # segundos timeout para requests
        'MAX_RETRIES': 3,  # intentos máximos
        'RETRY_DELAY': 5  # segundos entre reintentos
    },
    
    # Archivos y logs
    'FILES': {
        'LOG_MAX_SIZE': 1024*1024,  # 1MB máximo por log
        'LOG_BACKUP_COUNT': 5,  # archivos de log a mantener
        'TEMP_CLEANUP_HOURS': 24,  # horas para limpiar temporales
        'PDF_CACHE_SIZE': 20  # PDFs en caché
    },
    
    # Memoria
    'MEMORY': {
        'MAX_CACHE_SIZE': 100,  # elementos en caché
        'GC_INTERVAL': 300,  # segundos entre garbage collection
        'PRELOAD_DATA': True,  # precargar datos en memoria
        'LAZY_LOADING': False  # carga diferida de imágenes/datos pesados
    }
}

def get_config(seccion, clave=None):
    """Obtener configuración de rendimiento"""
    if clave:
        return CONFIGURACION_RENDIMIENTO.get(seccion, {}).get(clave)
    return CONFIGURACION_RENDIMIENTO.get(seccion, {})

def set_config(seccion, clave, valor):
    """Establecer configuración de rendimiento"""
    if seccion not in CONFIGURACION_RENDIMIENTO:
        CONFIGURACION_RENDIMIENTO[seccion] = {}
    CONFIGURACION_RENDIMIENTO[seccion][clave] = valor

def optimizar_memoria():
    """Ejecutar optimizaciones de memoria"""
    import gc
    import sqlite3
    
    # Forzar garbage collection
    gc.collect()
    
    # Optimizar SQLite
    try:
        conn = sqlite3.connect('ventas.db')
        conn.execute('PRAGMA optimize')
        conn.close()
    except Exception:
        pass
    
    return True

def verificar_rendimiento():
    """Verificar el estado del rendimiento del sistema"""
    import os
    import psutil
    
    stats = {
        'memoria_disponible': psutil.virtual_memory().available,
        'memoria_usada_porcentaje': psutil.virtual_memory().percent,
        'cpu_porcentaje': psutil.cpu_percent(interval=1),
        'espacio_disco': psutil.disk_usage('.').free
    }
    
    # Alertas de rendimiento
    alertas = []
    if stats['memoria_usada_porcentaje'] > 85:
        alertas.append("Memoria RAM alta")
    if stats['cpu_porcentaje'] > 90:
        alertas.append("CPU sobrecargado")
    if stats['espacio_disco'] < 100*1024*1024:  # 100MB
        alertas.append("Poco espacio en disco")
    
    return stats, alertas

def configurar_logging_optimizado():
    """Configurar logging optimizado para rendimiento"""
    import logging
    from logging.handlers import RotatingFileHandler
    
    # Crear handler con rotación automática
    handler = RotatingFileHandler(
        'cafeteria_log.txt',
        maxBytes=get_config('FILES', 'LOG_MAX_SIZE'),
        backupCount=get_config('FILES', 'LOG_BACKUP_COUNT')
    )
    
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s:%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Configurar logger raíz
    logging.getLogger().handlers.clear()
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)
    
    return True

if __name__ == "__main__":
    # Prueba de configuración
    print("Configuración de rendimiento cargada:")
    for seccion, configs in CONFIGURACION_RENDIMIENTO.items():
        print(f"\n[{seccion}]")
        for clave, valor in configs.items():
            print(f"  {clave}: {valor}")
    
    # Verificar rendimiento
    try:
        stats, alertas = verificar_rendimiento()
        print(f"\nEstado del sistema:")
        print(f"Memoria disponible: {stats['memoria_disponible']//1024//1024} MB")
        print(f"Uso de memoria: {stats['memoria_usada_porcentaje']:.1f}%")
        print(f"Uso de CPU: {stats['cpu_porcentaje']:.1f}%")
        
        if alertas:
            print("⚠️  Alertas:", ", ".join(alertas))
        else:
            print("✅ Sistema funcionando correctamente")
    except ImportError:
        print("⚠️  Instalar 'psutil' para monitoreo completo: pip install psutil")
