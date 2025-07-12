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
Agregar estas variables en la configuración:
```
ENVIRONMENT=production
PORT=10000
DEBUG=False
USE_TEST_MODE=False
PROD_ACCESS_TOKEN=APP_USR-660730758522573-071123-fe57a6e4b6158e37e5bc7b40d4097de0-1016726005
```

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
