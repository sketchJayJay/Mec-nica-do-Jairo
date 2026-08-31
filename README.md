# Mecânica do Jairo - Coolify

Versão com a tela de Cadastro/OS no visual Pro Light antigo, mantendo as alterações novas.

## Correções mantidas

- Usa o banco antigo cheio: `/data/oficina.db`
- Usa o volume correto: `mecanica-jairo-data:/data`
- Sem `ports`, usa `expose: 8080` para não conflitar porta no servidor
- Migração SQLite corrigida, sem `DEFAULT CURRENT_TIMESTAMP`
- Gunicorn com 1 worker para evitar dois processos migrando o SQLite ao mesmo tempo

## Visual ajustado

A aba Cadastro/OS foi deixada igual ao programa desktop antigo:

- Cliente: Nome, Telefone, Puxar cadastro (F2)
- Veículo: Marca, Modelo, Placa, Ano, KM e Correia
- Serviço com abas Descrição / Itens do serviço
- Aba Itens com Buscar no estoque, Adicionar item, tabela e mão de obra
- Botões finais: Salvar cadastro + serviço, Excluir por placa e Limpar

## Antes do redeploy

Faça backup no terminal do Coolify:

```bash
cp /data/oficina.db /data/oficina.db.backup_antes_layout_cadastro_exato
```

## Depois de subir no GitHub

No Coolify:

1. Save
2. Reload Compose File
3. Force Redeploy / No Cache

Depois confirme no terminal:

```bash
grep -n "LAYOUT_CADASTRO_DESKTOP_EXATO" /app/app.py
grep -n "DEFAULT CURRENT_TIMESTAMP" /app/app.py
```

O primeiro comando precisa aparecer. O segundo não deve retornar nada.
