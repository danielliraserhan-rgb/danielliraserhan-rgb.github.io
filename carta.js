/* Cartas (newsletter): URL del formulario del proveedor de correo.
   Para conectarlo, cambia SOLO esta constante. */
const CARTA_ACTION = 'https://PENDIENTE-PROVEEDOR.example/subscribe';
document.querySelectorAll('aside.carta form').forEach(function (f) { f.action = CARTA_ACTION; });
