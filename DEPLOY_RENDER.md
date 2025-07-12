# 🚀 GUÍA DE DESPLIEGUE EN RENDER

## Pasos para desplegar tu página en línea:

### 1. 📝 Preparar repositorio
```bash
git add .
git commit -m "Preparar para despliegue en Render"
git push origin main
```

### 2. 🌐 Crear cuenta en Render
1. Ve a [render.com](https://render.com)
2. Crea cuenta gratis con GitHub
3. Conecta tu repositorio `caffeymiga`

### 3. ⚙️ Configurar Web Service
- **Repository**: lsVals/caffeymiga
- **Branch**: main
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements_render.txt`
- **Start Command**: `python main.py`

### 4. 🔐 Variables de entorno en Render
Agregar estas variables en la configuración del Web Service:

**Variables principales:**
```
ENVIRONMENT = production
PORT = 10000
DEBUG = False
USE_TEST_MODE = False
PROD_ACCESS_TOKEN = APP_USR-660730758522573-071123-fe57a6e4b6158e37e5bc7b40d4097de0-1016726005
```

**Variables de Firebase:**
```
FIREBASE_PRIVATE_KEY_ID = 171d1d626b0e55518e44a2ea4c912d587e03ba31
FIREBASE_PRIVATE_KEY = -----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDCxgOw1ai6zldq
Y/UYva2U5UrkcnTgHoivh3EaAXyKysvPMX9G+T1Bkd75riOmGqrn0TrE78hckrhA
qoE1+wj62KCqsF+QLJrqv8QTpo99CwCezhkPErmM/D8hkaBGo4cyN1NHqvVltYwp
KZ+3HVLCoaEs2SA1Ij9skSv9pEf5CJMQXlvWCxMyhRTe607qECkZtpM9wp2Bp0Kq
Mh3nGebpHSBO+MU713hRekNF2Xplv6+rWPd7+NjzBRU7w6WV6hW8djqrbZJsm8dp
smMCfiX5begI2MXWO85dO0bJP2xZOPrudUJG4SGd+ObKptyLm49pxYhleCUHYg8R
eARfUoVDAgMBAAECggEAAUWhyIncrDukvoEgnKTAeXR15MAKm1wXsG3GA1F3KsDg
S94a4q/GAqOdPSwx92e9Lf5jz91xBYm/wkxaw6t8B4dapUK5nQtth5LxCN/RmBN2
UZMu/rY0mAMdtm5pCY0P2PgbhyBKsftZivtGm7+JRtQfZVeVqkMq/t6D1wg3oBy3
SNS8QIKWpxuQOX1LDObtm2kxlZ2L6oDYTC29ct7pvke/IM/WpH8f+49iO+tQ3OaI
vqaIUBX+teGIdozIGDn2t3HYAyN1XaRRLJNd3l0lQJ3/5br005Q7bJCQIGge6Drb
pqlYSUUj1H8KDG2T8l6Lb14J9vBjN5qXzheoqki7wQKBgQD8kotX4XnNFkd7d8es
NQDGms5RaiGTVaHqocmIpBtayNKmoqok6r2uQNHhBtbWIAtWxVP1Hw7DBZ205E/N
Q/wVJeqHQ2D0LddR8CtDaD0Alis6Y7uH83OL7NUhb1etF1ryITQTbukHQ8653YGa
X4Zb8XMB48ZLZFXD6zB3f9M2yQKBgQDFaqwWWb87hpQhJaIdzjHFlShCifsKJGNe
mSI5+wCSlwakZ4rEARccMog1NINewnnxT7kRi2JuhmEwcQaZgvEG7Fdj3Zl5sv6W
b6JfKmVDb6ukPIdgQdmafF6OCs3W+Qkrx9+4C8BquCZCxxat3ggowZvln2P/7CIu
B39SSlMFqwKBgEZy+bsBgV/bHwUpW+CEyDqdY38CA2t9LzSq+/PJEng4G8mvBZZW
g6HfIquJpNMFDSSe1dRBXXS4VEzogfnXRLEBanFgMeLqBm0seGTM5ncLa/NVbjF1
jn0xCiHRVLtLEGsJJ+VjwkvsdfUR+9x7WJa8uj+EsQLGccW8DEDIvrlBAoGBAIze
so98WR4zyQ3iGc2k7hUsez8H0LALCTFemnK/LkhsJlw4WmfE02XWlSVKJJgAtB1C
oy/mw0VU9JMpg+kU68Lh8PYdEcAqvspAPKAl036Md/FJE9zXAFzhdGNtSDanHCk2
heiB0jsUzpCGGiPVNQNILGNtGmFrcXRg+zSQPq/jAoGBAJ3qFhrUAh4TJJ0EsKBa
tNDFhI361DsdTe1h+Dxo+EwZ2DwJv6HZ1RRYvK2jE60/fmEHSQ2lz3V/D0QooP9S
1cNqcXjVXC1rbdhtLOCtDzp1TSxTY9P3s1QGu0O5ilWiQRNnrE1DklBbLVP2Cfnv
+sS3YflxqN77lB96SbJK8odl
-----END PRIVATE KEY-----
```

⚠️ **IMPORTANTE**: Para FIREBASE_PRIVATE_KEY, copia el contenido completo incluyendo los guiones y saltos de línea.

### 5. 🎯 URL final
Una vez desplegado, tendrás:
- **Backend**: `https://caffeymiga.onrender.com`
- **Frontend**: `https://lsvals.github.io/caffeymiga/`

### 6. ✅ Resultado
- ✅ Pedidos desde móvil van directo al POS
- ✅ Pagos con Mercado Pago funcionan
- ✅ Sistema completo en línea
- ✅ No más dependencia de servidor local

## 📱 URLs para probar:
- **Desde cualquier móvil**: `https://lsvals.github.io/caffeymiga/`
- **Servidor backend**: `https://caffeymiga.onrender.com/health`

## 🔧 Debugging:
- Los logs del servidor se ven en el dashboard de Render
- Todos los pedidos se guardan en Firebase
- El POS local sigue funcionando con sincronización
