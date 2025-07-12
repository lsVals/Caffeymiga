# Configuración para integrar con tu base de datos SQLite existente

# 1. INFORMACIÓN DE TU BASE DE DATOS ACTUAL
# Cambia estos valores según tu sistema:

MI_BASE_DATOS = {
    "ruta": "C:/ruta/a/tu/pos.db",  # ← Ruta de tu base de datos
    "tabla_pedidos": "pedidos",      # ← Nombre de tu tabla de pedidos
    "columnas": {
        "id": "id",                  # ← Tu columna de ID
        "cliente": "cliente_nombre", # ← Tu columna de cliente
        "telefono": "telefono",      # ← Tu columna de teléfono
        "total": "total",            # ← Tu columna de total
        "items": "items_json",       # ← Tu columna de items (JSON)
        "estado": "estado",          # ← Tu columna de estado
        "fecha": "fecha_creacion"    # ← Tu columna de fecha
    }
}

# 2. CONFIGURACIÓN DEL SERVIDOR
SERVIDOR_CONFIG = {
    "url": "http://127.0.0.1:3000",  # URL del servidor Caffe & Miga
    "timeout": 10,                   # Timeout en segundos
    "intervalo": 30                  # Intervalo de sincronización en segundos
}

# 3. MAPEO DE ESTADOS
# Cómo se relacionan los estados de Firebase con tu POS
MAPEO_ESTADOS = {
    # Estado Firebase -> Estado en tu POS
    "nuevo": "pendiente",
    "preparando": "en_cocina", 
    "listo": "listo_entrega",
    "entregado": "completado",
    "cancelado": "cancelado"
}

# 4. CONFIGURACIÓN DE LOGGING
LOGGING_CONFIG = {
    "archivo": "pos_integration.log",
    "nivel": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "formato": "%(asctime)s - %(levelname)s - %(message)s"
}

# 5. CONFIGURACIÓN DE NOTIFICACIONES (opcional)
NOTIFICACIONES = {
    "habilitar": True,
    "sonido": True,
    "email": {
        "habilitar": False,
        "smtp_server": "smtp.gmail.com",
        "puerto": 587,
        "usuario": "tu_email@gmail.com",
        "password": "tu_password",
        "destinatario": "cocina@turestaurante.com"
    }
}

# 6. FUNCIÓN PARA ADAPTAR PEDIDOS A TU FORMATO
def adaptar_pedido_firebase_a_mi_pos(pedido_firebase):
    """
    Convierte un pedido de Firebase al formato de tu POS
    PERSONALIZA ESTA FUNCIÓN según tu estructura
    """
    
    # Extraer datos del pedido Firebase
    customer = pedido_firebase.get('customer', {})
    items = pedido_firebase.get('items', [])
    
    # Convertir al formato de tu POS
    mi_pedido = {
        MI_BASE_DATOS["columnas"]["id"]: f"CF_{pedido_firebase['id'][:8]}",
        MI_BASE_DATOS["columnas"]["cliente"]: customer.get('name', 'Cliente'),
        MI_BASE_DATOS["columnas"]["telefono"]: customer.get('phone', ''),
        MI_BASE_DATOS["columnas"]["total"]: pedido_firebase.get('total', 0),
        MI_BASE_DATOS["columnas"]["items"]: json.dumps(items),
        MI_BASE_DATOS["columnas"]["estado"]: MAPEO_ESTADOS.get('nuevo', 'pendiente'),
        MI_BASE_DATOS["columnas"]["fecha"]: datetime.now().isoformat()
    }
    
    return mi_pedido

# 7. EJEMPLO DE QUERY PARA INSERTAR EN TU BD
def generar_query_insercion():
    """Generar query SQL para insertar en tu base de datos"""
    
    columnas = list(MI_BASE_DATOS["columnas"].values())
    placeholders = ['?' for _ in columnas]
    
    query = f"""
        INSERT INTO {MI_BASE_DATOS["tabla_pedidos"]} 
        ({', '.join(columnas)}) 
        VALUES ({', '.join(placeholders)})
    """
    
    return query

# 8. FUNCIÓN DE VALIDACIÓN
def validar_configuracion():
    """Validar que la configuración esté completa"""
    
    # Verificar que la base de datos existe
    import os
    if not os.path.exists(MI_BASE_DATOS["ruta"]):
        print(f"⚠️ ADVERTENCIA: Base de datos no encontrada en {MI_BASE_DATOS['ruta']}")
        return False
    
    # Verificar conexión al servidor
    try:
        import requests
        response = requests.get(f"{SERVIDOR_CONFIG['url']}/pos/dashboard", timeout=5)
        if response.status_code == 200:
            print("✅ Conexión al servidor exitosa")
            return True
        else:
            print(f"⚠️ Servidor responde con código: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False

if __name__ == "__main__":
    import json
    from datetime import datetime
    
    print("🔧 Configuración POS - Caffe & Miga")
    print("=" * 40)
    
    # Mostrar configuración actual
    print(f"Base de datos: {MI_BASE_DATOS['ruta']}")
    print(f"Tabla: {MI_BASE_DATOS['tabla_pedidos']}")
    print(f"Servidor: {SERVIDOR_CONFIG['url']}")
    
    # Validar configuración
    if validar_configuracion():
        print("✅ Configuración válida")
    else:
        print("❌ Revisar configuración")
    
    # Mostrar query de ejemplo
    print(f"\nQuery de inserción:")
    print(generar_query_insercion())
