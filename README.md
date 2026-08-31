# Jairo Oficina Web - Correção editar OS sem sobrepor

Versão: EDITAR_OS_SEM_SOBREPOR_20260831

Correções:
- Na edição de OS, a tabela de itens agora fica com scroll e não passa por cima da linha Mão de obra/Preço/Adicionar.
- Rodapé Remover selecionado e Total ficam presos no lugar certo.
- Corrigido cálculo no navegador para aceitar valores como 81.50 e 81,50 sem virar 8.150,00.
- Valores antigos abrem com vírgula decimal no campo Unitário.

Banco/volume preservados:
- DB_PATH=/data/oficina.db
- mecanica-jairo-data:/data


Versão: BOTAO_SALVAR_EDICAO_OS_20260831
- Adiciona botão destacado para salvar quando estiver editando OS.
- Mantém banco /data/oficina.db e volume mecanica-jairo-data:/data.


Versão: BUSCA_ESTOQUE_MODAL_TOPO_FUNCIONANDO_20260831


Versão: BOTAO_ADICIONAR_ITEM_MODAL_20260831
- Cards da busca exibem botão "Adicionar item".
- Clique no card adiciona direto na OS e mostra confirmação.


Versão: FLUXO_SELECIONAR_QTD_ADICIONAR_20260831
- Botão Usar apenas seleciona o item do estoque.
- Usuário escolhe quantidade e clica em Adicionar item.
