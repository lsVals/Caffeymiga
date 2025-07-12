// Datos de productos por categoría
const productosData = {
    promociones: [
        { 
            nombre: "2x100 Frappes - Cualquier Sabor", 
            precio: 100, 
            imagen: "img/promos.jpg", 
            descripcion: "Martes y Viernes únicamente. Elige 2 frappes de cualquier sabor: Moka, Capuchino, Taro, Caramelo u Oreo",
            tieneOpciones: true,
            tieneLeche: true,
            saboresDisponibles: ["Moka", "Capuchino", "Taro", "Caramelo", "Oreo"],
            lechesDisponibles: ["Entera", "Deslactosada", "Deslactosada Light"]
        }
    ],
    frappe: [
        { nombre: "Frappé Moka", precio: 70, imagen: "img/frappe-moka.jpg", tieneLeche: true, lechesDisponibles: ["Entera", "Deslactosada", "Deslactosada Light"] },
        { nombre: "Frappé Capuchino", precio: 70, imagen: "img/frappe-capuchino.jpg", tieneLeche: true, lechesDisponibles: ["Entera", "Deslactosada", "Deslactosada Light"] },
        { nombre: "Frappé Taro", precio: 75, imagen: "img/frappe-taro.jpg", tieneLeche: true, lechesDisponibles: ["Entera", "Deslactosada", "Deslactosada Light"] },
        { nombre: "Frappé Caramelo", precio: 75, imagen: "img/frappe-caramelo.jpg", tieneLeche: true, lechesDisponibles: ["Entera", "Deslactosada", "Deslactosada Light"] },
        { nombre: "Frappé Oreo", precio: 80, imagen: "img/frappe-oreo.jpg", tieneLeche: true, lechesDisponibles: ["Entera", "Deslactosada", "Deslactosada Light"] }
    ],
    bebidas: [
        { nombre: "Agua 500ml", precio: 8, imagen: "img/agua-500ml.jpg" },
        { nombre: "Agua 1L", precio: 12, imagen: "img/agua-1l.jpg" },
        { nombre: "Coca Cola 355ml", precio: 17, imagen: "img/coca-355ml.jpg" },
        { nombre: "Coca Cola 600ml", precio: 25, imagen: "img/coca-600ml.jpg" },
        { nombre: "Coca Cola Zero 355ml", precio: 17, imagen: "img/coca-zero-355ml.jpg" },
        { nombre: "Coca Cola Zero 600ml", precio: 25, imagen: "img/coca-zero-600ml.jpg" }
    ],
    "bebidas-frias": [
        { nombre: "Latte Matcha", precio: 65, imagen: "img/latte-matcha.jpg", tieneLeche: true, lechesDisponibles: ["Entera", "Deslactosada", "Deslactosada Light"] },
        { nombre: "Cold Brew", precio: 60, imagen: "img/cold-brew.jpg", tieneLeche: true, lechesDisponibles: ["Entera", "Deslactosada", "Deslactosada Light"] },
        { nombre: "Chai", precio: 65, imagen: "img/chai.jpg", tieneLeche: true, lechesDisponibles: ["Entera", "Deslactosada", "Deslactosada Light"] },
        { nombre: "Caramel Macchiato", precio: 65, imagen: "img/caramel-macchiato.jpg", tieneLeche: true, lechesDisponibles: ["Entera", "Deslactosada", "Deslactosada Light"] },
        { nombre: "Latte", precio: 60, imagen: "img/latte.jpg", tieneLeche: true, lechesDisponibles: ["Entera", "Deslactosada", "Deslactosada Light"] }
    ],
    "cafe-caliente": [
        { nombre: "Capuchino", precio: 55, imagen: "img/capuchino.jpg", tieneLeche: true, lechesDisponibles: ["Entera", "Deslactosada", "Deslactosada Light"] },
        { nombre: "Moka", precio: 60, imagen: "img/moka.jpg", tieneLeche: true, lechesDisponibles: ["Entera", "Deslactosada", "Deslactosada Light"] },
        { nombre: "Americano", precio: 40, imagen: "img/americano.jpg", tieneLeche: true, lechesDisponibles: ["Sin leche", "Entera", "Deslactosada", "Deslactosada Light"] },
        { nombre: "Latte", precio: 55, imagen: "img/latte-caliente.jpg", tieneLeche: true, lechesDisponibles: ["Entera", "Deslactosada", "Deslactosada Light"] }
    ],
    postres: [
        { nombre: "Waffles", precio: 65, imagen: "img/waffles.jpg" },
        { nombre: "Budín", precio: 30, imagen: "img/budin.jpg" },
        { nombre: "Flan Napolitano", precio: 35, imagen: "img/flan-napolitano.jpg" }
    ],
    pan: [
        { nombre: "Carterita", precio: 12, imagen: "img/carterita.jpg" },
        { nombre: "Concha", precio: 12, imagen: "img/concha.jpg" },
        { nombre: "Bisquet", precio: 18, imagen: "img/bisquet.jpg" },
        { nombre: "Roll de Canela", precio: 30, imagen: "img/roll-canela.jpg" },
        { nombre: "Keke", precio: 12, imagen: "img/keke.jpg" }
    ],
    comida: [
        { nombre: "Sandwich", precio: 65, imagen: "img/sandwich.jpg" }
    ]
};

// Variables globales
let carrito = [];
let categoriaActual = 'promociones';
let carritoColapsado = false;

// Configuración de Mercado Pago
const MERCADO_PAGO_CONFIG = {
    // IMPORTANTE: Public Key de PRODUCCIÓN
    publicKey: "APP_USR-e440d8d5-6f4e-464e-bff1-89b92613fd19", // 🔑 PUBLIC KEY DE PRODUCCIÓN
    
    // URL de tu backend (ajusta según tu configuración)
    backendUrl: "http://localhost:3000", // Cambia por la URL de tu backend
    
    // Endpoints de tu backend
    endpoints: {
        createPreference: "/create_preference",
        webhook: "/webhook"
    },
    
    // URLs de retorno (ajusta según tu dominio)
    redirectUrls: {
        success: window.location.origin + "/success.html",
        failure: window.location.origin + "/failure.html", 
        pending: window.location.origin + "/pending.html"
    }
};

// Inicializar Mercado Pago
let mp = null;
if (typeof MercadoPago !== 'undefined') {
    try {
        mp = new MercadoPago(MERCADO_PAGO_CONFIG.publicKey);
        console.log('✅ Mercado Pago inicializado correctamente');
    } catch (error) {
        console.error('❌ Error al inicializar Mercado Pago:', error);
    }
}

// Función para generar link de Mercado Pago (si está configurado)
function generarLinkMercadoPago(total) {
    if (MERCADO_PAGO_CONFIG.linkPago) {
        return MERCADO_PAGO_CONFIG.linkPago;
    }
    
    if (MERCADO_PAGO_CONFIG.usarLinkDinamico && MERCADO_PAGO_CONFIG.linkBase) {
        // Aquí podrías implementar lógica para links dinámicos
        return `${MERCADO_PAGO_CONFIG.linkBase}?amount=${total}`;
    }
    
    return null;
}

// Inicializar la aplicación
document.addEventListener('DOMContentLoaded', function() {
    inicializarMenu();
    mostrarProductos('promociones');
    configurarCarrito();
    inicializarCarritoFlotante();
    configurarHorarios();
    mostrarBannerCerrado();
    actualizarHorariosHeader(); // Nueva línea para actualizar horarios en el header
});

// Configurar el menú de navegación
function inicializarMenu() {
    const menuItems = document.querySelectorAll('.menu-item');
    
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            const categoria = this.getAttribute('data-categoria');
            
            // Remover clase activa de todos los items
            menuItems.forEach(i => i.classList.remove('activo'));
            
            // Agregar clase activa al item seleccionado
            this.classList.add('activo');
            
            // Mostrar productos de la categoría
            mostrarProductos(categoria);
            categoriaActual = categoria;
        });
    });
    
    // Activar el primer item por defecto
    menuItems[0].classList.add('activo');
}

// Mostrar productos de una categoría
function mostrarProductos(categoria) {
    const contenedorProductos = document.querySelector('.productos');
    const productos = productosData[categoria] || [];
    
    contenedorProductos.innerHTML = '';
    
    // Si es la categoría promociones, usar diseño especial
    if (categoria === 'promociones') {
        productos.forEach((producto, index) => {
            const promoDiv = document.createElement('div');
            promoDiv.className = 'promocion-banner';
            
            promoDiv.innerHTML = `
                <div class="promocion-contenido">
                    <div class="promocion-imagen">
                        <img src="${producto.imagen}" alt="${producto.nombre}" onerror="this.src='img/placeholder.jpg'">
                    </div>
                    <div class="promocion-info">
                        <div class="promocion-etiqueta">¡PROMOCIÓN ESPECIAL!</div>
                        <h2 class="promocion-titulo">${producto.nombre}</h2>
                        <p class="promocion-descripcion">${producto.descripcion}</p>
                        <div class="promocion-precio-container">
                            <span class="promocion-precio">$${producto.precio}</span>
                            <div class="contador">
                                <button onclick="cambiarCantidad('${categoria}', ${index}, -1)">-</button>
                                <span id="cantidad-${categoria}-${index}">0</span>
                                <button onclick="cambiarCantidad('${categoria}', ${index}, 1)">+</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            contenedorProductos.appendChild(promoDiv);
        });
    } else {
        // Diseño normal para otras categorías
        productos.forEach((producto, index) => {
            const productoDiv = document.createElement('div');
            productoDiv.className = 'producto';
            
            const descripcionHTML = producto.descripcion ? 
                `<p class="descripcion-promocion">${producto.descripcion}</p>` : '';
            
            productoDiv.innerHTML = `
                <img src="${producto.imagen}" alt="${producto.nombre}" onerror="this.src='img/placeholder.jpg'">
                <h3>${producto.nombre}</h3>
                ${descripcionHTML}
                <p class="precio">$${producto.precio}</p>
                <div class="contador">
                    <button onclick="cambiarCantidad('${categoria}', ${index}, -1)">-</button>
                    <span id="cantidad-${categoria}-${index}">0</span>
                    <button onclick="cambiarCantidad('${categoria}', ${index}, 1)">+</button>
                </div>
            `;
            contenedorProductos.appendChild(productoDiv);
        });
    }
}

// Cambiar cantidad de un producto
function cambiarCantidad(categoria, index, cambio) {
    const producto = productosData[categoria][index];
    
    // Si es una promoción con opciones de sabores y se está agregando
    if (producto.tieneOpciones && cambio > 0) {
        abrirSelectorSabores(categoria, index);
        return;
    }
    
    // Si tiene opción de leche y se está agregando
    if (producto.tieneLeche && !producto.tieneOpciones && cambio > 0) {
        abrirSelectorLeche(categoria, index);
        return;
    }
    
    // Si es una promoción con opciones y se está reduciendo, reducir el último agregado
    if ((producto.tieneOpciones || producto.tieneLeche) && cambio < 0) {
        const productosPersonalizados = carrito.filter(item => 
            item.categoria === categoria && item.index === index && 
            (item.saboresElegidos || item.lecheElegida)
        );
        
        if (productosPersonalizados.length > 0) {
            const ultimoProducto = productosPersonalizados[productosPersonalizados.length - 1];
            const indexEnCarrito = carrito.findIndex(item => 
                item === ultimoProducto
            );
            
            if (indexEnCarrito > -1) {
                if (ultimoProducto.cantidad > 1) {
                    ultimoProducto.cantidad--;
                } else {
                    carrito.splice(indexEnCarrito, 1);
                }
                
                // Actualizar contador visual
                const spanCantidad = document.getElementById(`cantidad-${categoria}-${index}`);
                const totalActual = carrito.filter(item => 
                    item.categoria === categoria && item.index === index
                ).reduce((sum, item) => sum + item.cantidad, 0);
                spanCantidad.textContent = totalActual;
                
                mostrarCarrito();
                return;
            }
        }
    }
    
    const spanCantidad = document.getElementById(`cantidad-${categoria}-${index}`);
    let cantidadActual = parseInt(spanCantidad.textContent);
    let nuevaCantidad = Math.max(0, cantidadActual + cambio);
    
    spanCantidad.textContent = nuevaCantidad;
    
    const productoCarrito = {
        ...producto,
        categoria: categoria,
        index: index,
        cantidad: nuevaCantidad
    };
    
    actualizarCarrito(productoCarrito);
}

// Actualizar carrito
function actualizarCarrito(producto) {
    // Para productos con sabores o leche, cada combinación es un item único
    let index = -1;
    if (producto.saboresElegidos && producto.lechesElegidas) {
        // Productos con sabores y leches individuales (promociones)
        index = carrito.findIndex(item => 
            item.categoria === producto.categoria && 
            item.index === producto.index &&
            JSON.stringify(item.saboresElegidos) === JSON.stringify(producto.saboresElegidos) &&
            JSON.stringify(item.lechesElegidas) === JSON.stringify(producto.lechesElegidas)
        );
    } else if (producto.saboresElegidos && producto.lecheElegida) {
        // Productos con sabores y leche única (legacy)
        index = carrito.findIndex(item => 
            item.categoria === producto.categoria && 
            item.index === producto.index &&
            JSON.stringify(item.saboresElegidos) === JSON.stringify(producto.saboresElegidos) &&
            item.lecheElegida === producto.lecheElegida
        );
    } else if (producto.saboresElegidos) {
        // Productos solo con sabores
        index = carrito.findIndex(item => 
            item.categoria === producto.categoria && 
            item.index === producto.index &&
            JSON.stringify(item.saboresElegidos) === JSON.stringify(producto.saboresElegidos) &&
            !item.lecheElegida && !item.lechesElegidas
        );
    } else if (producto.lecheElegida) {
        // Productos solo con leche
        index = carrito.findIndex(item => 
            item.categoria === producto.categoria && 
            item.index === producto.index &&
            item.lecheElegida === producto.lecheElegida &&
            !item.saboresElegidos
        );
    } else {
        // Productos sin opciones
        index = carrito.findIndex(item => 
            item.categoria === producto.categoria && 
            item.index === producto.index &&
            !item.saboresElegidos &&
            !item.lecheElegida &&
            !item.lechesElegidas
        );
    }
    
    if (producto.cantidad === 0) {
        if (index > -1) {
            carrito.splice(index, 1);
        }
    } else {
        if (index > -1) {
            carrito[index] = producto;
        } else {
            carrito.push(producto);
        }
    }
    
    mostrarCarrito();
}

// Mostrar carrito
function mostrarCarrito() {
    const listaCarrito = document.getElementById('lista-carrito');
    const contadorCarrito = document.getElementById('carrito-contador');
    const totalCarrito = document.getElementById('carrito-total');
    const btnPedido = document.getElementById('enviar-pedido');
    
    listaCarrito.innerHTML = '';
    
    let total = 0;
    let totalItems = 0;
    
    if (carrito.length === 0) {
        listaCarrito.innerHTML = '<div class="carrito-vacio">Tu carrito está vacío</div>';
        btnPedido.disabled = true;
        btnPedido.textContent = 'Carrito Vacío';
    } else {
        carrito.forEach((item, index) => {
            const li = document.createElement('li');
            const subtotal = item.precio * item.cantidad;
            total += subtotal;
            totalItems += item.cantidad;
            
            const nombreMostrar = item.nombrePersonalizado || item.nombre;
            const saboresInfo = item.saboresElegidos ? 
                `<div class="item-sabores">${item.saboresElegidos.map(sabor => getSaborEmoji(sabor) + ' ' + sabor).join(', ')}</div>` : '';
            
            // Mostrar información de leches (individuales para promociones o única para otros productos)
            let lecheInfo = '';
            if (item.lechesElegidas && item.lechesElegidas.length > 0) {
                // Promociones con leches individuales
                const lechesTexto = item.lechesElegidas.map((leche, index) => {
                    if (leche !== 'Entera') {
                        const saborCorrespondiente = item.saboresElegidos ? item.saboresElegidos[index] : `Frappe ${index + 1}`;
                        return `${saborCorrespondiente}: 🥛 ${leche}`;
                    }
                    return null;
                }).filter(Boolean);
                
                if (lechesTexto.length > 0) {
                    lecheInfo = `<div class="item-leches">${lechesTexto.join('<br>')}</div>`;
                }
            } else if (item.lecheElegida && item.lecheElegida !== 'Entera' && item.lecheElegida !== 'Sin leche') {
                // Productos individuales con leche única (solo mostrar si no es entera ni sin leche)
                lecheInfo = `<div class="item-leche">🥛 ${item.lecheElegida}</div>`;
            }
            
            li.innerHTML = `
                <div class="item-info">
                    <div class="item-nombre">${nombreMostrar}</div>
                    ${saboresInfo}
                    ${lecheInfo}
                    <small class="item-precio-unitario">$${item.precio} c/u</small>
                </div>
                <div class="item-controles">
                    <div class="item-cantidad-controles">
                        <button class="btn-cantidad" onclick="ajustarCantidadCarrito(${index}, -1)">-</button>
                        <span class="item-cantidad">${item.cantidad}</span>
                        <button class="btn-cantidad" onclick="ajustarCantidadCarrito(${index}, 1)">+</button>
                    </div>
                    <div class="item-subtotal">$${subtotal}</div>
                    <button class="btn-eliminar" onclick="eliminarDelCarrito(${index})" title="Eliminar producto">🗑️</button>
                </div>
            `;
            listaCarrito.appendChild(li);
        });
        
        // Agregar total
        const totalLi = document.createElement('li');
        totalLi.className = 'carrito-total-item';
        totalLi.innerHTML = `
            <div class="item-info">
                <strong>TOTAL</strong>
            </div>
            <div class="item-controles">
                <div class="item-subtotal">
                    <strong>$${total}</strong>
                </div>
            </div>
        `;
        listaCarrito.appendChild(totalLi);
        
        btnPedido.disabled = false;
        btnPedido.textContent = 'Hacer Pedido';
    }
    
    // Actualizar contador y total en el header
    contadorCarrito.textContent = totalItems === 1 ? '1 producto' : `${totalItems} productos`;
    totalCarrito.textContent = `$${total}`;
    
    // Animar el carrito cuando se agregue un item
    if (totalItems > 0) {
        const carritoFlotante = document.getElementById('carrito-flotante');
        carritoFlotante.style.transform = 'scale(1.05)';
        setTimeout(() => {
            carritoFlotante.style.transform = 'scale(1)';
        }, 200);
    }
}

// Configurar carrito y formulario
function configurarCarrito() {
    const botonEnviar = document.getElementById('enviar-pedido');
    const modal = document.getElementById('formulario-modal');
    const cerrarModal = document.getElementById('cerrar-modal');
    const formulario = document.getElementById('formulario');
    
    botonEnviar.addEventListener('click', function() {
        if (carrito.length === 0) {
            alert('El carrito está vacío. Agrega productos antes de hacer el pedido.');
            return;
        }
        
        // Verificar si la cafetería está abierta
        if (!estaCafeteriaAbierta()) {
            mostrarMensajeCerrado();
            modal.style.display = 'block';
            return;
        }
        
        // Configurar horarios dinámicos al abrir el modal
        configurarHorarios();
        modal.style.display = 'block';
    });
    
    cerrarModal.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    formulario.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const metodoPago = document.querySelector('input[name="metodoPago"]:checked');
        if (!metodoPago) {
            alert('Por favor selecciona un método de pago');
            return;
        }
        
        // TODOS los métodos van al sistema POS ahora
        if (metodoPago.value === 'tarjeta') {
            // Pago en línea con Mercado Pago
            procesarPagoEnLinea();
        } else {
            // Efectivo o terminal - también van al sistema POS
            procesarPedidoSistema(metodoPago.value);
        }
    });
}

// Enviar pedido por WhatsApp
function enviarPedidoWhatsApp() {
    const nombre = document.getElementById('nombre').value;
    const telefono = document.getElementById('telefono').value;
    const horaRecogida = document.getElementById('horaRecogida').value;
    const metodoPago = document.querySelector('input[name="metodoPago"]:checked');
    
    if (!metodoPago) {
        alert('Por favor selecciona un método de pago');
        return;
    }
    
    let mensaje = `¡Hola! Soy ${nombre}\n`;
    mensaje += `Mi teléfono: ${telefono}\n`;
    mensaje += `Hora de recogida: ${horaRecogida}\n`;
    
    // Agregar método de pago
    const tipoPago = metodoPago.value;
    if (tipoPago === 'efectivo') {
        mensaje += `💵 Método de pago: Efectivo en sucursal\n\n`;
    } else if (tipoPago === 'tarjeta') {
        mensaje += `💳 Método de pago: PAGADO CON MERCADO PAGO ✅\n\n`;
    } else if (tipoPago === 'terminal') {
        mensaje += `🏪 Método de pago: Tarjeta con terminal en sucursal\n\n`;
    }
    
    mensaje += `Mi pedido:\n`;
    
    let total = 0;
    carrito.forEach(item => {
        const subtotal = item.precio * item.cantidad;
        total += subtotal;
        
        let nombreProducto = item.nombrePersonalizado || item.nombre;
        if (item.saboresElegidos && item.saboresElegidos.length > 0) {
            nombreProducto += ` (${item.saboresElegidos.join(' + ')})`;
        }
        
        // Agregar información de leches
        if (item.lechesElegidas && item.lechesElegidas.length > 0) {
            const lechesTexto = item.lechesElegidas.map((leche, index) => {
                if (leche !== 'Entera') {
                    const saborCorrespondiente = item.saboresElegidos ? item.saboresElegidos[index] : `Frappe ${index + 1}`;
                    return `${saborCorrespondiente}: ${leche}`;
                }
                return null;
            }).filter(Boolean);
            
            if (lechesTexto.length > 0) {
                nombreProducto += ` - Leches: ${lechesTexto.join(', ')}`;
            }
        } else if (item.lecheElegida && item.lecheElegida !== 'Entera' && item.lecheElegida !== 'Sin leche') {
            nombreProducto += ` - ${item.lecheElegida}`;
        }
        
        mensaje += `• ${nombreProducto} (${item.cantidad}) - $${subtotal}\n`;
    });
    
    mensaje += `\n💰 Total: $${total}`;
    
    // Agregar nota según el método de pago
    if (tipoPago === 'efectivo') {
        mensaje += `\n\n📝 Nota: Pago en efectivo al recoger el pedido`;
    } else if (tipoPago === 'tarjeta') {
        mensaje += `\n\n✅ PEDIDO PAGADO - Listo para preparar`;
    } else if (tipoPago === 'terminal') {
        mensaje += `\n\n� Nota: Pago con tarjeta usando terminal Mercado Pago en sucursal`;
    }
    
    const numeroWhatsApp = '50246007071'; // Cambia este número por el tuyo
    const urlWhatsApp = `https://wa.me/${numeroWhatsApp}?text=${encodeURIComponent(mensaje)}`;
    
    window.open(urlWhatsApp, '_blank');
    
    // Cerrar modal y limpiar carrito
    document.getElementById('formulario-modal').style.display = 'none';
    carrito = [];
    mostrarCarrito();
    
    // Resetear contadores
    document.querySelectorAll('[id^="cantidad-"]').forEach(span => {
        span.textContent = '0';
    });
    
    // Limpiar formulario
    document.getElementById('formulario').reset();
}

// Función para abrir el menú PDF
function abrirMenuPDF() {
    // Usa el archivo Menu.pdf que está en la carpeta img
    const urlPDF = 'img/Menu.pdf';
    window.open(urlPDF, '_blank');
}

// Inicializar carrito flotante
function inicializarCarritoFlotante() {
    const carritoFlotante = document.getElementById('carrito-flotante');
    
    // Iniciar colapsado en móviles
    if (window.innerWidth <= 768) {
        carritoColapsado = true;
        carritoFlotante.classList.add('collapsed');
    }
    
    // Mostrar/ocultar carrito cuando no hay items
    mostrarCarrito();
}

// Toggle del carrito flotante
function toggleCarrito() {
    const carritoFlotante = document.getElementById('carrito-flotante');
    const toggle = document.getElementById('carrito-toggle');
    
    carritoColapsado = !carritoColapsado;
    
    if (carritoColapsado) {
        carritoFlotante.classList.add('collapsed');
        toggle.textContent = '▲';
    } else {
        carritoFlotante.classList.remove('collapsed');
        toggle.textContent = '▼';
    }
}

// Detectar scroll para animar el carrito
let scrollTimeout;
window.addEventListener('scroll', function() {
    const carritoFlotante = document.getElementById('carrito-flotante');
    
    // Añadir efecto de scroll
    carritoFlotante.style.transform = 'translateY(5px)';
    
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
        carritoFlotante.style.transform = 'translateY(0)';
    }, 150);
});

// Ajustar cantidad directamente desde el carrito
function ajustarCantidadCarrito(index, cambio) {
    if (index >= 0 && index < carrito.length) {
        const item = carrito[index];
        const nuevaCantidad = Math.max(0, item.cantidad + cambio);
        
        if (nuevaCantidad === 0) {
            eliminarDelCarrito(index);
        } else {
            carrito[index].cantidad = nuevaCantidad;
            
            // Actualizar también el contador en la página de productos
            const spanCantidad = document.getElementById(`cantidad-${item.categoria}-${item.index}`);
            if (spanCantidad) {
                spanCantidad.textContent = nuevaCantidad;
            }
            
            mostrarCarrito();
        }
    }
}

// Eliminar producto completamente del carrito
function eliminarDelCarrito(index) {
    if (index >= 0 && index < carrito.length) {
        const item = carrito[index];
        
        // Resetear contador en la página de productos
        const spanCantidad = document.getElementById(`cantidad-${item.categoria}-${item.index}`);
        if (spanCantidad) {
            spanCantidad.textContent = '0';
        }
        
        // Eliminar del carrito
        carrito.splice(index, 1);
        mostrarCarrito();
        
        // Efecto visual de eliminación
        const carritoFlotante = document.getElementById('carrito-flotante');
        carritoFlotante.style.transform = 'scale(0.95)';
        setTimeout(() => {
            carritoFlotante.style.transform = 'scale(1)';
        }, 150);
    }
}

// Vaciar carrito completo
function vaciarCarrito() {
    if (carrito.length > 0 && confirm('¿Estás seguro de que quieres vaciar el carrito?')) {
        // Resetear todos los contadores
        carrito.forEach(item => {
            const spanCantidad = document.getElementById(`cantidad-${item.categoria}-${item.index}`);
            if (spanCantidad) {
                spanCantidad.textContent = '0';
            }
        });
        
        carrito = [];
        mostrarCarrito();
    }
}

// Responsive: auto-colapsar en móviles
window.addEventListener('resize', function() {
    const carritoFlotante = document.getElementById('carrito-flotante');
    
    if (window.innerWidth <= 768 && !carritoColapsado) {
        toggleCarrito();
    } else if (window.innerWidth > 768 && carritoColapsado) {
        toggleCarrito();
    }
});

// Abrir selector de sabores para promociones
function abrirSelectorSabores(categoria, index) {
    const producto = productosData[categoria][index];
    
    // Crear modal de selección de sabores
    const modal = document.createElement('div');
    modal.className = 'modal-sabores';
    modal.innerHTML = `
        <div class="modal-sabores-content">
            <div class="modal-sabores-header">
                <h3>Elige los sabores de tus 2 frappes</h3>
                <button class="cerrar-sabores" onclick="cerrarSelectorSabores()">
                    <span class="cerrar-icono">✕</span>
                </button>
            </div>
            <div class="modal-sabores-body">
                <p>Puedes elegir el mismo sabor para ambos frappes o sabores diferentes:</p>
                
                <!-- Frappe 1 -->
                <div class="frappe-selector">
                    <h4>🥤 Frappe #1:</h4>
                    <div class="sabores-grid" data-frappe="1">
                        ${producto.saboresDisponibles.map(sabor => `
                            <div class="sabor-opcion" onclick="seleccionarSaborFrappe(1, '${sabor}')">
                                <div class="sabor-emoji">${getSaborEmoji(sabor)}</div>
                                <span>${sabor}</span>
                            </div>
                        `).join('')}
                    </div>
                    <div class="sabor-elegido" id="sabor-frappe-1">
                        <span class="sabor-placeholder">Selecciona un sabor</span>
                    </div>
                    
                    <!-- Selector de leche para Frappe 1 -->
                    <div class="leche-frappe-selector">
                        <h5>🥛 Leche para Frappe #1:</h5>
                        <div class="leches-grid-frappe" data-frappe="1">
                            ${producto.lechesDisponibles.map(leche => `
                                <div class="leche-opcion-frappe ${leche === 'Entera' ? 'seleccionado' : ''}" onclick="seleccionarLecheFrappe(1, '${leche}')">
                                    <div class="leche-icono">${getLecheEmoji(leche)}</div>
                                    <span>${leche}</span>
                                </div>
                            `).join('')}
                        </div>
                        <div class="leche-frappe-elegida" id="leche-frappe-1">
                            <span class="leche-confirmada">${getLecheEmoji('Entera')} Entera</span>
                        </div>
                    </div>
                </div>
                
                <!-- Frappe 2 -->
                <div class="frappe-selector">
                    <h4>🥤 Frappe #2:</h4>
                    <div class="sabores-grid" data-frappe="2">
                        ${producto.saboresDisponibles.map(sabor => `
                            <div class="sabor-opcion" onclick="seleccionarSaborFrappe(2, '${sabor}')">
                                <div class="sabor-emoji">${getSaborEmoji(sabor)}</div>
                                <span>${sabor}</span>
                            </div>
                        `).join('')}
                    </div>
                    <div class="sabor-elegido" id="sabor-frappe-2">
                        <span class="sabor-placeholder">Selecciona un sabor</span>
                    </div>
                    
                    <!-- Selector de leche para Frappe 2 -->
                    <div class="leche-frappe-selector">
                        <h5>🥛 Leche para Frappe #2:</h5>
                        <div class="leches-grid-frappe" data-frappe="2">
                            ${producto.lechesDisponibles.map(leche => `
                                <div class="leche-opcion-frappe ${leche === 'Entera' ? 'seleccionado' : ''}" onclick="seleccionarLecheFrappe(2, '${leche}')">
                                    <div class="leche-icono">${getLecheEmoji(leche)}</div>
                                    <span>${leche}</span>
                                </div>
                            `).join('')}
                        </div>
                        <div class="leche-frappe-elegida" id="leche-frappe-2">
                            <span class="leche-confirmada">${getLecheEmoji('Entera')} Entera</span>
                        </div>
                    </div>
                </div>
                
                <div class="resumen-seleccion">
                    <h4>📋 Resumen de tu pedido:</h4>
                    <div id="resumen-sabores"></div>
                </div>
            </div>
            <div class="modal-sabores-footer">
                <button id="confirmar-sabores" onclick="confirmarSabores('${categoria}', ${index})" disabled>
                    Agregar al Carrito
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.saboresFrappe1 = null;
    modal.saboresFrappe2 = null;
    modal.lecheFrappe1 = 'Entera'; // Leche por defecto para frappe 1
    modal.lecheFrappe2 = 'Entera'; // Leche por defecto para frappe 2
    
    // Mostrar modal inmediatamente
    modal.style.display = 'flex';
}

// Cerrar selector de sabores
function cerrarSelectorSabores() {
    const modal = document.querySelector('.modal-sabores');
    if (modal) {
        modal.classList.remove('mostrar');
        setTimeout(() => modal.remove(), 300);
    }
}

// Seleccionar sabor para un frappe específico
function seleccionarSaborFrappe(numeroFrappe, sabor) {
    const modal = document.querySelector('.modal-sabores');
    if (!modal) return;
    
    // Limpiar selección anterior para este frappe
    const gridFrappe = document.querySelector(`[data-frappe="${numeroFrappe}"]`);
    gridFrappe.querySelectorAll('.sabor-opcion').forEach(opcion => {
        opcion.classList.remove('seleccionado');
    });
    
    // Marcar nuevo sabor como seleccionado
    const saborOpcion = gridFrappe.querySelector(`[onclick="seleccionarSaborFrappe(${numeroFrappe}, '${sabor}')"]`);
    saborOpcion.classList.add('seleccionado');
    
    // Guardar selección
    if (numeroFrappe === 1) {
        modal.saboresFrappe1 = sabor;
    } else {
        modal.saboresFrappe2 = sabor;
    }
    
    // Actualizar display del sabor elegido
    const contenedorSabor = document.getElementById(`sabor-frappe-${numeroFrappe}`);
    contenedorSabor.innerHTML = `<span class="sabor-confirmado">${getSaborEmoji(sabor)} ${sabor}</span>`;
    
    // Actualizar resumen
    actualizarResumenSabores();
    
    // Actualizar estado del botón
    actualizarBotonConfirmarPromo();
}

// Actualizar resumen de sabores seleccionados
function actualizarResumenSabores() {
    const modal = document.querySelector('.modal-sabores');
    const contenedor = document.getElementById('resumen-sabores');
    
    if (!modal.saboresFrappe1 && !modal.saboresFrappe2) {
        contenedor.innerHTML = '<span class="resumen-placeholder">Selecciona los sabores para ambos frappes</span>';
        return;
    }
    
    let resumen = '<div class="resumen-items">';
    
    if (modal.saboresFrappe1) {
        resumen += `<div class="resumen-item">🥤 Frappe 1: ${getSaborEmoji(modal.saboresFrappe1)} ${modal.saboresFrappe1}</div>`;
    } else {
        resumen += `<div class="resumen-item pendiente">🥤 Frappe 1: Pendiente</div>`;
    }
    
    if (modal.saboresFrappe2) {
        resumen += `<div class="resumen-item">🥤 Frappe 2: ${getSaborEmoji(modal.saboresFrappe2)} ${modal.saboresFrappe2}</div>`;
    } else {
        resumen += `<div class="resumen-item pendiente">🥤 Frappe 2: Pendiente</div>`;
    }
    
    resumen += '</div>';
    
    // Mostrar si son iguales o diferentes
    if (modal.saboresFrappe1 && modal.saboresFrappe2) {
        if (modal.saboresFrappe1 === modal.saboresFrappe2) {
            resumen += '<div class="tipo-seleccion">✨ ¡2 frappes del mismo sabor!</div>';
        } else {
            resumen += '<div class="tipo-seleccion">🎨 ¡2 sabores diferentes!</div>';
        }
    }
    
    contenedor.innerHTML = resumen;
}

// Confirmar sabores y agregar al carrito
function confirmarSabores(categoria, index) {
    const modal = document.querySelector('.modal-sabores');
    if (!modal || !modal.saboresFrappe1 || !modal.saboresFrappe2 || !modal.lecheFrappe1 || !modal.lecheFrappe2) return;
    
    const producto = productosData[categoria][index];
    const spanCantidad = document.getElementById(`cantidad-${categoria}-${index}`);
    let cantidadActual = parseInt(spanCantidad.textContent);
    let nuevaCantidad = cantidadActual + 1;
    
    spanCantidad.textContent = nuevaCantidad;
    
    // Crear array de sabores elegidos
    const saboresElegidos = [modal.saboresFrappe1, modal.saboresFrappe2];
    
    // Crear array de leches elegidas
    const lechesElegidas = [modal.lecheFrappe1, modal.lecheFrappe2];
    
    // Crear nombre personalizado más detallado
    let nombrePersonalizado;
    if (modal.saboresFrappe1 === modal.saboresFrappe2) {
        nombrePersonalizado = `${producto.nombre} (2x ${modal.saboresFrappe1})`;
    } else {
        nombrePersonalizado = `${producto.nombre} (${modal.saboresFrappe1} + ${modal.saboresFrappe2})`;
    }
    
    // Agregar información de leches si no son ambas enteras
    const lechesTexto = [];
    if (modal.lecheFrappe1 !== 'Entera') {
        lechesTexto.push(`${modal.saboresFrappe1}: ${modal.lecheFrappe1}`);
    }
    if (modal.lecheFrappe2 !== 'Entera') {
        lechesTexto.push(`${modal.saboresFrappe2}: ${modal.lecheFrappe2}`);
    }
    
    if (lechesTexto.length > 0) {
        nombrePersonalizado += ` - ${lechesTexto.join(', ')}`;
    }
    
    const productoCarrito = {
        ...producto,
        categoria: categoria,
        index: index,
        cantidad: nuevaCantidad,
        saboresElegidos: saboresElegidos,
        lechesElegidas: lechesElegidas,
        nombrePersonalizado: nombrePersonalizado
    };
    
    actualizarCarrito(productoCarrito);
    cerrarSelectorSabores();
}

// Abrir selector de leche para productos lácteos
function abrirSelectorLeche(categoria, index) {
    const producto = productosData[categoria][index];
    
    // Crear modal de selección de leche
    const modal = document.createElement('div');
    modal.className = 'modal-leche';
    modal.innerHTML = `
        <div class="modal-leche-content">
            <div class="modal-leche-header">
                <h3>🥛 Elige tu tipo de leche</h3>
                <button class="cerrar-leche" onclick="cerrarSelectorLeche()">
                    <span class="cerrar-icono">✕</span>
                </button>
            </div>
            <div class="modal-leche-body">
                <p>Selecciona el tipo de leche para tu <strong>${producto.nombre}</strong>:</p>
                ${producto.nombre === 'Americano' ? '<p class="americano-nota"><em>💡 El Americano tradicionalmente se sirve solo, pero puedes agregar leche si lo prefieres</em></p>' : ''}
                
                <div class="leches-grid">
                    ${producto.lechesDisponibles.map(leche => {
                        const esDefecto = (producto.nombre === 'Americano' && leche === 'Sin leche') || 
                                         (producto.nombre !== 'Americano' && leche === 'Entera');
                        return `
                            <div class="leche-opcion ${esDefecto ? 'seleccionada' : ''}" onclick="seleccionarLeche('${leche}')">
                                <div class="leche-icono">${getLecheEmoji(leche)}</div>
                                <div class="leche-info">
                                    <span class="leche-nombre">${leche}</span>
                                    <span class="leche-descripcion">${getLecheDescripcion(leche)}</span>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
                
                <div class="leche-seleccionada">
                    <h4>Leche seleccionada:</h4>
                    <div id="leche-elegida">
                        ${producto.nombre === 'Americano' ? 
                            `<span class="leche-confirmada">${getLecheEmoji('Sin leche')} Sin leche</span>` :
                            `<span class="leche-confirmada">${getLecheEmoji('Entera')} Entera</span>`
                        }
                    </div>
                </div>
            </div>
            <div class="modal-leche-footer">
                <button id="confirmar-leche" onclick="confirmarLeche('${categoria}', ${index})">
                    Agregar al Carrito
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Configurar leche por defecto según el producto
    if (producto.nombre === 'Americano') {
        modal.lecheSeleccionada = 'Sin leche';
    } else {
        modal.lecheSeleccionada = 'Entera';
    }
    
    // Mostrar modal con animación
    setTimeout(() => modal.classList.add('mostrar'), 10);
}

// Cerrar selector de leche
function cerrarSelectorLeche() {
    const modal = document.querySelector('.modal-leche');
    if (modal) {
        modal.classList.remove('mostrar');
        setTimeout(() => modal.remove(), 300);
    }
}

// Seleccionar tipo de leche
function seleccionarLeche(leche) {
    const modal = document.querySelector('.modal-leche');
    if (!modal) return;
    
    // Limpiar selección anterior
    document.querySelectorAll('.leche-opcion').forEach(opcion => {
        opcion.classList.remove('seleccionado');
    });
    
    // Marcar nueva selección
    const lecheOpcion = document.querySelector(`[onclick="seleccionarLeche('${leche}')"]`);
    lecheOpcion.classList.add('seleccionado');
    
    // Guardar selección
    modal.lecheSeleccionada = leche;
    
    // Actualizar display
    const contenedor = document.getElementById('leche-elegida');
    contenedor.innerHTML = `<span class="leche-confirmada">${getLecheEmoji(leche)} ${leche}</span>`;
    
    // Habilitar botón
    const btnConfirmar = document.getElementById('confirmar-leche');
    btnConfirmar.disabled = false;
}

// Confirmar leche y agregar al carrito
function confirmarLeche(categoria, index) {
    const modal = document.querySelector('.modal-leche');
    if (!modal || !modal.lecheSeleccionada) return;
    
    const producto = productosData[categoria][index];
    const spanCantidad = document.getElementById(`cantidad-${categoria}-${index}`);
    let cantidadActual = parseInt(spanCantidad.textContent);
    let nuevaCantidad = cantidadActual + 1;
    
    spanCantidad.textContent = nuevaCantidad;
    
    // Crear nombre personalizado
    let nombrePersonalizado = producto.nombre;
    if (modal.lecheSeleccionada !== 'Entera') {
        nombrePersonalizado += ` - ${modal.lecheSeleccionada}`;
    }
    
    const productoCarrito = {
        ...producto,
        categoria: categoria,
        index: index,
        cantidad: nuevaCantidad,
        lecheElegida: modal.lecheSeleccionada,
        nombrePersonalizado: nombrePersonalizado
    };
    
    actualizarCarrito(productoCarrito);
    cerrarSelectorLeche();
}

// Seleccionar leche para promociones
function seleccionarLechePromo(leche) {
    const modal = document.querySelector('.modal-sabores');
    if (!modal) return;
    
    // Limpiar selección anterior
    document.querySelectorAll('.leche-opcion-promo').forEach(opcion => {
        opcion.classList.remove('seleccionado');
    });
    
    // Marcar nueva selección
    const lecheOpcion = document.querySelector(`[onclick="seleccionarLechePromo('${leche}')"]`);
    lecheOpcion.classList.add('seleccionado');
    
    // Guardar selección
    modal.lecheSeleccionada = leche;
    
    // Actualizar display
    const contenedor = document.getElementById('leche-promo-elegida');
    contenedor.innerHTML = `<span class="leche-confirmada">${getLecheEmoji(leche)} ${leche}</span>`;
    
    // Actualizar estado del botón
    actualizarBotonConfirmarPromo();
}

// Actualizar estado del botón de confirmar promoción
function actualizarBotonConfirmarPromo() {
    const modal = document.querySelector('.modal-sabores');
    const btnConfirmar = document.getElementById('confirmar-sabores');
    
    if (modal && btnConfirmar) {
        btnConfirmar.disabled = !modal.saboresFrappe1 || !modal.saboresFrappe2 || !modal.lecheFrappe1 || !modal.lecheFrappe2;
    }
}

// Obtener emoji para cada tipo de leche
function getLecheEmoji(leche) {
    const emojis = {
        'Sin leche': '☕',
        'Entera': '🥛',
        'Deslactosada': '🌱',
        'Deslactosada Light': '💧'
    };
    return emojis[leche] || '🥛';
}

// Obtener descripción para cada tipo de leche
function getLecheDescripcion(leche) {
    const descripciones = {
        'Sin leche': 'Café americano tradicional',
        'Entera': 'Cremosa y tradicional',
        'Deslactosada': 'Sin lactosa, misma cremosidad',
        'Deslactosada Light': 'Sin lactosa, menos grasa'
    };
    return descripciones[leche] || '';
}

// Obtener emoji para cada sabor
function getSaborEmoji(sabor) {
    const emojis = {
        'Moka': '☕',
        'Capuchino': '🤎',
        'Taro': '💜',
        'Caramelo': '🍯',
        'Oreo': '🍪'
    };
    return emojis[sabor] || '🥤';
}

// Configurar horarios de atención dinámicos
function configurarHorarios() {
    const horaRecogida = document.getElementById('horaRecogida');
    const horarioInfo = document.getElementById('horario-info');
    
    if (!horaRecogida || !horarioInfo) return;
    
    const ahora = new Date();
    const diaSemana = ahora.getDay(); // 0 = Domingo, 1 = Lunes, etc.
    
    // Limpiar opciones existentes excepto la primera
    horaRecogida.innerHTML = '<option value="">Selecciona un horario</option>';
    
    // Definir horarios por día
    const horarios = {
        1: null, // Lunes - Cerrado
        2: { inicio: 12, fin: 20, nombre: "Martes" }, // Martes 12pm-8pm
        3: { inicio: 12, fin: 20, nombre: "Miércoles" }, // Miércoles 12pm-8pm
        4: { inicio: 12, fin: 20, nombre: "Jueves" }, // Jueves 12pm-8pm
        5: { inicio: 12, fin: 20, nombre: "Viernes" }, // Viernes 12pm-8pm
        6: { inicio: 12, fin: 20, nombre: "Sábado" }, // Sábado 12pm-8pm
        0: { inicio: 9, fin: 14, nombre: "Domingo" } // Domingo 9am-2pm
    };
    
    const horarioHoy = horarios[diaSemana];
    
    if (!horarioHoy) {
        // Lunes - cerrado
        horarioInfo.innerHTML = `
            <div class="horario-cerrado">
                <strong>¡Lo sentimos!</strong> Los lunes estamos cerrados.<br>
                Horarios: Martes a Sábado 12:00 PM - 8:00 PM | Domingos 9:00 AM - 2:00 PM
            </div>
        `;
        horaRecogida.disabled = true;
        horaRecogida.innerHTML = '<option value="">Cerrado los lunes</option>';
        return;
    }
    
    // Generar opciones de horario para el día actual
    const opciones = [];
    for (let hora = horarioHoy.inicio; hora < horarioHoy.fin; hora++) {
        // Hora en punto
        const horaFormato12 = hora > 12 ? hora - 12 : hora;
        const periodo = hora >= 12 ? 'PM' : 'AM';
        const horaTexto = `${horaFormato12}:00 ${periodo}`;
        opciones.push(horaTexto);
        
        // Media hora (excepto la última hora)
        if (hora < horarioHoy.fin - 1) {
            const mediaHoraTexto = `${horaFormato12}:30 ${periodo}`;
            opciones.push(mediaHoraTexto);
        }
    }
    
    // Agregar opciones al select
    opciones.forEach(opcion => {
        const option = document.createElement('option');
        option.value = opcion;
        option.textContent = opcion;
        horaRecogida.appendChild(option);
    });
    
    // Mostrar información del horario
    let infoTexto = '';
    if (diaSemana === 0) {
        infoTexto = `<span class="dia-actual">Domingo:</span> 9:00 AM - 2:00 PM`;
    } else {
        infoTexto = `<span class="dia-actual">${horarioHoy.nombre}:</span> 12:00 PM - 8:00 PM`;
    }
    infoTexto += '<br><small>Lunes cerrado | Domingos 9:00 AM - 2:00 PM</small>';
    
    horarioInfo.innerHTML = infoTexto;
    horaRecogida.disabled = false;
}

// Actualizar horarios en el header
function actualizarHorariosHeader() {
    const horarioHoy = document.getElementById('horario-hoy');
    if (!horarioHoy) return;
    
    const ahora = new Date();
    const diaSemana = ahora.getDay(); // 0 = Domingo, 1 = Lunes, etc.
    const dias = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
    const nombreDia = dias[diaSemana];
    
    let mensaje = '';
    let clase = '';
    
    switch (diaSemana) {
        case 1: // Lunes
            mensaje = `🚫 Hoy ${nombreDia} - CERRADO`;
            clase = 'cerrado';
            break;
        case 0: // Domingo
            mensaje = `☀️ Hoy ${nombreDia} - 9:00 AM a 2:00 PM`;
            clase = 'abierto';
            break;
        default: // Martes a Sábado
            mensaje = `⏰ Hoy ${nombreDia} - 12:00 PM a 8:00 PM`;
            clase = 'abierto';
            break;
    }
    
    horarioHoy.textContent = mensaje;
    horarioHoy.className = `horario-dia ${clase}`;
    
    // Si está cerrado, agregar efecto especial al header
    const header = document.querySelector('header');
    if (diaSemana === 1) {
        header.classList.add('dia-cerrado');
    } else {
        header.classList.remove('dia-cerrado');
    }
}

// Verificar si la cafetería está abierta hoy
function estaCafeteriaAbierta() {
    const ahora = new Date();
    const diaSemana = ahora.getDay(); // 0 = Domingo, 1 = Lunes, etc.
    
    // Lunes está cerrado
    if (diaSemana === 1) {
        return false;
    }
    
    return true;
}

// Mostrar mensaje cuando está cerrado
function mostrarMensajeCerrado() {
    const modal = document.getElementById('formulario-modal');
    modal.innerHTML = `
        <div class="modal-content">
            <span class="cerrar-modal" onclick="cerrarModalCerrado()">&times;</span>
            <div style="text-align: center; padding: 20px;">
                <h2 style="color: #721c24;">🚫 Cafetería Cerrada</h2>
                <p>Lo sentimos, los <strong>lunes estamos cerrados</strong>.</p>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">
                    <strong>Nuestros horarios:</strong><br>
                    📅 Martes a Sábado: 12:00 PM - 8:00 PM<br>
                    📅 Domingos: 9:00 AM - 2:00 PM<br>
                    ❌ Lunes: Cerrado
                </div>
                <p>¡Te esperamos mañana!</p>
                <button onclick="cerrarModalCerrado()" style="background: #e74c3c; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">Entendido</button>
            </div>
        </div>
    `;
}

// Cerrar modal de cerrado y restaurar el modal original
function cerrarModalCerrado() {
    const modal = document.getElementById('formulario-modal');
    modal.style.display = 'none';
    
    // Restaurar el modal original
    modal.innerHTML = `
        <div class="modal-content">
            <span class="cerrar-modal" id="cerrar-modal">&times;</span>
            <h2>Datos del Cliente</h2>
            <form id="formulario">
                <label>Nombre completo:</label>
                <input type="text" id="nombre" placeholder="Tu nombre completo" required><br>
        
                <label>Teléfono:</label>
                <input type="tel" id="telefono" placeholder="Tu número de teléfono" required><br>
        
                <label>¿A qué hora quieres recoger tu pedido?</label>
                <select id="horaRecogida" required>
                    <option value="">Selecciona un horario</option>
                </select>
                <div id="horario-info" class="horario-info"></div><br><br>
        
                <button type="submit">Confirmar Pedido</button>
            </form>
        </div>
    `;
    
    // Reconfigurar eventos
    configurarCarrito();
}

// Mostrar banner informativo cuando está cerrado
function mostrarBannerCerrado() {
    const ahora = new Date();
    const diaSemana = ahora.getDay();
    
    if (diaSemana === 1) { // Lunes
        const contenedorProductos = document.querySelector('.productos');
        const banner = document.createElement('div');
        banner.className = 'banner-cerrado';
        banner.innerHTML = `
            <div class="banner-cerrado-contenido">
                <h3>🚫 Cafetería Cerrada - Lunes</h3>
                <p>Los lunes estamos cerrados para descanso del personal.</p>
                <div class="horarios-banner">
                    <strong>Nuestros horarios de atención:</strong><br>
                    📅 Martes a Sábado: 12:00 PM - 8:00 PM<br>
                    📅 Domingos: 9:00 AM - 2:00 PM
                </div>
                <p>¡Puedes explorar nuestro menú y preparar tu pedido para mañana!</p>
            </div>
        `;
        
        contenedorProductos.insertBefore(banner, contenedorProductos.firstChild);
    }
}

// Seleccionar leche para un frappe específico en promociones
function seleccionarLecheFrappe(numeroFrappe, leche) {
    const modal = document.querySelector('.modal-sabores');
    if (!modal) return;
    
    // Limpiar selección anterior para este frappe
    const gridFrappe = document.querySelector(`[data-frappe="${numeroFrappe}"].leches-grid-frappe`);
    if (gridFrappe) {
        gridFrappe.querySelectorAll('.leche-opcion-frappe').forEach(opcion => {
            opcion.classList.remove('seleccionado');
        });
    }
    
    // Marcar nueva selección
    const lecheOpcion = document.querySelector(`[onclick="seleccionarLecheFrappe(${numeroFrappe}, '${leche}')"]`);
    if (lecheOpcion) {
        lecheOpcion.classList.add('seleccionado');
    }
    
    // Guardar selección en el modal
    if (numeroFrappe === 1) {
        modal.lecheFrappe1 = leche;
    } else {
        modal.lecheFrappe2 = leche;
    }
    
    // Actualizar display
    const contenedor = document.getElementById(`leche-frappe-${numeroFrappe}`);
    if (contenedor) {
        contenedor.innerHTML = `<span class="leche-confirmada">${getLecheEmoji(leche)} ${leche}</span>`;
    }
    
    // Actualizar estado del botón
    actualizarBotonConfirmarPromo();
}

// Procesar pago en línea con Mercado Pago
function procesarPagoEnLinea() {
    if (!mp) {
        alert('Error: Mercado Pago no está configurado correctamente. Verifica tu Public Key.');
        return;
    }
    
    // Obtener datos del formulario
    const nombre = document.getElementById('nombre').value;
    const telefono = document.getElementById('telefono').value;
    const horaRecogida = document.getElementById('horaRecogida').value;
    
    // Validar campos
    if (!nombre || !telefono || !horaRecogida) {
        alert('Por favor completa todos los campos');
        return;
    }
    
    // Mostrar modal de checkout
    mostrarCheckoutModal();
    
    // Crear preferencia de pago
    crearPreferenciaPago();
}

// Mostrar modal de checkout
function mostrarCheckoutModal() {
    const modal = document.getElementById('checkout-modal');
    const resumenContainer = document.getElementById('resumen-productos');
    const totalContainer = document.getElementById('total-pago');
    const checkoutContainer = document.getElementById('checkout-container');
    
    // Mostrar resumen del pedido
    let resumenHTML = '';
    let total = 0;
    
    carrito.forEach(item => {
        const subtotal = item.precio * item.cantidad;
        total += subtotal;
        
        let nombreProducto = item.nombrePersonalizado || item.nombre;
        let detalles = '';
        
        if (item.saboresElegidos && item.saboresElegidos.length > 0) {
            detalles += `Sabores: ${item.saboresElegidos.join(' + ')}`;
        }
        
        if (item.lecheElegida && item.lecheElegida !== 'Entera') {
            detalles += detalles ? ` | Leche: ${item.lecheElegida}` : `Leche: ${item.lecheElegida}`;
        }
        
        resumenHTML += `
            <div class="resumen-item">
                <div class="resumen-item-info">
                    <div class="resumen-item-nombre">${nombreProducto} (${item.cantidad})</div>
                    ${detalles ? `<div class="resumen-item-detalles">${detalles}</div>` : ''}
                </div>
                <div class="resumen-item-precio">$${subtotal}</div>
            </div>
        `;
    });
    
    resumenContainer.innerHTML = resumenHTML;
    totalContainer.textContent = total;
    
    // Mostrar loading en checkout
    checkoutContainer.innerHTML = '<div class="checkout-loading">Cargando formulario de pago...</div>';
    
    modal.style.display = 'flex';
    
    // Configurar botón cerrar
    document.getElementById('cerrar-checkout').onclick = function() {
        modal.style.display = 'none';
    };
}

// Crear preferencia de pago - NUEVA VERSIÓN CON BACKEND
async function crearPreferenciaPago() {
    try {
        console.log('🔄 Creando preferencia de pago...');
        
        // Preparar datos del pedido
        const nombre = document.getElementById('nombre').value;
        const telefono = document.getElementById('telefono').value;
        const horaRecogida = document.getElementById('horaRecogida').value;
        
        let total = 0;
        const items = carrito.map(item => {
            const subtotal = item.precio * item.cantidad;
            total += subtotal;
            
            let nombreProducto = item.nombrePersonalizado || item.nombre;
            if (item.saboresElegidos && item.saboresElegidos.length > 0) {
                nombreProducto += ` (${item.saboresElegidos.join(' + ')})`;
            }
            
            if (item.lecheElegida && item.lecheElegida !== 'Entera') {
                nombreProducto += ` (Leche: ${item.lecheElegida})`;
            }
            
            return {
                id: item.nombre.toLowerCase().replace(/\s+/g, '_'),
                title: nombreProducto,
                quantity: item.cantidad,
                unit_price: item.precio,
                description: `${item.nombre} - Hora recogida: ${horaRecogida}`
            };
        });
        
        // Datos de la preferencia para nuestro backend
        const orderData = {
            items: items,
            payer: {
                name: nombre,
                phone: {
                    area_code: "502", // Código de área de Guatemala
                    number: telefono
                },
                email: `${telefono}@caffeymiga.com` // Email temporal basado en teléfono
            },
            payment_method: 'tarjeta',
            notes: `Hora de recogida: ${horaRecogida}. Total: $${total}`,
            metadata: {
                pickup_time: horaRecogida,
                source: 'web_ecommerce'
            }
        };
        
        console.log('📦 Datos del pedido:', orderData);
        
        // Enviar al backend para crear la preferencia de Mercado Pago
        const response = await fetch('http://localhost:3000/create_preference', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData)
        });
        
        if (!response.ok) {
            throw new Error(`Error del servidor: ${response.status} ${response.statusText}`);
        }
        
        const preference = await response.json();
        console.log('✅ Preferencia creada:', preference);
        
        // Redirigir a Mercado Pago
        if (preference.init_point) {
            console.log('🔄 Redirigiendo a Mercado Pago...');
            window.location.href = preference.init_point;
        } else {
            throw new Error('No se recibió link de pago de Mercado Pago');
        }
        
    } catch (error) {
        console.error('❌ Error al crear preferencia:', error);
        handleCheckoutError(error);
    }
}

// Crear checkout de Mercado Pago
async function crearCheckout(preferenceId) {
    try {
        console.log('🎨 Creando checkout con preferencia:', preferenceId);
        
        const checkoutContainer = document.getElementById('checkout-container');
        
        // Limpiar container
        checkoutContainer.innerHTML = '<div class="checkout-loading">Cargando formulario de pago...</div>';
        
        // Crear checkout
        const checkout = mp.checkout({
            preference: {
                id: preferenceId
            },
            render: {
                container: '#checkout-container',
                label: 'Pagar con Mercado Pago'
            },
            theme: {
                elementsColor: '#8B4513',
                headerColor: '#8B4513'
            }
        });
        
        console.log('✅ Checkout creado exitosamente');
        
    } catch (error) {
        console.error('❌ Error al crear checkout:', error);
        handleCheckoutError(error);
    }
}

// Manejar errores del checkout
function handleCheckoutError(error) {
    const checkoutContainer = document.getElementById('checkout-container');
    
    checkoutContainer.innerHTML = `
        <div class="checkout-error">
            <h3>❌ Error al procesar el pago</h3>
            <p><strong>Error:</strong> ${error.message}</p>
            
            <div class="error-actions">
                <button onclick="reintentar_pago()" class="btn-reintentar">
                    🔄 Reintentar
                </button>
                <button onclick="volverAWhatsApp()" class="btn-whatsapp-error">
                    📱 Enviar por WhatsApp
                </button>
            </div>
            
            <div class="error-info">
                <h4>💡 Soluciones:</h4>
                <ul>
                    <li>Verifica que tu backend esté ejecutándose</li>
                    <li>Confirma que la URL del backend sea correcta</li>
                    <li>Revisa las credenciales de Mercado Pago</li>
                    <li>Comprueba la consola del navegador para más detalles</li>
                </ul>
            </div>
        </div>
    `;
}

// Reintentar pago
function reintentar_pago() {
    console.log('🔄 Reintentando pago...');
    crearPreferenciaPago();
}

// Volver a WhatsApp desde checkout
function volverAWhatsApp() {
    document.getElementById('checkout-modal').style.display = 'none';
    enviarPedidoWhatsApp();
}

// Procesar pedido para efectivo o terminal - NUEVA FUNCIÓN
async function procesarPedidoSistema(metodoPago) {
    try {
        console.log(`🔄 Procesando pedido con método: ${metodoPago}`);
        
        // Obtener datos del formulario
        const nombre = document.getElementById('nombre').value;
        const telefono = document.getElementById('telefono').value;
        const horaRecogida = document.getElementById('horaRecogida').value;
        
        // Validar campos
        if (!nombre || !telefono || !horaRecogida) {
            alert('Por favor completa todos los campos');
            return;
        }
        
        let total = 0;
        const items = carrito.map(item => {
            const subtotal = item.precio * item.cantidad;
            total += subtotal;
            
            let nombreProducto = item.nombrePersonalizado || item.nombre;
            if (item.saboresElegidos && item.saboresElegidos.length > 0) {
                nombreProducto += ` (${item.saboresElegidos.join(' + ')})`;
            }
            
            if (item.lecheElegida && item.lecheElegida !== 'Entera') {
                nombreProducto += ` (Leche: ${item.lecheElegida})`;
            }
            
            return {
                id: item.nombre.toLowerCase().replace(/\s+/g, '_'),
                title: nombreProducto,
                quantity: item.cantidad,
                unit_price: item.precio,
                description: `${item.nombre} - Hora recogida: ${horaRecogida}`
            };
        });
        
        // Datos del pedido para el sistema
        const orderData = {
            items: items,
            payer: {
                name: nombre,
                phone: {
                    area_code: "502",
                    number: telefono
                },
                email: `${telefono}@caffeymiga.com`
            },
            payment_method: metodoPago, // 'efectivo' o 'terminal'
            notes: `Hora de recogida: ${horaRecogida}. Total: $${total}. Método: ${metodoPago === 'efectivo' ? 'Efectivo en sucursal' : 'Terminal Mercado Pago en sucursal'}`,
            metadata: {
                pickup_time: horaRecogida,
                source: 'web_ecommerce',
                payment_method: metodoPago,
                requires_payment: false // No requiere pago en línea
            }
        };
        
        console.log('📦 Enviando pedido al sistema:', orderData);
        
        // Mostrar loading
        showLoadingMessage('Procesando pedido...');
        
        // Enviar al backend - endpoint específico para pedidos del sistema
        const response = await fetch('http://localhost:3000/pos/orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData)
        });
        
        console.log('📡 Respuesta del servidor:', response.status, response.statusText);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Error del servidor:', errorText);
            throw new Error(`Error del servidor: ${response.status} - ${errorText}`);
        }
        
        const result = await response.json();
        console.log('✅ Pedido procesado:', result);
        
        // Ocultar loading
        hideLoadingMessage();
        
        // Mostrar confirmación
        mostrarConfirmacionPedido(metodoPago, total, nombre, telefono, horaRecogida);
        
    } catch (error) {
        console.error('❌ Error procesando pedido:', error);
        
        // Ocultar loading
        hideLoadingMessage();
        
        alert('Error al procesar el pedido. Por favor intenta nuevamente.');
    }
}

// Mostrar confirmación de pedido
function mostrarConfirmacionPedido(metodoPago, total, nombre, telefono, horaRecogida) {
    const metodoTexto = metodoPago === 'efectivo' ? 'Efectivo en sucursal' : 'Terminal Mercado Pago en sucursal';
    
    const mensaje = `
    🎉 ¡Pedido confirmado!
    
    👤 Cliente: ${nombre}
    📱 Teléfono: ${telefono}
    🕐 Hora de recogida: ${horaRecogida}
    💰 Total: $${total}
    💳 Método de pago: ${metodoTexto}
    
    ✅ Tu pedido ha sido enviado a la cafetería
    📱 Te contactaremos para confirmar
    ⏰ Ten listo tu pago cuando recojas
    `;
    
    alert(mensaje);
    
    // Limpiar carrito y volver al inicio
    carrito = [];
    mostrarCarrito();
    
    // Resetear contadores
    document.querySelectorAll('[id^="cantidad-"]').forEach(span => {
        span.textContent = '0';
    });
    
    // Cerrar modal y limpiar formulario
    document.getElementById('formulario-modal').style.display = 'none';
    document.getElementById('formulario').reset();
}

// Mostrar mensaje de loading
function showLoadingMessage(mensaje) {
    // Crear overlay de loading si no existe
    let overlay = document.getElementById('loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
            color: white;
            font-size: 18px;
            font-weight: bold;
        `;
        document.body.appendChild(overlay);
    }
    
    overlay.innerHTML = `
        <div style="text-align: center;">
            <div style="font-size: 50px; margin-bottom: 20px;">⏳</div>
            <div>${mensaje}</div>
        </div>
    `;
    overlay.style.display = 'flex';
    
    // Ocultar después de 3 segundos
    setTimeout(() => {
        overlay.style.display = 'none';
    }, 3000);
}

// Ocultar mensaje de loading
function hideLoadingMessage() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}