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

## ▶️ Ejecutar el Proyecto

### 1. Iniciar Backend
```bash
# Activar entorno virtual si no está activo
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Ejecutar servidor
python main.py
```

El backend estará disponible en: `http://localhost:3000`

### 2. Iniciar Frontend
```bash
# Abrir en navegador o servidor local
# Opción 1: Directo en navegador
start index_nuevo.html

# Opción 2: Servidor HTTP simple
python -m http.server 8000
# Luego ir a: http://localhost:8000/index_nuevo.html
```

## 🌐 Demo en Vivo

**🎯 Visita la demo online:** https://lsvals.github.io/Caffeymiga/

Una vez iniciado el proyecto:
1. **Navega** por el menú de productos
2. **Agrega** items al carrito
3. **Selecciona** método de pago
4. **Completa** la compra con Mercado Pago
5. **Recibe** confirmación por WhatsApp

> **Nota:** La demo online muestra el frontend completo. Para pagos reales, necesitas configurar el backend localmente.

## 🎯 Métodos de Pago Disponibles

### 1. � Pago Online (Mercado Pago)
- Tarjetas de crédito/débito
- Transferencias bancarias
- Billeteras digitales
- Procesamiento inmediato

### 2. 💵 Pago en Efectivo
- Recolección en tienda
- Confirmación por WhatsApp
- Sin comisiones adicionales

### 3. 🏪 Pago en Terminal
- Point de venta en tienda
- Tarjetas chip y contactless
- Comprobante inmediato

## 📡 API Endpoints

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

## 📦 Estructura del Proyecto

```
caffe-y-miga/
├── 🎨 Frontend
│   ├── index_nuevo.html     # Página principal del e-commerce
│   ├── script.js           # Lógica de la aplicación
│   ├── styles.css          # Estilos y diseño responsive
│   ├── success.html        # Página pago exitoso
│   ├── failure.html        # Página pago fallido
│   ├── pending.html        # Página pago pendiente
│   └── img/               # Imágenes y assets
│       ├── C&M_logo.PNG
│       ├── fondo.jpg
│       ├── logo.png
│       ├── Menu.pdf
│       └── promos.jpg
│
├── 🔧 Backend
│   ├── main.py            # Servidor Flask principal
│   ├── requirements.txt   # Dependencias Python
│   └── venv/             # Entorno virtual
│
├── ⚙️ Configuración
│   ├── .env.example      # Variables de entorno ejemplo
│   ├── .env              # Variables de entorno (local)
│   ├── .gitignore        # Archivos ignorados por Git
│   ├── setup.sh         # Instalación Linux/Mac
│   └── setup.bat        # Instalación Windows
│
└── 📚 Documentación
    ├── README.md                    # Este archivo
    ├── GITHUB_README.md            # README específico para GitHub
    ├── MERCADOPAGO-SETUP.md        # Guía configuración MP
    ├── CONFIGURACION-MERCADOPAGO.md # Documentación técnica
    └── DEPLOYMENT_CHECKLIST.md     # Lista verificación deploy
```

## 🚀 Despliegue en Producción

### Preparación
1. **Configura variables de entorno** de producción
2. **Obtén certificado SSL** para tu dominio
3. **Configura webhook URL** en Mercado Pago
4. **Actualiza URLs** en el frontend

### Opciones de Hosting
- **Heroku**: Deploy automático con Git
- **AWS**: EC2 + RDS para escalabilidad
- **DigitalOcean**: VPS simple y económico
- **Vercel/Netlify**: Frontend + Serverless backend

### Comandos de Producción
```bash
# Cambiar a modo producción
echo "DEBUG=False" >> .env

# Usar servidor WSGI
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:3000 main:app
```

## 🛡️ Seguridad Implementada

- ✅ **Variables de entorno** protegidas
- ✅ **Access tokens** fuera del código
- ✅ **CORS** configurado correctamente
- ✅ **Validación** de datos de entrada
- ✅ **HTTPS** recomendado para producción
- ✅ **Webhooks** con verificación de firma

## 🧪 Testing y Desarrollo

## 📞 Soporte y Recursos

### Documentación
- 📖 [Documentación Mercado Pago](https://developers.mercadopago.com)
- 🔧 [SDKs y librerías](https://developers.mercadopago.com/docs/sdks)
- 🪝 [Testing de Webhooks](https://developers.mercadopago.com/docs/checkout-pro/additional-content/your-integrations/webhooks)

### Comunidad
- 💬 [Stack Overflow - Mercado Pago](https://stackoverflow.com/questions/tagged/mercado-pago)
- 🐛 [Reportar Issues](https://github.com/lsVals/Caffeymiga/issues)
- 📧 Contacto: [tu-email@dominio.com]

### Tecnologías Utilizadas
- ![Python](https://img.shields.io/badge/Python-3.8+-blue)
- ![Flask](https://img.shields.io/badge/Flask-2.0+-green)
- ![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow)
- ![HTML5](https://img.shields.io/badge/HTML5-orange)
- ![CSS3](https://img.shields.io/badge/CSS3-blue)
- ![Mercado Pago](https://img.shields.io/badge/Mercado%20Pago-SDK-blue)

---

<div align="center">
  <b>🍰 Desarrollado con ❤️ para Caffe & Miga</b><br>
  <i>Sistema completo de e-commerce con pagos integrados</i>
</div>
