// MSG_ITEM_MELHOR_VOLTA_IMPRIMIR_ESTOQUE_20260901
// MSG_ITEM_ADICIONADO_FECHAR_BUSCA_20260901
// CORRIGE_BUSCA_ITEM_PAROU_20260831
// REMOVER_ITEM_SELECIONADO_20260831
// FLUXO_SELECIONAR_QTD_ADICIONAR_20260831
// baseado em BOTAO_ADICIONAR_ITEM_MODAL_20260831
// BUSCA_ESTOQUE_MODAL_TOPO_FUNCIONANDO_20260831
// BUSCA_ESTOQUE_MAIS_VISIVEL_20260831
// BOTAO_SALVAR_CADASTRO_E_BUSCA_ESTOQUE_COMPLETA_20260831
// EDITAR_OS_SEM_SOBREPOR_20260831
function onlyNumber(v){
  let s = String(v || '').trim().replace('R$', '').replace(/\s/g, '');
  if(!s) return 0;
  // Aceita 81,50, 81.50, 1.234,56 e 1234.56 sem transformar centavos em milhares.
  const hasComma = s.includes(',');
  const hasDot = s.includes('.');
  if(hasComma){
    s = s.replace(/\./g, '').replace(',', '.');
  } else if(hasDot){
    const parts = s.split('.');
    const last = parts[parts.length - 1];
    if(parts.length > 2 || last.length === 3){
      s = s.replace(/\./g, '');
    }
  }
  s = s.replace(/[^0-9.\-]/g, '');
  const n = parseFloat(s);
  return isNaN(n) ? 0 : n;
}
function moneyBR(n){
  return (n || 0).toLocaleString('pt-BR',{style:'currency',currency:'BRL'});
}
function setupVehicleOptions(){
  const marca = document.getElementById('marca');
  const modelo = document.getElementById('modelo');
  const modelosList = document.getElementById('modelosList');
  if(!marca || !modelo || !modelosList) return;
  function fill(suggest=false){
    const list = (window.BRANDS && window.BRANDS[marca.value]) || (window.BRANDS && window.BRANDS['Outros']) || [];
    modelosList.innerHTML = list.map(x => `<option value="${String(x).replaceAll('"','&quot;')}">`).join('');
    if(suggest && !modelo.value && list.length) modelo.value = list[0];
  }
  marca.addEventListener('input', () => fill(false));
  marca.addEventListener('change', () => fill(true));
  fill(false);
}
function setupCalculations(){
  const km = document.getElementById('km_atual');
  const intervalo = document.getElementById('intervalo_km');
  const prox = document.getElementById('proxima_manut_km');
  const corrInt = document.getElementById('km_troca_corr');
  const corrFeita = document.getElementById('km_corr_trocada');
  const corrProx = document.getElementById('km_corr_proxima');
  function calcOleo(){ if(km && intervalo && prox){ const soma = onlyNumber(km.value) + onlyNumber(intervalo.value); if(soma>0) prox.value = Math.round(soma).toLocaleString('pt-BR'); } }
  function calcCorr(){ if(corrInt && corrFeita && corrProx){ const soma = onlyNumber(corrInt.value) + onlyNumber(corrFeita.value); if(soma>0) corrProx.value = Math.round(soma).toLocaleString('pt-BR'); } }
  [km,intervalo].forEach(el => el && el.addEventListener('input', calcOleo));
  [corrInt,corrFeita].forEach(el => el && el.addEventListener('input', calcCorr));
}
let estoqueTimer;
function setupEstoqueSearch(){
  const input = document.getElementById('estoqueBusca');
  if(!input) return;
  const run = () => {
    clearTimeout(estoqueTimer);
    estoqueTimer = setTimeout(() => searchEstoque(input.value), 120);
  };
  input.addEventListener('input', run);
  input.addEventListener('keyup', run);
  input.addEventListener('change', run);
}
async function searchEstoque(q){
  const box = document.getElementById('estoqueResultados');
  const status = document.getElementById('estoqueStatus');
  if(!box) return;
  const query = String(q || '').trim();
  box.innerHTML = '<div class="empty estoque-loading">Carregando itens do estoque...</div>';
  if(status) status.textContent = query ? `Buscando por: ${query}` : 'Mostrando itens do estoque';
  try{
    const res = await fetch('/api/estoque?q=' + encodeURIComponent(query), {cache:'no-store'});
    if(!res.ok){ throw new Error('HTTP ' + res.status); }
    const rows = await res.json();
    const header = query
      ? `${rows.length} item(ns) encontrado(s) para "${escapeHtml(query)}"`
      : `${rows.length} item(ns) do estoque para escolher`;
    if(status) status.textContent = header;
    box.innerHTML = (rows.map(r => `
      <button type="button" class="result-item-card" onclick='pickEstoque(${JSON.stringify(r).replaceAll("'", "&#39;")})'>
        <div class="result-main">
          <div class="result-title">${escapeHtml(r.item || '')}</div>
          <div class="result-sub">
            <span class="result-badge">${escapeHtml(r.categoria || 'Sem categoria')}</span>
            <span class="result-meta">Qtde: ${escapeHtml(r.qtde ?? 0)}</span>
            <span class="result-meta">ID: ${escapeHtml(r.id ?? '')}</span>
          </div>
        </div>
        <div class="result-side">
          <div class="result-price">${moneyBR(Number(r.preco || 0))}</div>
          <span class="result-use">Usar</span>
        </div>
      </button>`).join('') || '<div class="empty">Nenhum item achado. Tente outra palavra, categoria ou deixe vazio para ver o estoque.</div>');
  }catch(err){
    if(status) status.textContent = 'Erro ao buscar estoque';
    box.innerHTML = `<div class="empty error-box">Não consegui buscar no estoque. Erro: ${escapeHtml(err.message || err)}. Veja os logs do Coolify.</div>`;
  }
}

function hideItemAddedNoticeOldReal(){
  const notice = document.getElementById('itemAddedNotice');
  if(notice) notice.classList.remove('show');
}
function focusSearchAfterAddOldReal(){
  hideItemAddedNoticeOldReal();
  const busca = document.getElementById('estoqueBusca');
  if(busca){ busca.focus(); busca.select?.(); }
}
function showItemAddedNoticeOldReal(nome){
  const notice = document.getElementById('itemAddedNotice');
  const noticeText = document.getElementById('itemAddedNoticeText');
  if(noticeText){
    noticeText.innerHTML = `<span class="item-added-notice-title">${escapeHtml(nome)} adicionado na OS.</span><span class="item-added-notice-sub">Pode escolher outro item ou clicar em Fechar busca para voltar para a OS.</span>`;
  }
  if(notice) notice.classList.add('show');
  const label = document.getElementById('selectedItemLabel');
  if(label) label.textContent = `${nome} adicionado. Pode adicionar outro.`;
  const status = document.getElementById('estoqueStatus');
  if(status) status.textContent = 'Item adicionado. A busca continua aberta para escolher outro.';
}
function pickEstoque(r){
  hideItemAddedNoticeOldReal();
  // FLUXO_SELECIONAR_QTD_ADICIONAR_20260831
  // Primeiro seleciona o item; depois o usuário informa quantidade e clica em Adicionar item.
  const cat = r.categoria || 'Outros';
  const nome = r.item || '';
  const valor = Number(r.preco || 0).toLocaleString('pt-BR',{minimumFractionDigits:2, maximumFractionDigits:2});
  if(!nome){ return; }
  const set = (id,v) => { const el=document.getElementById(id); if(el) el.value = v || ''; };
  set('itemCategoria', cat);
  set('itemNome', nome);
  set('itemValor', valor);
  set('itemQtde', '1');
  set('itemBaixa', '1');
  const label = document.getElementById('selectedItemLabel');
  if(label) label.textContent = `${nome} selecionado`;
  const status = document.getElementById('estoqueStatus');
  if(status) status.textContent = `Item selecionado: ${nome}. Agora informe a quantidade e clique em Adicionar item.`;
  const panel = document.getElementById('selectedStockPanel');
  if(panel) panel.classList.add('selected-stock-active');
  const q = document.getElementById('itemQtde');
  if(q){ q.focus(); q.select?.(); }
}
function addItemFromInputs(){
  const cat = document.getElementById('itemCategoria').value || 'Outros';
  const nome = document.getElementById('itemNome').value || '';
  const qtde = document.getElementById('itemQtde').value || '1';
  const valor = document.getElementById('itemValor').value || '0,00';
  const baixa = document.getElementById('itemBaixa').value || '1';
  if(!nome.trim()){ alert('Informe o item.'); return; }
  addItemRow(cat,nome,qtde,valor,baixa);
  ['itemNome','itemValor'].forEach(id => document.getElementById(id).value='');
  document.getElementById('itemQtde').value='1';
  showItemAddedNoticeOldReal(nome);
  const busca = document.getElementById('estoqueBusca'); if(busca) busca.focus();
}
function addMaoObra(){
  const desc = prompt('Descrição da mão de obra:', 'Mão de obra');
  if(!desc) return;
  const valor = prompt('Valor da mão de obra:', '0,00') || '0,00';
  addItemRow('Mão de obra', desc, '1', valor, '0');
}
function addItemRow(cat,nome,qtde,valor,baixa){
  const tbody = document.querySelector('#itensTable tbody');
  if(!tbody) return;
  const tr = document.createElement('tr');
  tr.innerHTML = `<td><input name="item_categoria[]" value="${escapeHtml(cat)}"></td>
    <td><input name="item_nome[]" value="${escapeHtml(nome)}"></td>
    <td><input name="item_qtde[]" value="${escapeHtml(qtde)}" inputmode="decimal" oninput="recalcItens()"></td>
    <td><input name="item_valor[]" value="${escapeHtml(valor)}" inputmode="decimal" oninput="recalcItens()"></td>
    <td class="row-total">R$ 0,00</td>
    <td class="no-print"><select name="item_baixa[]"><option value="1" ${baixa==='1'?'selected':''}>Sim</option><option value="0" ${baixa==='0'?'selected':''}>Não</option></select></td>
    <td class="no-print"><button class="btn danger small" type="button" onclick="removeRow(this)">Excluir</button></td>`;
  tbody.appendChild(tr);
  recalcItens();
}
function escapeHtml(s){ return String(s || '').replace(/[&<>"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch])); }
function removeRow(btn){ btn.closest('tr').remove(); recalcItens(); }
function recalcItens(){
  let total = 0;
  document.querySelectorAll('#itensTable tbody tr').forEach(tr => {
    const qtd = onlyNumber(tr.querySelector('[name="item_qtde[]"]')?.value);
    const val = onlyNumber(tr.querySelector('[name="item_valor[]"]')?.value);
    const row = qtd * val;
    total += row;
    const cell = tr.querySelector('.row-total'); if(cell) cell.textContent = moneyBR(row);
  });
  const out = document.getElementById('itensTotal'); if(out) out.textContent = moneyBR(total);
}
async function buscarClientes(){
  let q = document.getElementById('clienteBusca')?.value || '';
  if(!q.trim()){
    q = document.getElementById('nome')?.value || document.getElementById('placa')?.value || '';
  }
  const box = document.getElementById('clienteResultados');
  if(!box) return;
  const res = await fetch('/api/clientes?q=' + encodeURIComponent(q));
  const rows = await res.json();
  box.innerHTML = rows.map(r => `<div class="result-item"><div><b>${r.nome}</b><br><small>${r.telefone || ''} • ${r.marca || ''} ${r.modelo || ''} • ${r.placa || ''}</small></div><button type="button" class="btn small" onclick='fillCliente(${JSON.stringify(r).replaceAll("'", "&#39;")})'>Usar</button></div>`).join('') || '<div class="empty">Nenhum cadastro encontrado.</div>';
}
function fillCliente(r){
  const set = (id,v) => { const el=document.getElementById(id); if(el) el.value = v || ''; };
  set('nome', r.nome); set('telefone', r.telefone); set('marca', r.marca); set('modelo', r.modelo); set('placa', r.placa); set('ano', r.ano); set('km_atual', r.km_atual);
  set('km_troca_corr', r.km_troca_corr); set('km_corr_trocada', r.km_corr_trocada); set('km_corr_proxima', r.km_corr_proxima);
  setupVehicleOptions();
  document.getElementById('clienteResultados').innerHTML='';
}

window.addEventListener('keydown', (ev) => {
  if(ev.key === 'F2'){
    ev.preventDefault();
    buscarClientes();
  }
});
