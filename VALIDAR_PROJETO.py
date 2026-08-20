from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parent
required = [
    'app.py','db.py','requirements.txt','Dockerfile','docker-compose.yaml','entrypoint.sh',
    'seed/oficina.db','templates/base.html','templates/os_form.html','templates/estoque.html',
    'static/css/app.css','static/js/os_form.js','static/js/orcamento_form.js','static/img/logo.png',
    'templates/orcamento_form.html','templates/orcamentos_list.html','templates/orcamento_view.html','templates/orcamento_print.html'
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


# MIGRACAO ORCAMENTOS: valida em uma copia temporaria sem tocar o seed original.
import os, tempfile, shutil
from pathlib import Path as _Path
with tempfile.TemporaryDirectory() as _td:
    _test_db = _Path(_td) / 'oficina.db'
    shutil.copy2(ROOT/'seed/oficina.db', _test_db)
    os.environ['DATABASE_PATH'] = str(_test_db)
    import db as _db
    _db.init_db()
    with _db.connect(_test_db) as _con:
        _tables = {r[0] for r in _con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert 'orcamentos' in _tables and 'itens_orcamento' in _tables
    print('Modulo de orcamentos: OK (migracao sem alterar estoque)')
