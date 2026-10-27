(function(){
  var f=document.getElementById('bib-filtros'); if(!f) return;
  var items=[].slice.call(document.querySelectorAll('.bib-item'));
  var cuenta=document.getElementById('bib-cuenta'), vacio=document.getElementById('bib-vacio');
  f.hidden=false;
  var q=new URLSearchParams(location.search);
  ['tipo','libro','tema'].forEach(function(k){ if(q.get(k)) f.elements[k].value=q.get(k); });
  function has(list,v){ return !v || (list||'').split('|').indexOf(v)>-1; }
  function aplicar(){
    var t=f.elements.tipo.value, l=f.elements.libro.value, m=f.elements.tema.value, n=0;
    items.forEach(function(el){
      var ok=(!t||el.dataset.tipo===t)&&has(el.dataset.libros,l)&&has(el.dataset.temas,m);
      el.hidden=!ok; if(ok) n++;
    });
    cuenta.textContent=n+(n===1?' elemento':' elementos');
    vacio.hidden=n>0;
    var p=new URLSearchParams(); if(t)p.set('tipo',t); if(l)p.set('libro',l); if(m)p.set('tema',m);
    history.replaceState(null,'',location.pathname+(p.toString()?'?'+p:''));
  }
  f.addEventListener('change',aplicar);
  f.addEventListener('reset',function(){ setTimeout(aplicar,0); });
  aplicar();
})();
