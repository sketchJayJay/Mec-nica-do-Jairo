function onlyNumber(v){
  const s = String(v || '').replace(/\./g,'').replace(',', '.').replace(/[^0-9.]/g,'');
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
  input.addEventListener('input', () => {
    clearTimeout(estoqueTimer);
    estoqueTimer = setTimeout(() => searchEstoque(input.value), 250);
  });
}
async function searchEstoque(q){
  const box = document.getElementById('estoqueResultados');
  if(!box) return;
  if(!q){ box.innerHTML=''; return; }
  const res = await fetch('/api/estoque?q=' + encodeURIComponent(q));
  const rows = await res.json();
  box.innerHTML = rows.map(r => `<div class="result-item"><div><b>${r.item}</b><br><small>${r.categoria} • qtd ${r.qtde} • ${moneyBR(r.preco)}</small></div><button type="button" class="btn small" onclick='pickEstoque(${JSON.stringify(r).replaceAll("'", "&#39;")})'>Usar</button></div>`).join('') || '<div class="empty">Nenhum item achado.</div>';
}
function pickEstoque(r){
  document.getElementById('itemCategoria').value = r.categoria || 'Outros';
  document.getElementById('itemNome').value = r.item || '';
  document.getElementById('itemValor').value = Number(r.preco || 0).toLocaleString('pt-BR',{minimumFractionDigits:2, maximumFractionDigits:2});
  document.getElementById('itemQtde').focus();
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
  document.getElementById('estoqueBusca').value='';
  document.getElementById('estoqueResultados').innerHTML='';
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

// Layout Cadastro Desktop Exato 2026-08-31
let SELECTED_ESTOQUE_ITEM = null;
function setServiceTab(tab){
  document.querySelectorAll('.desktop-service-tabs .tab-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
  const desc = document.getElementById('descricaoPane');
  const itens = document.getElementById('itensPane');
  if(desc) desc.classList.toggle('active', tab === 'descricao');
  if(itens) itens.classList.toggle('active', tab === 'itens');
}
function toggleEstoquePicker(){
  const picker = document.getElementById('estoquePicker');
  if(!picker) return;
  picker.classList.toggle('hidden-helper');
  if(!picker.classList.contains('hidden-helper')){
    const busca = document.getElementById('estoqueBusca');
    if(busca) busca.focus();
  }
}
function setupEstoqueSearch(){
  const input = document.getElementById('estoqueBusca');
  if(!input) return;
  input.addEventListener('input', () => {
    clearTimeout(estoqueTimer);
    estoqueTimer = setTimeout(() => searchEstoque(input.value), 180);
  });
}
async function searchEstoque(q){
  const box = document.getElementById('estoqueResultados');
  if(!box) return;
  if(!q){ box.innerHTML=''; return; }
  const res = await fetch('/api/estoque?q=' + encodeURIComponent(q));
  const rows = await res.json();
  box.innerHTML = rows.map(r => `<div class="result-item"><div><b>${escapeHtml(r.item)}</b><br><small>${escapeHtml(r.categoria || '')} • qtd ${r.qtde} • ${moneyBR(r.preco)}</small></div><button type="button" class="btn small" onclick='pickEstoque(${JSON.stringify(r).replaceAll("'", "&#39;")})'>Selecionar</button></div>`).join('') || '<div class="empty">Nenhum item achado.</div>';
}
function pickEstoque(r){
  SELECTED_ESTOQUE_ITEM = r || null;
  const set = (id,v) => { const el=document.getElementById(id); if(el) el.value = v || ''; };
  set('itemCategoria', r.categoria || 'Outros');
  set('itemNome', r.item || '');
  set('itemValor', Number(r.preco || 0).toLocaleString('pt-BR',{minimumFractionDigits:2, maximumFractionDigits:2}));
  set('itemQtde', '1');
  const label = document.getElementById('selectedItemLabel');
  if(label) label.textContent = r.item ? `${r.item} selecionado` : 'Nenhum item selecionado';
}
function addSelectedOrPrompt(){
  const nomeEl = document.getElementById('itemNome');
  const catEl = document.getElementById('itemCategoria');
  const qtdEl = document.getElementById('itemQtde');
  const valEl = document.getElementById('itemValor');
  const baixaEl = document.getElementById('itemBaixa');
  let nome = nomeEl?.value || '';
  let cat = catEl?.value || 'Outros';
  let qtde = qtdEl?.value || '1';
  let valor = valEl?.value || '0,00';
  let baixa = baixaEl?.value || '1';
  if(!nome.trim()){
    nome = prompt('Nome do item:', '') || '';
    if(!nome.trim()) return;
    cat = prompt('Categoria:', 'Outros') || 'Outros';
    qtde = prompt('Quantidade:', '1') || '1';
    valor = prompt('Valor unitário:', '0,00') || '0,00';
    baixa = '1';
  }
  addItemRow(cat, nome, qtde, valor, baixa);
  if(nomeEl) nomeEl.value = '';
  if(valEl) valEl.value = '';
  if(qtdEl) qtdEl.value = '1';
  const busca = document.getElementById('estoqueBusca');
  const res = document.getElementById('estoqueResultados');
  const label = document.getElementById('selectedItemLabel');
  if(busca) busca.value = '';
  if(res) res.innerHTML = '';
  if(label) label.textContent = 'Nenhum item selecionado';
  SELECTED_ESTOQUE_ITEM = null;
}
function addItemFromInputs(){ addSelectedOrPrompt(); }
function addMaoObraInline(){
  const desc = document.getElementById('maoObraDesc')?.value || 'Mão de obra';
  const valor = document.getElementById('maoObraValor')?.value || '0,00';
  if(!desc.trim()){ alert('Informe a mão de obra.'); return; }
  addItemRow('Mão de obra', desc, '1', valor, '0');
  const d = document.getElementById('maoObraDesc');
  const v = document.getElementById('maoObraValor');
  if(d) d.value = '';
  if(v) v.value = '';
}
function addMaoObra(){ addMaoObraInline(); }
function addItemRow(cat,nome,qtde,valor,baixa){
  const tbody = document.querySelector('#itensTable tbody');
  if(!tbody) return;
  const tr = document.createElement('tr');
  tr.setAttribute('onclick','selectItemRow(this)');
  tr.innerHTML = `<td><input name="item_categoria[]" value="${escapeHtml(cat)}"></td>
    <td><input name="item_nome[]" value="${escapeHtml(nome)}"><input type="hidden" name="item_baixa[]" value="${escapeHtml(baixa || '1')}"></td>
    <td><input name="item_qtde[]" value="${escapeHtml(qtde)}" inputmode="decimal" oninput="recalcItens()"></td>
    <td><input name="item_valor[]" value="${escapeHtml(valor)}" inputmode="decimal" oninput="recalcItens()"></td>
    <td class="row-total">R$ 0,00</td>`;
  tbody.appendChild(tr);
  recalcItens();
}
function selectItemRow(row){
  document.querySelectorAll('#itensTable tbody tr').forEach(r => r.classList.remove('selected-row'));
  if(row) row.classList.add('selected-row');
}
function removeSelectedItem(){
  const row = document.querySelector('#itensTable tbody tr.selected-row');
  if(!row){ alert('Selecione um item na tabela para remover.'); return; }
  row.remove();
  recalcItens();
}
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
function excluirPorPlaca(){
  const placa = (document.getElementById('placa')?.value || '').trim();
  if(!placa){ alert('Informe a placa para localizar a OS.'); return; }
  window.location.href = '/os?q=' + encodeURIComponent(placa);
}
