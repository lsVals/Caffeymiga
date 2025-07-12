# 🔥 Integración Específica para cafeteria_sistema

## 📋 **¿Qué necesitas hacer?**

Tu sistema en `cafeteria_sistema` puede recibir pedidos automáticamente del e-commerce. Aquí te explico paso a paso.

## 🚀 **Instalación Rápida**

### **Paso 1: Copiar el instalador**
1. Copia el archivo `instalar_en_cafeteria_sistema.py` 
2. Pégalo en: `C:\Users\victo\OneDrive\Escritorio\cafeteria_sistema\`
3. Ejecuta: `python instalar_en_cafeteria_sistema.py`

### **Paso 2: Configurar tu base de datos**
Edita el archivo generado `caffe_miga_integration/config.py`:

```python
MI_BD_CONFIG = {
    "archivo": "tu_base_datos.db",     # ← Nombre de tu archivo .db
    "tabla": "tu_tabla_pedidos",       # ← Nombre de tu tabla
    "columnas": {
        "id_externo": "id_externo",    # ← Ajustar nombres
        "cliente": "nombre_cliente", 
        "telefono": "telefono_cliente",
        "total": "monto_total",
        # ... etc según tu esquema
    }
}
```

### **Paso 3: Integrar en tu código principal**

#### **Opción A: Agregar al menú**
En tu archivo principal donde creas el menú:

```python
# Al inicio del archivo
from caffe_miga_integration.caffe_miga_integration import agregar_a_tu_menu

# Donde creas tu menú principal
agregar_a_tu_menu(tu_menu_principal, tu_ventana_principal)
```

#### **Opción B: Agregar botón**
En tu ventana principal:

```python
from caffe_miga_integration.caffe_miga_integration import agregar_boton_a_tu_ventana

# En tu función de crear interfaz
integration = agregar_boton_a_tu_ventana(tu_frame_botones, tu_ventana)

# Opcional: iniciar monitoreo automático
integration.iniciar_monitoreo(30)  # Cada 30 segundos
```

## 🔧 **Personalización según tu sistema**

### **Si tu tabla se llama diferente:**
```python
# En config.py, cambiar:
"tabla": "ventas"          # En lugar de "pedidos"
"tabla": "ordenes"         # O como se llame tu tabla
"tabla": "comandas"        # etc.
```

### **Si tus columnas son diferentes:**
```python
# Ejemplo para diferentes nombres de columnas:
"columnas": {
    "id_externo": "id_web",
    "cliente": "nombre_cliente", 
    "telefono": "tel_cliente",
    "total": "precio_total",
    "items": "productos_json",
    "estado": "status_pedido",
    "fecha": "fecha_creacion"
}
```

### **Si usas campos adicionales:**
En `caffe_miga_integration.py`, en la función `insertar_pedido_en_mi_bd()`:

```python
# Agregar más campos según tu sistema
cursor.execute('''
    INSERT INTO tu_tabla (
        id_externo, cliente, telefono, total, items, estado, fecha,
        origen, metodo_pago, email, observaciones  -- ← Campos extra
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    pedido['id'],
    customer.get('name', 'Cliente Web'),
    customer.get('phone', ''),
    pedido.get('total', 0),
    json.dumps(items),
    'nuevo',
    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'ecommerce',  # ← origen
    customer.get('payment_method', 'tarjeta'),  # ← método de pago
    customer.get('email', ''),  # ← email
    f"Pedido web - {len(items)} items"  # ← observaciones
))
```

## 📊 **Estructura de datos que recibes**

Cada pedido del e-commerce viene con:

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
    },
    {
      "id": "croissant",
      "title": "Croissant de Jamón",
      "quantity": 1,
      "unit_price": 45.00
    }
  ],
  "total": 115.00,
  "currency": "MXN",
  "payment_status": "approved"
}
```

## 🔄 **Cómo funciona el flujo**

1. **Cliente hace pedido** en: http://localhost:8000
2. **Pago se procesa** con Mercado Pago
3. **Pedido se guarda** en Firebase automáticamente
4. **Tu sistema consulta** cada 30 segundos si hay pedidos nuevos
5. **Pedido aparece** en tu sistema automáticamente
6. **Procesas normalmente** como cualquier pedido
7. **Estados se sincronizan** (nuevo → preparando → listo → entregado)

## 🛠 **Ejemplos de personalización**

### **Ejemplo 1: Imprimir ticket automáticamente**
```python
def insertar_pedido_en_mi_bd(self, pedido):
    # ... insertar en BD ...
    
    # Imprimir ticket automáticamente
    self.imprimir_ticket_pedido(pedido)
    
def imprimir_ticket_pedido(self, pedido):
    # Tu código de impresión aquí
    # Puede ser impresora térmica, PDF, etc.
    pass
```

### **Ejemplo 2: Sonido de notificación**
```python
def insertar_pedido_en_mi_bd(self, pedido):
    # ... insertar en BD ...
    
    # Reproducir sonido
    import winsound
    winsound.Beep(1000, 500)  # Frecuencia 1000Hz, 500ms
```

### **Ejemplo 3: Email al equipo**
```python
def insertar_pedido_en_mi_bd(self, pedido):
    # ... insertar en BD ...
    
    # Enviar email
    self.enviar_email_nuevo_pedido(pedido)
    
def enviar_email_nuevo_pedido(self, pedido):
    import smtplib
    # Tu código de email aquí
```

## 🔧 **Troubleshooting**

### **"No se puede conectar al servidor"**
- Verifica que el servidor esté corriendo: `python main.py` en la carpeta principal
- URL correcta: `http://127.0.0.1:3000`

### **"Error insertando en BD"**
- Verifica nombres de tabla y columnas en `config.py`
- Verifica que la base de datos existe
- Ejecuta: `python probar_integracion.py`

### **"No aparecen pedidos"**
- Haz un pedido de prueba en: http://localhost:8000
- Verifica que el pago se complete
- Ejecuta sincronización manual

### **"Pedidos duplicados"**
- El sistema verifica automáticamente pedidos duplicados por `id_externo`
- Si persiste, verifica la lógica en `insertar_pedido_en_mi_bd()`

## 📱 **Interfaz de usuario**

La integración agrega:

- **Menú "🔥 Pedidos Web"** con opciones:
  - Sincronizar ahora
  - Iniciar monitoreo automático
  - Detener monitoreo

- **Notificaciones emergentes** cuando llegan pedidos

- **Log de actividad** para ver qué está pasando

## 🚀 **¿Necesitas ayuda específica?**

Si me dices:

1. **¿Cómo se llama tu archivo de base de datos?** (ej: `ventas.db`, `cafeteria.db`)
2. **¿Cómo se llama tu tabla de pedidos?** (ej: `pedidos`, `ventas`, `ordenes`)
3. **¿Qué columnas tienes?** (ej: `id`, `cliente`, `total`, etc.)
4. **¿Cómo se llama tu archivo principal?** (ej: `main.py`, `cafeteria.py`)

Te creo una integración personalizada exacta para tu sistema.

## 🔥 **Resultado final**

Una vez integrado:

✅ **Pedidos llegan automáticamente** a tu sistema  
✅ **Sin intervención manual**  
✅ **Notificaciones visuales**  
✅ **Estados sincronizados**  
✅ **Compatible con tu sistema actual**  

**¡Ya no más WhatsApp! Los pedidos van directo a tu POS.** 🚀

---

**¿Listo para integrar? ¡Solo dime los datos de tu base de datos!** 🔥
