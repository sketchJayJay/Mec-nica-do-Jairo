# Mecânica do Jairo - Web para Coolify

Versão web em Flask + SQLite + Docker, pronta para subir pelo GitHub no Coolify.

## Visual

Esta versão foi ajustada para ficar parecida com o sistema antigo/novo das telas enviadas:

- topo com logo, nome **MECÂNICA DO JAIRO** e texto **Pro Light 2025 — FIX**
- menu em abas: Início, Cadastro, Busca, Estoque e Relatórios
- tela inicial com imagem da oficina no fundo e cartões transparentes
- Cadastro/OS, Busca, Estoque e Relatórios com visual mais simples, claro e parecido com o programa de desktop

## Funções mantidas

- Cadastro de cliente
- Cadastro de veículo com Marca e Veículo/Modelo já com opções
- Digitação manual quando não tiver marca/modelo na lista
- Nova OS / Nota
- Buscar, abrir, editar, imprimir e excluir OS
- Editar OS pronta sem refazer tudo
- Baixa de estoque ao salvar OS
- Ao editar ou excluir OS, o estoque antigo é revertido para evitar baixa dupla
- Estoque com adicionar, editar, excluir, buscar e imprimir
- Relatórios básicos
- Banco SQLite persistente em `/app/data`

## Como subir no Coolify

1. Crie um repositório no GitHub.
2. Envie todos os arquivos desta pasta para o repositório.
3. No Coolify, crie um novo recurso usando esse repositório.
4. Escolha deploy por Dockerfile ou Docker Compose.
5. Porta interna: `8080`.
6. Faça o deploy.

## Volume obrigatório

O banco fica em:

```txt
/app/data/jairo_oficina.db
```

No Coolify, mantenha um volume persistente em:

```txt
/app/data
```

Sem esse volume, o sistema pode perder clientes, OS e estoque depois de redeploy.
