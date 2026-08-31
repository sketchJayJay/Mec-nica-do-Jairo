CORREÇÃO - Cannot add a column with non-constant default

O erro vinha do SQLite ao tentar adicionar coluna em banco antigo usando:
TEXT DEFAULT CURRENT_TIMESTAMP

SQLite não permite esse tipo de DEFAULT em ALTER TABLE ADD COLUMN quando a tabela já existe.

Correção aplicada:
- colunas created_at adicionadas como TEXT simples durante migração
- depois o sistema preenche os registros vazios com a data/hora atual
- mantém DB_PATH=/data/oficina.db
- mantém volume antigo mecanica-jairo-data:/data

Antes de subir, faça backup no terminal do Coolify:
cp /data/oficina.db /data/oficina.db.backup_antes_correcao_default_timestamp

Depois suba no GitHub, Reload Compose File e Force Redeploy.
