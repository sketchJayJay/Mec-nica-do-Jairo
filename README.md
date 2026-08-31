# REMOVER_ITEM_SELECIONADO_20260831

Correção do fluxo do estoque na OS:

- Depois de clicar em Usar, o item fica selecionado.
- Agora existe botão **Remover seleção** antes de adicionar na OS.
- O botão de remover item da tabela ficou mais claro: **Remover item selecionado da OS**.
- Se tentar remover sem selecionar linha, aparece aviso.

Banco/volume mantidos:
- /data/oficina.db
- mecanica-jairo-data:/data


Versão: EXCLUIR_ITEM_LINHA_EDITAR_OS_20260831
- Adiciona botão Excluir em cada linha dos itens da OS, inclusive ao editar OS salva.
- O item só é removido de verdade do banco quando clicar em Salvar alterações da OS.


Correção: CORRIGE_BUSCA_ITEM_PAROU_20260831
Remove duplicidade de const baixa que quebrava o JavaScript da tela e fazia a busca de estoque parar.
