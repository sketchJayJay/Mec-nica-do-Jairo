# Mecânica do Jairo • versão web para Coolify

Esta versão foi criada a partir do banco real da oficina e preparada para rodar no navegador, celular e computador.

## O que foi corrigido / incluído

- OS podem ser abertas e editadas mesmo depois de `Finalizada`.
- É possível alterar apenas uma linha da OS, sem refazer a OS inteira.
- Itens adicionados pelo estoque na versão web ficam vinculados ao produto e o saldo é reconciliado automaticamente quando quantidade é aumentada, reduzida ou removida.
- OS antigas continuam preservadas. Como o sistema antigo não gravava o ID do produto do estoque dentro da OS, itens históricos antigos não alteram estoque automaticamente quando editados, evitando baixar ou repor a peça errada.
- Estoque permite editar **nome/descrição**, categoria, quantidade e preço.
- Botão para imprimir a relação completa do estoque com todos os itens, quantidades, preços e valor total.
- Busca de cliente por nome, telefone e placa.
- Edição dos dados do carro.
- Impressão/reimpressão da OS.
- Backup do banco pelo próprio sistema.
- Relatório de movimentações do estoque feitas pela nova versão.
- Layout responsivo para celular.
- A antiga rotina de atualização do programa Windows deixa de ser necessária. Atualizações passam a ser feitas pelo deploy/redeploy do Coolify.

## Banco de dados

O banco original enviado foi colocado em:

`seed/oficina.db`

No primeiro start do container, se `/data/oficina.db` ainda não existir, o sistema copia automaticamente esse banco para o volume persistente.

O sistema também cria automaticamente um backup pré-migração chamado aproximadamente:

`/data/oficina.db.pre-web-v2.bak`

### Dados conferidos antes da migração

- 425 clientes
- 410 veículos
- 676 ordens de serviço
- 4.239 itens de OS
- 1.300 itens de estoque

## Coolify

### Opção recomendada: Docker Compose

No Coolify:

1. Crie um novo Resource usando o repositório deste projeto.
2. Escolha **Docker Compose**.
3. O arquivo está na raiz e se chama exatamente `docker-compose.yaml`.
4. Configure as variáveis:
   - `LOGIN_REMOVIDO`
   - `LOGIN_REMOVIDO`
   - `SECRET_KEY`
5. Faça o deploy.
6. A aplicação escuta na porta `8000`.
7. Configure o domínio no Coolify apontando para o serviço na porta interna `8000`.

> Use um repositório **privado**. O arquivo `seed/oficina.db` contém os dados reais da oficina.

O volume `mecanica_jairo_data` mantém o banco entre os deploys.

## Login inicial

Se nenhuma variável for definida, o sistema inicia com:

- usuário: `admin`
- senha: `admin`

**Troque isso no Coolify antes de deixar o domínio público.**

## Backup

Dentro do sistema existe o botão **Baixar backup**. Ele usa o recurso de backup do próprio SQLite para gerar uma cópia consistente mesmo com a aplicação ligada.

Mesmo com esse botão, é recomendado manter também backup externo do volume `/data`.

## Desenvolvimento local

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Acesse `http://localhost:8000`.

## Observação importante sobre o estoque antigo

O programa Windows baixava estoque por nome/categoria e não salvava uma referência segura do produto em `itens_servico`. Por isso a nova versão não tenta adivinhar automaticamente qual produto pertence a cada uma das milhares de linhas históricas. Isso evita corromper o saldo atual.

A partir da nova versão, peças escolhidas em **Buscar no estoque** recebem `estoque_id`, e alterações futuras passam a ser exatas.


## Modelo original da OS
A impressão da Ordem de Serviço mantém o modelo original do programa desktop, incluindo logo, QR PIX, seções Cliente/Veículo/Serviço, tabela de itens e assinatura.


## v9
- A placa passou a ser opcional ao criar ou editar uma OS.
- OS sem placa continuam vinculadas a um carro/cliente normalmente.


## Orçamentos sem baixa de estoque

Esta versão inclui um módulo separado de **Orçamentos**. Ele pode puxar nome, categoria e preço dos itens cadastrados no estoque, mas **não baixa, não reserva e não repõe quantidades**. Criar, editar ou excluir um orçamento não gera movimentação de estoque.

Fluxo: **Orçamentos → Novo orçamento → buscar item no estoque → ajustar nome/quantidade/preço → salvar → Imprimir / PDF**.


## v12 - X para fechar
- Botão X vermelho no canto superior direito.
- Quando aberto pelo aplicativo Windows/PyWebView, fecha a janela inteira com um clique.
