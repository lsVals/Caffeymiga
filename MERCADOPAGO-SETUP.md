# 🛒 Configuración SDK Mercado Pago - Caffe & Miga ✅ BACKEND LISTO

## ✅ Sistema Completamente Implementado

Ahora tienes 3 métodos de pago totalmente funcionales:

### 💵 Efectivo en Sucursal
- Pago tradicional al recoger
- Sin configuración adicional

### 💳 Pago en Línea (Con SDK + Backend) ⭐ LISTO
- Pago inmediato con tarjeta
- Checkout completo de Mercado Pago  
- Confirmación automática por WhatsApp
- **COMPLETAMENTE FUNCIONAL**

### 🏪 Terminal en Sucursal
- Pago con terminal físico al recoger
- Backup confiable

## 🔧 Configuración Final (Solo 2 pasos)

### 1. Public Key en Frontend
Edita `script.js` línea 2:
```javascript
publicKey: "TU_PUBLIC_KEY_AQUI" // ← Solo cambiar esto
```

### 2. URL del Backend (si es diferente)
```javascript
backendUrl: "http://localhost:3000" // ← Tu URL del backend
```

## ✅ Ya Incluido en el Sistema:

- ✅ Páginas de resultado (success.html, failure.html, pending.html)
- ✅ Manejo completo de errores  
- ✅ Confirmación automática por WhatsApp
- ✅ Interfaz responsive y profesional
- ✅ Fallback a WhatsApp si algo falla

¡Tu sistema está 100% listo para recibir pagos! 🚀

## ✅ Sistema Implementado

Ahora tienes 3 métodos de pago disponibles:

### 💵 Efectivo en Sucursal
- Pago tradicional al recoger
- Sin configuración adicional

### 💳 Pago en Línea (Con SDK)
- Pago inmediato con tarjeta
- Confirmación automática por WhatsApp
- **Requiere configuración del SDK**

### 🏪 Terminal en Sucursal
- Pago con terminal físico al recoger
- Backup si el pago en línea falla

## 🔧 Configuración Requerida

### 1. Public Key de Mercado Pago

Edita el archivo `script.js` línea aproximada 2:

```javascript
const MERCADO_PAGO_CONFIG = {
    // Reemplaza con tu Public Key real
    publicKey: "APP_USR-12345678-123456-123456789abcdef-123456789", // Tu Public Key aquí
    
    // Para pruebas usa: "TEST-12345678-123456-123456789abcdef-123456789"
    // Para producción usa: "APP_USR-12345678-123456-123456789abcdef-123456789"
};
```

### 2. Backend para Crear Preferencias

Necesitas un servidor que cree las preferencias de pago. Ejemplo en Node.js:

```javascript
// server.js
const express = require('express');
const mercadopago = require('mercadopago');

mercadopago.configurations.setAccessToken('TU_ACCESS_TOKEN_AQUI');

app.post('/create_preference', (req, res) => {
    const preference = {
        items: req.body.items,
        payer: req.body.payer,
        back_urls: {
            success: "https://tudominio.com/success",
            failure: "https://tudominio.com/failure",
            pending: "https://tudominio.com/pending"
        },
        auto_return: "approved"
    };
    
    mercadopago.preferences.create(preference)
        .then(response => res.json(response.body))
        .catch(error => res.status(400).json(error));
});
```

### 3. Páginas de Resultado

Crea estas páginas en tu servidor:

- `success.html` - Pago exitoso
- `failure.html` - Pago fallido  
- `pending.html` - Pago pendiente

## 🎯 Pasos para Configurar

### Paso 1: Obtener Credenciales
1. Ve a [developers.mercadopago.com](https://developers.mercadopago.com)
2. Inicia sesión con tu cuenta
3. Ve a "Mis aplicaciones"
4. Copia tu **Public Key** y **Access Token**

### Paso 2: Configurar Public Key
```javascript
// En script.js línea 2
publicKey: "TU_PUBLIC_KEY_REAL_AQUI"
```

### Paso 3: Configurar Backend
- Instala SDK de Mercado Pago en tu servidor
- Configura endpoint `/create_preference`
- Usa tu **Access Token** en el servidor

### Paso 4: Actualizar URLs
```javascript
// En script.js función crearPreferenciaPago
const preferenceData = {
    // ...
    back_urls: {
        success: "https://tudominio.com/success.html",
        failure: "https://tudominio.com/failure.html", 
        pending: "https://tudominio.com/pending.html"
    }
};
```

## 📱 Flujo de Pago Completo

1. **Cliente hace pedido** → Agrega productos
2. **Selecciona "Pagar ahora con tarjeta"** → Abre checkout
3. **Completa datos de pago** → Mercado Pago procesa
4. **Pago exitoso** → Confirmación automática por WhatsApp
5. **Pedido confirmado** → Listo para preparar

## 🔄 Flujo Actual (Temporal)

Mientras configuras el backend:

1. **Cliente selecciona pago en línea** → Abre modal informativo
2. **Ve información de configuración** → Instrucciones técnicas
3. **Puede simular pago exitoso** → Para pruebas
4. **O enviar por WhatsApp** → Método alternativo

## 🚀 Producción vs Desarrollo

### Desarrollo (TEST)
```javascript
publicKey: "TEST-12345678-123456-123456789abcdef-123456789"
```

### Producción (LIVE)
```javascript
publicKey: "APP_USR-12345678-123456-123456789abcdef-123456789"
```

## 💡 Recomendaciones

1. **Empieza con TEST** para hacer pruebas
2. **Configura webhooks** para confirmaciones automáticas
3. **Mantén backup** con terminal físico
4. **Monitorea pagos** desde panel de Mercado Pago

## 📞 Soporte

- [Documentación oficial](https://developers.mercadopago.com)
- [SDKs y librerías](https://developers.mercadopago.com/docs/sdks)
- [Centro de ayuda](https://www.mercadopago.com.ar/ayuda)
