/* Cartas (newsletter) con MailerLite. Para cambiar de formulario, cambia SOLO esta constante
   (y el action del HTML, que es el respaldo sin JavaScript). */
const CARTA_ACTION = 'https://assets.mailerlite.com/jsonp/2734247/forms/202049256123532577/subscribe';
document.querySelectorAll('aside.carta form').forEach(function (f) {
  f.action = CARTA_ACTION;
  f.addEventListener('submit', function (e) {
    if (!window.fetch || !window.FormData) return; /* respaldo: envío normal en pestaña nueva */
    e.preventDefault();
    var ok = f.parentNode.querySelector('.carta-ok'), btn = f.querySelector('button');
    btn.disabled = true;
    fetch(CARTA_ACTION, { method: 'POST', mode: 'no-cors', body: new FormData(f) })
      .then(function () { f.reset(); if (ok) ok.textContent = 'Revisa tu correo para confirmar la suscripción.'; })
      .catch(function () { f.submit(); })
      .then(function () { btn.disabled = false; });
  });
});
