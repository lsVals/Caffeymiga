# Instrucciones para configurar Firebase

## 🔥 PASO 1: Crear proyecto en Firebase

1. Ve a https://console.firebase.google.com/
2. Haz clic en "Agregar proyecto"
3. Nombre del proyecto: `caffeymigapedidos` ✅ (Ya tienes este proyecto)
4. Habilita Google Analytics (opcional)
5. Selecciona tu cuenta de Analytics
6. Crea el proyecto

## 🔥 PASO 2: Configurar Firestore Database

1. En el proyecto de Firebase, ve a "Firestore Database"
2. Haz clic en "Crear base de datos"
3. Selecciona "Comenzar en modo de prueba"
4. Elige una ubicación (recomendado: us-central)
5. Crea la base de datos

## 🔥 PASO 3: Obtener credenciales

### Opción A: Credenciales de servicio (Recomendado para producción)
1. Ve a "Configuración del proyecto" (ícono de engranaje)
2. Pestaña "Cuentas de servicio"
3. Haz clic en "Generar nueva clave privada"
4. Descarga el archivo JSON
5. Renómbralo a `firebase-credentials.json`
6. Colócalo en la carpeta del proyecto

### Opción B: Para desarrollo local (Modo de prueba)
1. Instala Firebase CLI: `npm install -g firebase-tools`
2. Ejecuta: `firebase login`
3. Ejecuta: `firebase init firestore`
4. Las credenciales se configurarán automáticamente

## 🔥 PASO 4: Configurar reglas de Firestore

Ve a Firestore Database > Reglas y usa estas reglas para desarrollo:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Permitir lectura/escritura para la colección orders
    match /orders/{document} {
      allow read, write: if true;
    }
    
    // Para producción, usa reglas más estrictas:
    // match /orders/{document} {
    //   allow read, write: if request.auth != null;
    // }
  }
}
```

## 🔥 PASO 5: Variables de entorno

Agrega estas variables a tu archivo `.env`:

```env
# Firebase Configuration
FIREBASE_PROJECT_ID=caffeymigapedidos
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json

# Opcional: Para usar credenciales por defecto
GOOGLE_APPLICATION_CREDENTIALS=firebase-credentials.json
```

## 🔥 PASO 6: Estructura de datos esperada

Los pedidos se guardarán con esta estructura:

```json
{
  "orders": {
    "order_id": {
      "preference_id": "123456789",
      "external_reference": "caffeymiga_1234567890",
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
      "status": "nuevo",
      "pos_status": "listo_para_preparar",
      "payment_status": "pending",
      "created_at": "2024-01-01T10:00:00Z",
      "source": "web_ecommerce"
    }
  }
}
```

## 🔥 PASO 7: Estados del POS

- `listo_para_preparar`: Nuevo pedido pagado
- `preparando`: En preparación
- `listo`: Listo para entregar
- `entregado`: Entregado al cliente
- `cancelado`: Cancelado

## 🔥 PASO 8: Testing

1. Inicia el servidor: `python main.py`
2. Abre el POS Dashboard: `http://localhost:5000/pos-dashboard.html`
3. Haz un pedido desde: `http://localhost:8000`
4. Verifica que aparezca en el POS

## 🔥 Endpoints disponibles para tu POS:

- `GET /pos/orders` - Obtener pedidos pendientes
- `PUT /pos/orders/{id}/status` - Actualizar estado
- `GET /pos/dashboard` - Dashboard con estadísticas

¡Firebase está listo para conectar tu e-commerce con tu sistema POS! 🚀
