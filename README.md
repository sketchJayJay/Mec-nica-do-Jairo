# Mecânica do Jairo - Cadastro antigo real sem imagem

Versão Coolify corrigida para a tela Cadastro/OS.

Marcador: CADASTRO_ANTIGO_REAL_SEM_IMAGEM_20260831

Correções principais:
- Remove completamente o print/imagem de fundo da tela de cadastro.
- Campos e botões são elementos HTML reais, então os cliques ficam no lugar certo.
- Mantém banco antigo em `/data/oficina.db`.
- Mantém volume `mecanica-jairo-data:/data`.
- Mantém correção SQLite/Gunicorn.

Antes de redeploy:
```bash
cp /data/oficina.db /data/oficina.db.backup_antes_cadastro_sem_imagem
```

Depois do deploy, confira:
```bash
grep -n "CADASTRO_ANTIGO_REAL_SEM_IMAGEM_20260831" /app/app.py /app/templates/form_os.html
```


Versão: CADASTRO_ANTIGO_AJUSTE_SERVICO_GRID_20260831
