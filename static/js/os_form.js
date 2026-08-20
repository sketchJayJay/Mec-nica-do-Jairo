(() => {
  const tbody = document.querySelector('#items-table tbody');
  if (!tbody) return;
  const initial = JSON.parse(document.getElementById('initial-items').textContent || '[]');
  const money = v => Number(v || 0).toLocaleString('pt-BR',{style:'currency',currency:'BRL'});
  const num = v => { const n = Number(String(v ?? '').replace(',','.')); return Number.isFinite(n) ? n : 0; };
  const esc = s => String(s ?? '').replace(/[&<>"]/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));

  function rowHtml(item={}) {
    const stockId = item.estoque_id || '';
    const origin = Number(item.origem_estoque || 0) ? 1 : 0;
    const itemId = item.id || '';
    const qty = Math.max(1, Number(item.qtde || 1));
    const price = Number(item.valor_unit ?? item.preco ?? 0);
    return `<tr>
      <td>
        <input type="hidden" name="item_id[]" value="${esc(itemId)}">
        <input type="hidden" name="item_estoque_id[]" value="${esc(stockId)}">
        <input type="hidden" name="item_origem_estoque[]" value="${origin}">
        <input class="item-cat" name="item_categoria[]" value="${esc(item.categoria || '')}" aria-label="Categoria" ${origin ? 'readonly title="Item vinculado ao estoque. Para trocar a peça, remova a linha e adicione outra pelo estoque."' : ''}>
      </td>
      <td><input class="item-name" name="item_nome[]" value="${esc(item.item || '')}" required aria-label="Item" ${origin ? 'readonly title="Item vinculado ao estoque. Para trocar a peça, remova a linha e adicione outra pelo estoque."' : ''}></td>
      <td><input class="item-qty" name="item_qtde[]" type="number" min="1" step="1" value="${qty}" aria-label="Quantidade"></td>
      <td><input class="item-price" name="item_preco[]" inputmode="decimal" value="${price.toFixed(2)}" aria-label="Preço unitário"></td>
      <td class="row-total">${money(qty*price)}</td>
      <td><button type="button" class="remove-row" title="Remover linha">×</button></td>
    </tr>`;
  }
  function addRow(item){ tbody.insertAdjacentHTML('beforeend', rowHtml(item)); recalc(); }
  function recalc(){
    let total=0;
    tbody.querySelectorAll('tr').forEach(tr=>{
      const q=num(tr.querySelector('.item-qty')?.value); const p=num(tr.querySelector('.item-price')?.value);
      const t=q*p; total+=t; tr.querySelector('.row-total').textContent=money(t);
    });
    document.getElementById('grand-total').textContent=money(total);
  }
  initial.forEach(addRow);
  tbody.addEventListener('input', e=>{ if(e.target.matches('.item-qty,.item-price')) recalc(); });
  tbody.addEventListener('click', e=>{ const b=e.target.closest('.remove-row'); if(b){ b.closest('tr').remove(); recalc(); }});

  document.getElementById('add-labor')?.addEventListener('click',()=>addRow({categoria:'Mão de obra',item:'Serviço',qtde:1,valor_unit:0,estoque_id:null,origem_estoque:0}));

  // Próxima troca de óleo automática
  const km = document.getElementById('km_atual'), intv = document.getElementById('intervalo_km'), prox = document.getElementById('proxima_manut_km');
  function calcProx(){ const a=parseInt(km?.value||'0',10)||0, b=parseInt(intv?.value||'0',10)||0; if(prox) prox.value=b>0?a+b:a; }
  km?.addEventListener('input',calcProx); intv?.addEventListener('change',calcProx);

  // Modal de estoque
  const modal=document.getElementById('stock-modal'), search=document.getElementById('stock-search'), results=document.getElementById('stock-results');
  const openModal=()=>{ modal.classList.add('open'); modal.setAttribute('aria-hidden','false'); setTimeout(()=>search.focus(),50); loadStock(''); };
  const closeModal=()=>{ modal.classList.remove('open'); modal.setAttribute('aria-hidden','true'); };
  document.getElementById('open-stock')?.addEventListener('click',openModal);
  modal?.querySelectorAll('[data-close-modal]').forEach(b=>b.addEventListener('click',closeModal));
  modal?.addEventListener('click',e=>{ if(e.target===modal)closeModal(); });
  document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal();});
  let stockTimer;
  search?.addEventListener('input',()=>{clearTimeout(stockTimer);stockTimer=setTimeout(()=>loadStock(search.value),180)});
  async function loadStock(q){
    results.innerHTML='<p class="empty">Buscando...</p>';
    try{
      const r=await fetch(`/api/estoque?q=${encodeURIComponent(q||'')}`); const data=await r.json();
      results.innerHTML=data.length?data.map(i=>`<div class="stock-item ${Number(i.qtde)<=0?'out':''}">
        <div><strong>${esc(i.item)}</strong><small>${esc(i.categoria||'Sem categoria')} • ${money(i.preco)}</small></div>
        <div class="stock-qty">Estoque: ${i.qtde}</div>
        <button type="button" class="btn small primary choose-stock" data-id="${i.id}" data-name="${esc(i.item)}" data-cat="${esc(i.categoria||'')}" data-price="${i.preco}" data-qty="${i.qtde}" ${Number(i.qtde)<=0?'disabled':''}>Adicionar</button>
      </div>`).join(''):'<p class="empty">Nenhum item encontrado.</p>';
    }catch{results.innerHTML='<p class="empty">Falha ao buscar o estoque.</p>'}
  }
  results?.addEventListener('click',e=>{
    const b=e.target.closest('.choose-stock'); if(!b)return;
    const available=Number(b.dataset.qty||0); let qty=Number(prompt(`Quantidade (disponível: ${available}):`,'1')||0);
    if(!Number.isInteger(qty)||qty<=0)return; if(qty>available){alert(`Só existem ${available} unidade(s) no estoque.`);return;}
    addRow({estoque_id:Number(b.dataset.id),origem_estoque:1,categoria:b.dataset.cat,item:b.dataset.name,qtde:qty,valor_unit:Number(b.dataset.price||0)}); closeModal();
  });

  // Busca cliente / carro
  const csearch=document.getElementById('client-search'), cresults=document.getElementById('client-results'); let ctimer;
  csearch?.addEventListener('input',()=>{clearTimeout(ctimer); const q=csearch.value.trim(); if(q.length<1){cresults.classList.remove('open');return;} ctimer=setTimeout(()=>loadClients(q),180)});
  async function loadClients(q){
    try{
      const r=await fetch(`/api/clientes?q=${encodeURIComponent(q)}`); const data=await r.json();
      cresults.innerHTML=data.length?data.map((x,idx)=>`<div class="lookup-item" data-idx="${idx}"><strong>${esc(x.nome)}</strong><small>${esc(x.telefone||'')} ${x.placa?'• '+esc(x.marca||'')+' '+esc(x.modelo||'')+' • '+esc(x.placa):'• sem carro'}</small></div>`).join(''):'<div class="lookup-item"><small>Nada encontrado. Preencha abaixo para cadastrar.</small></div>';
      cresults._data=data; cresults.classList.add('open');
    }catch{cresults.classList.remove('open')}
  }
  cresults?.addEventListener('click',e=>{
    const el=e.target.closest('.lookup-item[data-idx]'); if(!el)return; const x=cresults._data[Number(el.dataset.idx)]; if(!x)return;
    const set=(id,v)=>{const n=document.getElementById(id);if(n)n.value=v??''};
    set('cliente_id',x.cliente_id);set('veiculo_id',x.veiculo_id||'');set('cliente_nome',x.nome);set('cliente_telefone',x.telefone);set('marca',x.marca);set('modelo',x.modelo);set('placa',x.placa);set('ano',x.ano);set('veiculo_km_atual',x.km_atual||0);set('km_troca_corr',x.km_troca_corr||0);set('km_corr_trocada',x.km_corr_trocada||0);set('km_corr_proxima',x.km_corr_proxima||0);
    csearch.value=x.nome+(x.placa?' • '+x.placa:'');cresults.classList.remove('open');
  });
  document.addEventListener('click',e=>{if(!e.target.closest('.lookup-box'))cresults?.classList.remove('open')});

  document.getElementById('os-form')?.addEventListener('submit',e=>{
    if(!tbody.querySelector('tr') && !confirm('A OS está sem itens. Deseja salvar assim mesmo?')) e.preventDefault();
  });
})();
