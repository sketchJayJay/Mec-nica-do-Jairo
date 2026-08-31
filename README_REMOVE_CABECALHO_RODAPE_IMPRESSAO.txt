Correção: remove cabeçalho/rodapé automático na impressão da OS.

Alterações:
- templates/print_os.html com <title> vazio.
- @page margin: 0 para cortar cabeçalho/rodapé do navegador.
- margem visual mantida no body com padding 16mm.

Marcador:
REMOVE_CABECALHO_RODAPE_BROWSER_IMPRESSAO_OS_20260831

Observação: se o navegador/Chrome ainda imprimir data, título, URL ou número da página, desmarque “Cabeçalhos e rodapés” na janela de impressão.
