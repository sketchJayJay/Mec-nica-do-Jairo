# Jairo Oficina Web - Cadastro/OS no visual desktop antigo

Pacote para Coolify mantendo:
- Banco antigo: `/data/oficina.db`
- Volume: `mecanica-jairo-data:/data`
- Correção SQLite sem `DEFAULT CURRENT_TIMESTAMP`
- Gunicorn com 1 worker
- Aba Cadastro/OS remodelada para ficar no mesmo desenho do programa desktop antigo.

## Conferência após deploy
No terminal do Coolify:

```bash
grep -n "LAYOUT_CADASTRO_PIXEL_DESKTOP" /app/app.py /app/static/style.css
```

Tem que aparecer:

```txt
LAYOUT_CADASTRO_PIXEL_DESKTOP_20260831_1735
```

## Backup antes do redeploy

```bash
cp /data/oficina.db /data/oficina.db.backup_antes_layout_pixel_desktop
```
