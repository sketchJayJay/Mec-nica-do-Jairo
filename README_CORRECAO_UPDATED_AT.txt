CORREÇÃO - no such column: updated_at

Esta versão mantém o banco antigo em:
/data/oficina.db

E adiciona automaticamente as colunas novas que podem faltar no banco antigo, incluindo updated_at.

IMPORTANTE:
- Não apague nenhum volume.
- Faça backup antes do redeploy:
  cp /data/oficina.db /data/oficina.db.backup_antes_updated_at
- Suba estes arquivos no GitHub.
- No Coolify: Save > Reload Compose File > Force Redeploy.
