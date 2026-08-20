from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parent
required = [
    'app.py','db.py','requirements.txt','Dockerfile','docker-compose.yaml','entrypoint.sh',
    'seed/oficina.db','templates/base.html','templates/os_form.html','templates/estoque.html',
    'static/css/app.css','static/js/os_form.js','static/img/logo.png'
]
missing = [x for x in required if not (ROOT/x).exists()]
if missing:
    print('ERRO - arquivos ausentes:')
    for x in missing: print(' -', x)
    sys.exit(1)

con = sqlite3.connect(ROOT/'seed/oficina.db')
try:
    integrity = con.execute('PRAGMA integrity_check').fetchone()[0]
    counts = {t: con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
              for t in ['clientes','veiculos','servicos','itens_servico','estoque']}
finally:
    con.close()

print('Projeto: OK')
print('Banco:', integrity)
for k,v in counts.items(): print(f'{k}: {v}')
if integrity != 'ok': sys.exit(2)
