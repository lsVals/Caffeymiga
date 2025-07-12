# 🔥 Guía de Integración POS - Caffe & Miga

## ¿Cómo integrar tu sistema POS existente?

### 📋 **Paso 1: Copia el archivo cliente**
1. Copia `pos_client.py` a la carpeta de tu sistema POS
2. Instala la dependencia: `pip install requests`

### 📋 **Paso 2: Configuración básica**

```python
# En tu sistema POS, importa el cliente
from pos_client import CaffeYMigaPOSClient

# Crear instancia del cliente
pos = CaffeYMigaPOSClient("http://127.0.0.1:3000")
```

### 📋 **Paso 3: Opciones de integración**

#### **Opción A: Consultar pedidos manualmente**
```python
# Obtener pedidos nuevos
orders = pos.get_new_orders()

for order in orders:
    print(f"Nuevo pedido: {order['customer']['name']}")
    # Tu lógica aquí...
    
    # Marcar como preparando
    pos.update_order_status(order['id'], 'preparando')
```

#### **Opción B: Monitoreo automático cada 30 segundos**
```python
def mi_funcion_procesar(orders):
    for order in orders:
        # Tu lógica de procesamiento
        print(f"Procesando: {order['customer']['name']}")
        
        # Integrar con tu sistema
        mi_sistema.agregar_pedido(order)
        mi_impresora.imprimir_ticket(order)
        
        # Actualizar estado
        pos.update_order_status(order['id'], 'preparando')

# Iniciar monitoreo automático
pos.start_monitoring(mi_funcion_procesar, interval=30)
```

### 📋 **Paso 4: Estados de pedidos**

```python
# Estados disponibles:
# - 'preparando': Pedido en preparación
# - 'listo': Pedido listo para entregar
# - 'entregado': Pedido entregado al cliente
# - 'cancelado': Pedido cancelado

pos.update_order_status(order_id, 'listo')
```

### 📋 **Paso 5: Estructura de datos**

Los pedidos llegan con esta estructura:
```json
{
  "id": "abc123...",
  "customer": {
    "name": "Juan Pérez",
    "email": "juan@email.com",
    "phone": "5551234567",
    "payment_method": "tarjeta"
  },
  "items": [
    {
      "id": "cafe-americano",
      "title": "Café Americano",
      "quantity": 2,
      "unit_price": 35.00
    }
  ],
  "total": 70.00,
  "currency": "MXN",
  "created_at": "2024-01-01T10:00:00Z",
  "payment_status": "approved"
}
```

## 🚀 **Ejemplos de integración con diferentes sistemas:**

### **Sistema con Base de Datos MySQL**
```python
import mysql.connector
from pos_client import CaffeYMigaPOSClient

def integrar_con_mysql():
    pos = CaffeYMigaPOSClient()
    orders = pos.get_new_orders()
    
    conn = mysql.connector.connect(
        host='localhost',
        user='usuario',
        password='password',
        database='mi_pos'
    )
    
    for order in orders:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pedidos (id, cliente, telefono, total, items)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            order['id'],
            order['customer']['name'],
            order['customer']['phone'],
            order['total'],
            json.dumps(order['items'])
        ))
        conn.commit()
        
        # Marcar como procesado
        pos.update_order_status(order['id'], 'preparando')
```

### **Sistema con Impresora Térmica**
```python
from escpos.printer import Usb
from pos_client import CaffeYMigaPOSClient

def imprimir_tickets():
    pos = CaffeYMigaPOSClient()
    orders = pos.get_new_orders()
    
    # Configurar impresora (ajusta según tu modelo)
    printer = Usb(0x04b8, 0x0202)  # Epson
    
    for order in orders:
        printer.text(f"CAFFE & MIGA\n")
        printer.text(f"Pedido: {order['id'][:8]}\n")
        printer.text(f"Cliente: {order['customer']['name']}\n")
        printer.text(f"Teléfono: {order['customer']['phone']}\n")
        printer.text("-" * 32 + "\n")
        
        for item in order['items']:
            printer.text(f"{item['quantity']}x {item['title']}\n")
            printer.text(f"    ${item['unit_price']:.2f}\n")
        
        printer.text("-" * 32 + "\n")
        printer.text(f"TOTAL: ${order['total']:.2f}\n")
        printer.cut()
        
        # Marcar como preparando
        pos.update_order_status(order['id'], 'preparando')
```

### **Sistema con Notificaciones**
```python
import smtplib
from pos_client import CaffeYMigaPOSClient

def enviar_notificaciones():
    pos = CaffeYMigaPOSClient()
    orders = pos.get_new_orders()
    
    for order in orders:
        # Enviar email al equipo
        send_email(
            to="cocina@caffeymiga.com",
            subject=f"Nuevo pedido: {order['customer']['name']}",
            body=f"Total: ${order['total']}\nTeléfono: {order['customer']['phone']}"
        )
        
        # Marcar como notificado
        pos.update_order_status(order['id'], 'preparando')
```

## 🔧 **Configuración avanzada**

### **Cambiar URL del servidor**
```python
# Si tu servidor está en otra IP/Puerto
pos = CaffeYMigaPOSClient("http://192.168.1.100:3000")
```

### **Manejar errores de conexión**
```python
def verificar_conexion():
    pos = CaffeYMigaPOSClient()
    stats = pos.get_dashboard_stats()
    
    if stats:
        firebase_status = stats.get('firebase_status')
        print(f"Firebase: {firebase_status}")
        print(f"Pedidos totales: {stats.get('statistics', {}).get('total', 0)}")
    else:
        print("❌ No se pudo conectar al servidor")
```

## 📞 **¿Necesitas ayuda personalizada?**

Si tu sistema POS tiene características específicas, puedo ayudarte a crear una integración personalizada. Solo dime:

1. **¿Qué lenguaje usa tu POS?** (Python, PHP, Java, C#, etc.)
2. **¿Qué base de datos usa?** (MySQL, PostgreSQL, SQLite, etc.)
3. **¿Tiene API REST?** ¿O necesitas archivos/webhooks?
4. **¿Cómo procesas pedidos actualmente?**

## 🔥 **Endpoints disponibles:**

- `GET /pos/orders` - Obtener pedidos pendientes
- `PUT /pos/orders/{id}/status` - Actualizar estado
- `GET /pos/dashboard` - Estadísticas y estado

**¡Tu sistema POS ahora puede recibir pedidos automáticamente sin WhatsApp!** 🚀
