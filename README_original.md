# 🍰 Caffe & Miga - Backend con Mercado Pago

Backend completo en Python Flask para el sistema de pagos de Caffe & Miga.

## 🚀 Instalación Rápida

### Windows:
```bash
# Ejecutar script de instalación
setup.bat
```

### Linux/Mac:
```bash
# Dar permisos y ejecutar
chmod +x setup.sh
./setup.sh
```

### Manual:
```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu Access Token
```

## 🔑 Configuración

### 1. Obtener Access Token

1. Ve a [developers.mercadopago.com](https://developers.mercadopago.com)
2. Inicia sesión con tu cuenta
3. Ve a "Mis aplicaciones" → Tu aplicación
4. Copia el **Access Token** (se ve así: `APP_USR-xxxxx-xxxxx-xxxxx`)

### 2. Configurar .env

Edita el archivo `.env`:
```env
PROD_ACCESS_TOKEN=APP_USR-tu-access-token-real-aqui
PORT=3000
DEBUG=True
```

## ▶️ Ejecutar Servidor

```bash
# Activar entorno virtual si no está activo
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Ejecutar servidor
python main.py
```

El servidor estará disponible en: `http://localhost:3000`

## 📡 Endpoints Disponibles

### `GET /`
Verificar estado del servidor
```json
{
  "status": "ok",
  "message": "Servidor Caffe & Miga funcionando",
  "mercadopago_status": "connected"
}
```

### `POST /create_preference`
Crear preferencia de pago
```json
{
  "items": [
    {
      "title": "2x100 Frappes",
      "quantity": 1,
      "unit_price": 100,
      "currency_id": "GTQ"
    }
  ],
  "payer": {
    "name": "María González",
    "email": "maria@email.com",
    "phone": {
      "area_code": "502",
      "number": "51234567"
    }
  }
}
```

### `POST /webhook`
Recibir notificaciones de Mercado Pago (automático)

### `GET /payment_status/<payment_id>`
Consultar estado de un pago específico

## 🔧 Tu Información de Aplicación

```
User ID: 1016726005
Número de aplicación: 660730758522573
Integración: CheckoutPro
Modelo: Marketplace, BilleteraMercadopago
```

## 🧪 Probar el Sistema

1. **Inicia el backend**: `python main.py`
2. **Abre el frontend**: `http://localhost:8000/index_nuevo.html`
3. **Agrega productos** al carrito
4. **Selecciona "Pagar ahora"**
5. **Completa el pago** con tarjeta de prueba

### 💳 Tarjetas de Prueba

**Tarjeta aprobada:**
- Número: `4035 8887 4000 0016`
- CVV: `123`
- Fecha: `12/25`

**Tarjeta rechazada:**
- Número: `4013 5406 8274 6260`
- CVV: `123`
- Fecha: `12/25`

## 📝 Logs

El servidor muestra logs detallados:
```
✅ Preferencia creada: 1016726005-abc123
💳 Pago 123456789: approved
📦 Creando preferencia para: María González
```

## 🐛 Solución de Problemas

### Error: "SDK no inicializado"
- Verifica que tu `PROD_ACCESS_TOKEN` esté configurado correctamente
- El token debe empezar con `APP_USR-` (producción) o `TEST-` (pruebas)

### Error: "CORS"
- El servidor ya tiene CORS habilitado
- Verifica que el frontend apunte a la URL correcta del backend

### Error: "Preferencia no creada"
- Revisa los logs del servidor
- Verifica que los datos enviados sean válidos
- Confirma que tu aplicación de Mercado Pago esté activa

## 📦 Estructura de Archivos

```
caffe-y-miga/
├── main.py              # Servidor principal
├── requirements.txt     # Dependencias
├── .env.example         # Variables de entorno ejemplo
├── .env                 # Variables de entorno (crear)
├── setup.sh            # Instalación Linux/Mac
├── setup.bat           # Instalación Windows
├── venv/               # Entorno virtual (auto-creado)
├── index_nuevo.html    # Frontend
├── script.js           # JavaScript frontend
├── styles.css          # Estilos
├── success.html        # Página pago exitoso
├── failure.html        # Página pago fallido
└── pending.html        # Página pago pendiente
```

## 🚀 Producción

Para producción, cambia:
1. `DEBUG=False` en `.env`
2. Usa tu dominio real en las URLs
3. Configura HTTPS
4. Usa un servidor como Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:3000 main:app
   ```

## 📞 Soporte

- [Documentación Mercado Pago](https://developers.mercadopago.com)
- [SDKs y librerías](https://developers.mercadopago.com/docs/sdks)
- [Webhook testing](https://developers.mercadopago.com/docs/checkout-pro/additional-content/your-integrations/webhooks)
