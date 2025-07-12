# 🛒 Configuración de Métodos de Pago - Caffe & Miga

## ✅ Sistema Implementado

El sistema ahora incluye dos métodos de pago:

### 💵 Efectivo en Sucursal
- El cliente selecciona esta opción
- Paga cuando recoge el pedido
- No requiere configuración adicional

### 💳 Tarjeta con Terminal Mercado Pago
- El cliente selecciona esta opción
- Puede pagar con terminal en la sucursal
- Opcionalmente puede incluir link de pago previo

## 🔧 Configuración Opcional de Links de Mercado Pago

### Opción 1: Link Fijo de Pago
Si tienes un link fijo de Mercado Pago, edita el archivo `script.js` línea aproximada 1300:

```javascript
const MERCADO_PAGO_CONFIG = {
    linkPago: "https://mpago.la/TU_LINK_AQUI", // Cambia por tu link
    usarLinkDinamico: false,
    linkBase: ""
};
```

### Opción 2: Sin Link de Pago (Solo Terminal)
Para usar únicamente el terminal en sucursal, deja la configuración así:

```javascript
const MERCADO_PAGO_CONFIG = {
    linkPago: "", // Vacío = solo terminal en sucursal
    usarLinkDinamico: false,
    linkBase: ""
};
```

### Opción 3: Links Dinámicos (Avanzado)
Si Mercado Pago te permite generar links con montos dinámicos:

```javascript
const MERCADO_PAGO_CONFIG = {
    linkPago: "",
    usarLinkDinamico: true,
    linkBase: "https://mpago.la/tu_link_base"
};
```

## 📱 Cómo Funciona

1. **Cliente hace pedido** → Selecciona productos
2. **Hacer Pedido** → Abre formulario
3. **Selecciona método de pago**:
   - 💵 Efectivo: Pagará en sucursal
   - 💳 Tarjeta: Usará terminal (o link si está configurado)
4. **Envía por WhatsApp** → Mensaje incluye método de pago seleccionado

## 📋 Mensaje de WhatsApp Incluye:

```
¡Hola! Soy Juan Pérez
Mi teléfono: 50251234567
Hora de recogida: 2:00 PM - 3:00 PM
💳 Método de pago: Tarjeta con terminal Mercado Pago

Mi pedido:
• 2x100 Frappes - Cualquier Sabor (Moka + Capuchino) (1) - $100

💰 Total: $100

📝 Nota: Pago con tarjeta usando terminal Mercado Pago en sucursal
💳 Link de pago: https://mpago.la/1234567
(También puedes pagar directamente en sucursal con terminal)
```

## 🎯 Ventajas del Sistema

✅ **Flexibilidad**: Cliente elige cómo pagar
✅ **Claridad**: Método de pago aparece en WhatsApp
✅ **Terminal disponible**: Siempre funciona el terminal en sucursal
✅ **Links opcionales**: Puedes agregar links si los tienes
✅ **Fácil configuración**: Solo editar una variable

## 📞 Soporte

Si necesitas ayuda para configurar tu link de Mercado Pago, contacta a tu asesor de Mercado Pago o revisa su documentación oficial.
