# 🔥 Integración POS SQLite - Caffe & Miga

## 📋 **¿Qué hay en esta carpeta?**

Esta carpeta contiene todo lo necesario para integrar tu sistema POS (Python + SQLite) con el e-commerce de Caffe & Miga.

### **Archivos incluidos:**

1. **`pos_sqlite_client.py`** - Cliente completo con base de datos propia
2. **`simple_integration.py`** - Script simple para integrar con tu BD existente  
3. **`config.py`** - Configuración personalizable
4. **`README.md`** - Este archivo

## 🚀 **Opción 1: Usar cliente completo (Recomendado)**

Si quieres un sistema completo nuevo:

```bash
# 1. Copiar archivo a tu sistema
cp pos_sqlite_client.py /ruta/a/tu/pos/

# 2. Instalar dependencia
pip install requests

# 3. Ejecutar
python pos_sqlite_client.py
```

**Características:**
- ✅ Base de datos SQLite automática
- ✅ Monitoreo en tiempo real
- ✅ Interfaz de consola
- ✅ Historial de estados
- ✅ Estadísticas

## 🔧 **Opción 2: Integrar con tu sistema existente**

Si ya tienes un POS funcionando:

### **Paso 1: Configurar**
Edita `config.py` con los datos de tu base de datos:

```python
MI_BASE_DATOS = {
    "ruta": "/ruta/a/tu/pos.db",     # ← Tu base de datos
    "tabla_pedidos": "pedidos",      # ← Tu tabla de pedidos
    "columnas": {
        "id": "id",                  # ← Tus columnas
        "cliente": "cliente_nombre", 
        "telefono": "telefono",
        "total": "total",
        # ... etc
    }
}
```

### **Paso 2: Usar script simple**
Copia `simple_integration.py` a tu sistema y ejecútalo:

```python
from simple_integration import sincronizar_pedidos

# En tu código existente, agregar:
sincronizar_pedidos()  # Cada 30 segundos
```

### **Paso 3: Personalizar función**
En `simple_integration.py`, modifica la función `agregar_a_mi_pos()`:

```python
def agregar_a_mi_pos(self, pedido):
    # Tu lógica aquí:
    # - Insertar en tu BD
    # - Imprimir ticket
    # - Enviar notificación
    # - etc.
```

## 📊 **Estructura de datos que recibes:**

```json
{
  "id": "firebase_id_unico",
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
  "payment_status": "approved",
  "created_at": "2024-01-01T10:00:00Z"
}
```

## 🔄 **Estados de pedidos:**

- **`nuevo`** → Pedido recién llegado
- **`preparando`** → En preparación  
- **`listo`** → Listo para entregar
- **`entregado`** → Entregado al cliente
- **`cancelado`** → Cancelado

## 🛠 **Ejemplos de uso:**

### **Ejemplo 1: Monitoreo básico**
```python
from pos_sqlite_client import CaffeYMigaSQLiteClient

client = CaffeYMigaSQLiteClient()

# Obtener pedidos nuevos
pedidos = client.obtener_pedidos_nuevos()

# Mostrar pedidos activos  
activos = client.obtener_pedidos_activos()

# Cambiar estado
client.actualizar_estado_pedido("POS_123", "preparando")
```

### **Ejemplo 2: Integración con impresora**
```python
def imprimir_ticket(pedido):
    # Tu código de impresión
    print(f"TICKET: {pedido['customer']['name']}")
    for item in pedido['items']:
        print(f"{item['quantity']}x {item['title']}")

# En simple_integration.py
def agregar_a_mi_pos(self, pedido):
    # Guardar en BD
    self.insertar_en_mi_bd(pedido)
    
    # Imprimir ticket
    imprimir_ticket(pedido)
    
    # Marcar como procesado
    return True
```

### **Ejemplo 3: Notificaciones**
```python
def enviar_notificacion(pedido):
    # Email, SMS, sonido, etc.
    import winsound
    winsound.Beep(1000, 500)  # Sonido en Windows
    
    # O enviar WhatsApp, email, etc.
```

## 🔧 **Configuración avanzada:**

### **Cambiar servidor:**
```python
client = CaffeYMigaSQLiteClient("http://192.168.1.100:3000")
```

### **Cambiar intervalo:**
```python
client.iniciar_monitoreo(intervalo=60)  # Cada minuto
```

### **Base de datos personalizada:**
```python
client = CaffeYMigaSQLiteClient(db_path="/mi/pos/pedidos.db")
```

## 📞 **¿Cómo integrar paso a paso?**

### **Si tu POS es simple:**
1. Copia `pos_sqlite_client.py` a tu carpeta
2. Ejecuta: `python pos_sqlite_client.py`
3. Selecciona opción 5 (monitoreo automático)

### **Si tu POS es complejo:**
1. Edita `config.py` con tus datos
2. Copia `simple_integration.py` a tu carpeta  
3. Importa y usa `sincronizar_pedidos()` en tu código
4. Personaliza `agregar_a_mi_pos()` según tu sistema

### **Si necesitas ayuda específica:**
Dime:
- ¿Cómo se llaman tus tablas?
- ¿Qué columnas tienes?
- ¿Cómo procesas pedidos actualmente?
- ¿Usas impresora, notificaciones, etc.?

## 🚀 **Flujo completo:**

```
🛒 Cliente hace pedido → 💳 Mercado Pago → 🔥 Firebase → 📱 Tu POS SQLite
```

1. Cliente hace pedido en web
2. Pago se procesa con Mercado Pago
3. Pedido se guarda en Firebase automáticamente
4. Tu POS consulta cada 30 segundos
5. Nuevo pedido aparece en tu sistema
6. Procesas el pedido normalmente
7. Actualizas estado (preparando → listo → entregado)

## ⚡ **¡Ya no más WhatsApp!**

Los pedidos llegan **directamente** a tu sistema POS en tiempo real. ¡Sin intervención manual!

---

**¿Necesitas ayuda personalizada? ¡Solo pregunta!** 🔥
