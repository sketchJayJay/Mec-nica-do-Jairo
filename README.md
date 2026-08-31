# Mecânica do Jairo - correção dura SQLite

Correção para o erro:

`sqlite3.OperationalError: Cannot add a column with non-constant default`

Também mantém o banco antigo em `/data/oficina.db` e o volume `mecanica-jairo-data:/data`.

Antes do redeploy, faça backup no terminal:

```bash
cp /data/oficina.db /data/oficina.db.backup_antes_fix_hard
```

Depois suba estes arquivos no GitHub, substituindo os antigos, e no Coolify use Reload Compose File + Force Redeploy/No Cache.

Verificação após subir:

```bash
grep -n "DEFAULT CURRENT_TIMESTAMP" /app/app.py || echo OK_SEM_DEFAULT
grep -n "FIX_DEFAULT_TIMESTAMP_HARD" /app/app.py
```
