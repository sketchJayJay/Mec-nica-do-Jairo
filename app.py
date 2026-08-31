# SISTEMA_TODO_COMPACTO_20260831
# CADASTRO_AREAS_MENORES_20260831
# VOLTA_IMPRESSAO_OS_PARTE_DE_BAIXO_20260831
# VOLTA_IMPRESSAO_OS_20260831
# REMOVE_CABECALHO_RODAPE_BROWSER_IMPRESSAO_OS_20260831
# RESTAURA_MODELO_ANTIGO_IMPRESSAO_OS_20260831
# CORRIGE_BUSCA_ITEM_PAROU_20260831
# EXCLUIR_ITEM_LINHA_EDITAR_OS_20260831
# REMOVER_ITEM_SELECIONADO_20260831
# FLUXO_SELECIONAR_QTD_ADICIONAR_20260831
# BOTAO_ADICIONAR_ITEM_MODAL_20260831
# BUSCA_ESTOQUE_MODAL_TOPO_FUNCIONANDO_20260831
# BUSCA_ESTOQUE_MAIS_VISIVEL_20260831
# BOTAO_SALVAR_CADASTRO_E_BUSCA_ESTOQUE_COMPLETA_20260831
# BOTAO_SALVAR_EDICAO_OS_20260831
# EDITAR_OS_SEM_SOBREPOR_20260831
# CADASTRO_ANTIGO_REAL_AJUSTE_ALINHAMENTO_20260831
# CADASTRO_ANTIGO_REAL_SEM_IMAGEM_20260831
# -*- coding: utf-8 -*-
import os
import sqlite3
import unicodedata
from datetime import datetime
from decimal import Decimal, InvalidOperation
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort

from catalogos import BRANDS, CATALOGO, ESTOQUE_BASICO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data"))
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.environ.get("DB_PATH", os.path.join(DATA_DIR, "jairo_oficina.db"))

print("FIX_DEFAULT_TIMESTAMP_HARD_20260831_1618")
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "jairo-oficina-local")
app.config["JSON_AS_ASCII"] = False


def connect_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    con.execute("PRAGMA journal_mode = WAL;")
    con.execute("PRAGMA synchronous = NORMAL;")
    return con


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_br():
    return datetime.now().strftime("%d/%m/%Y")


def parse_money(value, default=0):
    if value is None:
        return float(default)
    s = str(value).strip().replace("R$", "").replace(" ", "")
    if not s:
        return float(default)
    # aceita 1.234,56 ou 1234.56
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(Decimal(s))
    except (InvalidOperation, ValueError):
        return float(default)


def parse_number(value, default=0):
    if value is None:
        return default
    s = str(value).strip().replace(".", "").replace(",", ".")
    if not s:
        return default
    try:
        n = float(s)
        if n.is_integer():
            return int(n)
        return n
    except ValueError:
        return default


def br_money(value):
    try:
        n = float(value or 0)
    except Exception:
        n = 0
    return f"R$ {n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def br_int(value):
    try:
        return f"{int(value or 0):,}".replace(",", ".")
    except Exception:
        return "0"


def norm_text(s):
    s = (s or "").strip().lower()
    s = "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch))
    keep = []
    for ch in s:
        keep.append(ch if ch.isalnum() else " ")
    return " ".join("".join(keep).split())


def tokens(s):
    stop = {"de", "do", "da", "dos", "das", "para", "e", "ou", "a", "o"}
    out = []
    for t in norm_text(s).split():
        if len(t) > 3 and t.endswith("s"):
            t = t[:-1]
        if t not in stop:
            out.append(t)
    return out


def find_estoque_match(con, item_name, categoria=None):
    item_name = (item_name or "").strip()
    if not item_name:
        return None
    key = norm_text(item_name)
    key_tokens = set(tokens(item_name))

    def pick(rows):
        for r in rows:
            if norm_text(r["item"]) == key:
                return r
        for r in rows:
            n = norm_text(r["item"])
            if n.startswith(key) or key in n:
                return r
        for r in rows:
            cand = set(tokens(r["item"]))
            if key_tokens and key_tokens.issubset(cand):
                return r
        for r in rows:
            cand = set(tokens(r["item"]))
            if cand and cand.issubset(key_tokens):
                return r
        return None

    cur = con.cursor()
    if categoria:
        cur.execute("SELECT * FROM estoque WHERE categoria = ? ORDER BY item", (categoria,))
        row = pick(cur.fetchall())
        if row:
            return row
    cur.execute("SELECT * FROM estoque ORDER BY item")
    return pick(cur.fetchall())


def ensure_db():
    with connect_db() as con:
        cur = con.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone TEXT,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS veiculos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                marca TEXT,
                modelo TEXT,
                placa TEXT UNIQUE,
                ano TEXT,
                km_atual REAL DEFAULT 0,
                km_troca_corr REAL DEFAULT 0,
                km_corr_trocada REAL DEFAULT 0,
                km_corr_proxima REAL DEFAULT 0,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS servicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                veiculo_id INTEGER NOT NULL,
                descricao TEXT,
                km_atual REAL DEFAULT 0,
                intervalo_km REAL DEFAULT 10000,
                proxima_manut_km REAL DEFAULT 0,
                km_troca_corr REAL DEFAULT 0,
                km_corr_trocada REAL DEFAULT 0,
                km_corr_proxima REAL DEFAULT 0,
                data TEXT,
                observacoes TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (veiculo_id) REFERENCES veiculos(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS itens_servico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                servico_id INTEGER NOT NULL,
                categoria TEXT,
                item TEXT NOT NULL,
                qtde REAL DEFAULT 1,
                valor_unit REAL DEFAULT 0,
                baixa_estoque INTEGER DEFAULT 1,
                estoque_id INTEGER,
                FOREIGN KEY (servico_id) REFERENCES servicos(id) ON DELETE CASCADE,
                FOREIGN KEY (estoque_id) REFERENCES estoque(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                categoria TEXT,
                qtde REAL DEFAULT 0,
                preco REAL DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS estoque_movimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                servico_id INTEGER,
                estoque_id INTEGER,
                item TEXT,
                categoria TEXT,
                qtde REAL DEFAULT 0,
                tipo TEXT NOT NULL,
                created_at TEXT,
                FOREIGN KEY (servico_id) REFERENCES servicos(id) ON DELETE CASCADE,
                FOREIGN KEY (estoque_id) REFERENCES estoque(id) ON DELETE SET NULL
            );
            """
        )
        # migrações simples caso suba em banco antigo.
        # O banco antigo do Jairo já tinha clientes/OS/estoque, mas algumas colunas
        # novas do layout web não existiam. Sem isso aparece erro tipo:
        # "no such column: updated_at".
        migrations = [
            ("clientes", "telefone", "TEXT"),
            ("clientes", "created_at", "TEXT"),
            ("clientes", "updated_at", "TEXT"),

            ("veiculos", "marca", "TEXT"),
            ("veiculos", "modelo", "TEXT"),
            ("veiculos", "placa", "TEXT"),
            ("veiculos", "ano", "TEXT"),
            ("veiculos", "km_atual", "REAL DEFAULT 0"),
            ("veiculos", "km_troca_corr", "REAL DEFAULT 0"),
            ("veiculos", "km_corr_trocada", "REAL DEFAULT 0"),
            ("veiculos", "km_corr_proxima", "REAL DEFAULT 0"),
            ("veiculos", "created_at", "TEXT"),
            ("veiculos", "updated_at", "TEXT"),

            ("servicos", "descricao", "TEXT"),
            ("servicos", "km_atual", "REAL DEFAULT 0"),
            ("servicos", "intervalo_km", "REAL DEFAULT 10000"),
            ("servicos", "proxima_manut_km", "REAL DEFAULT 0"),
            ("servicos", "km_troca_corr", "REAL DEFAULT 0"),
            ("servicos", "km_corr_trocada", "REAL DEFAULT 0"),
            ("servicos", "km_corr_proxima", "REAL DEFAULT 0"),
            ("servicos", "data", "TEXT"),
            ("servicos", "observacoes", "TEXT"),
            ("servicos", "created_at", "TEXT"),
            ("servicos", "updated_at", "TEXT"),

            ("itens_servico", "categoria", "TEXT"),
            ("itens_servico", "qtde", "REAL DEFAULT 1"),
            ("itens_servico", "valor_unit", "REAL DEFAULT 0"),
            ("itens_servico", "baixa_estoque", "INTEGER DEFAULT 1"),
            ("itens_servico", "estoque_id", "INTEGER"),

            ("estoque", "categoria", "TEXT"),
            ("estoque", "qtde", "REAL DEFAULT 0"),
            ("estoque", "preco", "REAL DEFAULT 0"),
            ("estoque", "created_at", "TEXT"),
            ("estoque", "updated_at", "TEXT"),

            ("estoque_movimentos", "servico_id", "INTEGER"),
            ("estoque_movimentos", "estoque_id", "INTEGER"),
            ("estoque_movimentos", "item", "TEXT"),
            ("estoque_movimentos", "categoria", "TEXT"),
            ("estoque_movimentos", "qtde", "REAL DEFAULT 0"),
            ("estoque_movimentos", "tipo", "TEXT DEFAULT 'baixa'"),
            ("estoque_movimentos", "created_at", "TEXT"),
        ]
        for table, col, spec in migrations:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not cur.fetchone():
                continue
            cur.execute(f"PRAGMA table_info({table})")
            cols = [r[1] for r in cur.fetchall()]
            if col not in cols:
                # Migração defensiva: SQLite não permite DEFAULT dinâmico em ADD COLUMN.
                # Também evita derrubar o sistema se dois workers tentarem migrar juntos.
                safe_spec = spec.replace("DEFAULT CURRENT_TIMESTAMP", "").strip()
                try:
                    cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {safe_spec}")
                except sqlite3.OperationalError as e:
                    msg = str(e).lower()
                    if "duplicate column" in msg:
                        pass
                    elif "non-constant default" in msg:
                        cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} TEXT")
                    else:
                        raise

        for table in ("clientes", "veiculos", "servicos", "estoque", "estoque_movimentos"):
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not cur.fetchone():
                continue
            cur.execute(f"PRAGMA table_info({table})")
            cols = [r[1] for r in cur.fetchall()]
            if "created_at" in cols:
                cur.execute(f"UPDATE {table} SET created_at = ? WHERE created_at IS NULL OR created_at = ''", (now_str(),))
        con.commit()

        cur.execute("SELECT COUNT(*) AS total FROM estoque")
        if cur.fetchone()["total"] == 0:
            cur.executemany(
                "INSERT INTO estoque (item, categoria, qtde, preco) VALUES (?, ?, ?, ?)",
                [(i, c, q, p) for i, c, q, p in ESTOQUE_BASICO],
            )
            con.commit()


@app.context_processor
def template_utils():
    return {"br_money": br_money, "br_int": br_int, "today_br": today_br}


def get_or_404(con, query, params=()):
    row = con.execute(query, params).fetchone()
    if not row:
        abort(404)
    return row


def upsert_cliente(con, nome, telefone):
    nome = (nome or "").strip()
    telefone = (telefone or "").strip()
    row = con.execute(
        "SELECT id FROM clientes WHERE nome = ? AND IFNULL(telefone,'') = IFNULL(?, '') LIMIT 1",
        (nome, telefone),
    ).fetchone()
    if row:
        return row["id"]
    cur = con.execute("INSERT INTO clientes (nome, telefone) VALUES (?, ?)", (nome, telefone))
    return cur.lastrowid


def upsert_veiculo(con, cliente_id, marca, modelo, placa, ano, km_atual, km_troca_corr, km_corr_trocada, km_corr_proxima):
    marca = (marca or "").strip()
    modelo = (modelo or "").strip()
    placa = (placa or "").strip().upper() or None
    ano = (ano or "").strip()
    row = None
    if placa:
        row = con.execute("SELECT id FROM veiculos WHERE placa = ? LIMIT 1", (placa,)).fetchone()
    if row:
        con.execute(
            """UPDATE veiculos
               SET cliente_id=?, marca=?, modelo=?, ano=?, km_atual=?, km_troca_corr=?, km_corr_trocada=?, km_corr_proxima=?, updated_at=?
               WHERE id=?""",
            (cliente_id, marca, modelo, ano, km_atual, km_troca_corr, km_corr_trocada, km_corr_proxima, now_str(), row["id"]),
        )
        return row["id"]
    cur = con.execute(
        """INSERT INTO veiculos
           (cliente_id, marca, modelo, placa, ano, km_atual, km_troca_corr, km_corr_trocada, km_corr_proxima)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (cliente_id, marca, modelo, placa, ano, km_atual, km_troca_corr, km_corr_trocada, km_corr_proxima),
    )
    return cur.lastrowid


def reverse_stock_movements(con, servico_id):
    rows = con.execute("SELECT * FROM estoque_movimentos WHERE servico_id = ? AND tipo = 'baixa'", (servico_id,)).fetchall()
    for r in rows:
        if r["estoque_id"]:
            con.execute("UPDATE estoque SET qtde = qtde + ?, updated_at=? WHERE id = ?", (r["qtde"] or 0, now_str(), r["estoque_id"]))
    con.execute("DELETE FROM estoque_movimentos WHERE servico_id = ?", (servico_id,))


def apply_stock_for_items(con, servico_id, items):
    avisos = []
    for it in items:
        if int(it.get("baixa_estoque", 1)) != 1:
            continue
        categoria = (it.get("categoria") or "").strip()
        item = (it.get("item") or "").strip()
        if not item or categoria.lower() in {"mão de obra", "mao de obra", "serviço", "servico"}:
            continue
        qtde = float(it.get("qtde") or 0)
        if qtde <= 0:
            continue
        est = find_estoque_match(con, item, categoria)
        if not est:
            avisos.append(f"Item '{item}' não encontrado no estoque. A OS foi salva, mas ele não teve baixa automática.")
            continue
        atual = float(est["qtde"] or 0)
        if atual < qtde:
            avisos.append(f"Estoque baixo para '{est['item']}': tinha {br_int(atual)} e precisava {br_int(qtde)}. A baixa não foi feita.")
            continue
        con.execute("UPDATE estoque SET qtde = qtde - ?, updated_at=? WHERE id = ?", (qtde, now_str(), est["id"]))
        con.execute(
            "INSERT INTO estoque_movimentos (servico_id, estoque_id, item, categoria, qtde, tipo) VALUES (?, ?, ?, ?, ?, 'baixa')",
            (servico_id, est["id"], est["item"], est["categoria"], qtde),
        )
    return avisos


def parse_items_form(form):
    nomes = form.getlist("item_nome[]")
    cats = form.getlist("item_categoria[]")
    qtdes = form.getlist("item_qtde[]")
    vals = form.getlist("item_valor[]")
    baixa = form.getlist("item_baixa[]")
    items = []
    for i, nome in enumerate(nomes):
        nome = (nome or "").strip()
        if not nome:
            continue
        cat = cats[i] if i < len(cats) else "Outros"
        qtd = parse_number(qtdes[i] if i < len(qtdes) else 1, 1)
        val = parse_money(vals[i] if i < len(vals) else 0, 0)
        bx = baixa[i] if i < len(baixa) else "1"
        items.append({
            "categoria": (cat or "Outros").strip(),
            "item": nome,
            "qtde": float(qtd or 0),
            "valor_unit": float(val or 0),
            "baixa_estoque": 0 if str(bx) == "0" else 1,
        })
    return items


def save_os_from_form(form, servico_id=None):
    nome = (form.get("nome") or "").strip()
    if not nome:
        raise ValueError("Informe o nome do cliente.")
    telefone = (form.get("telefone") or "").strip()
    marca = (form.get("marca") or "").strip()
    modelo = (form.get("modelo") or "").strip()
    placa = (form.get("placa") or "").strip().upper()
    ano = (form.get("ano") or "").strip()
    km_atual = parse_number(form.get("km_atual"), 0)
    intervalo_km = parse_number(form.get("intervalo_km"), 10000)
    proxima_km = parse_number(form.get("proxima_manut_km"), 0)
    km_troca_corr = parse_number(form.get("km_troca_corr"), 0)
    km_corr_trocada = parse_number(form.get("km_corr_trocada"), 0)
    km_corr_proxima = parse_number(form.get("km_corr_proxima"), 0)
    data = (form.get("data") or today_br()).strip()
    descricao = (form.get("descricao") or "").strip()
    observacoes = (form.get("observacoes") or "").strip()
    items = parse_items_form(form)

    with connect_db() as con:
        cli_id = upsert_cliente(con, nome, telefone)
        vei_id = upsert_veiculo(con, cli_id, marca, modelo, placa, ano, km_atual, km_troca_corr, km_corr_trocada, km_corr_proxima)
        if servico_id:
            get_or_404(con, "SELECT id FROM servicos WHERE id = ?", (servico_id,))
            reverse_stock_movements(con, servico_id)
            con.execute(
                """UPDATE servicos
                   SET veiculo_id=?, descricao=?, km_atual=?, intervalo_km=?, proxima_manut_km=?,
                       km_troca_corr=?, km_corr_trocada=?, km_corr_proxima=?, data=?, observacoes=?, updated_at=?
                   WHERE id=?""",
                (vei_id, descricao, km_atual, intervalo_km, proxima_km, km_troca_corr, km_corr_trocada, km_corr_proxima, data, observacoes, now_str(), servico_id),
            )
            con.execute("DELETE FROM itens_servico WHERE servico_id = ?", (servico_id,))
            sid = servico_id
        else:
            cur = con.execute(
                """INSERT INTO servicos
                   (veiculo_id, descricao, km_atual, intervalo_km, proxima_manut_km, km_troca_corr, km_corr_trocada, km_corr_proxima, data, observacoes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (vei_id, descricao, km_atual, intervalo_km, proxima_km, km_troca_corr, km_corr_trocada, km_corr_proxima, data, observacoes),
            )
            sid = cur.lastrowid
        for it in items:
            est = find_estoque_match(con, it["item"], it["categoria"])
            estoque_id = est["id"] if est else None
            con.execute(
                """INSERT INTO itens_servico
                   (servico_id, categoria, item, qtde, valor_unit, baixa_estoque, estoque_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (sid, it["categoria"], it["item"], it["qtde"], it["valor_unit"], it["baixa_estoque"], estoque_id),
            )
            # se preço foi preenchido para uma peça existente, atualiza o preço do estoque sem alterar qtde
            if estoque_id and it["valor_unit"] >= 0 and it["categoria"].lower() not in {"mão de obra", "mao de obra"}:
                con.execute("UPDATE estoque SET preco=?, updated_at=? WHERE id=?", (it["valor_unit"], now_str(), estoque_id))
        avisos = apply_stock_for_items(con, sid, items)
        con.commit()
        return sid, avisos


def load_os(con, sid):
    servico = get_or_404(
        con,
        """SELECT s.*, v.marca, v.modelo, v.placa, v.ano, v.km_atual AS km_veiculo,
                  c.nome, c.telefone, c.id AS cliente_id, v.id AS veiculo_id
           FROM servicos s
           JOIN veiculos v ON v.id = s.veiculo_id
           JOIN clientes c ON c.id = v.cliente_id
           WHERE s.id = ?""",
        (sid,),
    )
    itens = con.execute("SELECT * FROM itens_servico WHERE servico_id = ? ORDER BY id", (sid,)).fetchall()
    total = sum(float(i["qtde"] or 0) * float(i["valor_unit"] or 0) for i in itens)
    return servico, itens, total


@app.route("/")
def index():
    with connect_db() as con:
        total_os = con.execute("SELECT COUNT(*) AS n FROM servicos").fetchone()["n"]
        total_clientes = con.execute("SELECT COUNT(*) AS n FROM clientes").fetchone()["n"]
        estoque_baixo = con.execute("SELECT COUNT(*) AS n FROM estoque WHERE qtde <= 1").fetchone()["n"]
        ultimas = con.execute(
            """SELECT s.id, s.data, c.nome, v.marca, v.modelo, v.placa,
                      COALESCE(SUM(i.qtde * i.valor_unit), 0) AS total
               FROM servicos s
               JOIN veiculos v ON v.id=s.veiculo_id
               JOIN clientes c ON c.id=v.cliente_id
               LEFT JOIN itens_servico i ON i.servico_id=s.id
               GROUP BY s.id
               ORDER BY s.id DESC LIMIT 8"""
        ).fetchall()
    return render_template("index.html", total_os=total_os, total_clientes=total_clientes, estoque_baixo=estoque_baixo, ultimas=ultimas)


@app.route("/nova", methods=["GET", "POST"])
def nova_os():
    if request.method == "POST":
        try:
            sid, avisos = save_os_from_form(request.form)
            flash(f"OS #{sid} salva com sucesso.", "success")
            for a in avisos:
                flash(a, "warning")
            return redirect(url_for("ver_os", sid=sid))
        except Exception as e:
            flash(str(e), "danger")
    return render_template("form_os.html", brands=BRANDS, catalogo=CATALOGO, os=None, itens=[], title="Nova OS / Nota")


@app.route("/os")
def listar_os():
    q = (request.args.get("q") or "").strip()
    params = []
    where = ""
    if q:
        where = "WHERE c.nome LIKE ? OR IFNULL(v.placa,'') LIKE ? OR IFNULL(v.modelo,'') LIKE ?"
        like = f"%{q}%"
        params = [like, like.upper(), like]
    with connect_db() as con:
        rows = con.execute(
            f"""SELECT s.id, s.data, c.nome, c.telefone, v.marca, v.modelo, v.placa, s.km_atual, s.proxima_manut_km,
                       COALESCE(SUM(i.qtde * i.valor_unit), 0) AS total
                FROM servicos s
                JOIN veiculos v ON v.id=s.veiculo_id
                JOIN clientes c ON c.id=v.cliente_id
                LEFT JOIN itens_servico i ON i.servico_id=s.id
                {where}
                GROUP BY s.id
                ORDER BY s.id DESC
                LIMIT 200""",
            params,
        ).fetchall()
    return render_template("listar_os.html", rows=rows, q=q)


@app.route("/os/<int:sid>")
def ver_os(sid):
    with connect_db() as con:
        servico, itens, total = load_os(con, sid)
    return render_template("ver_os.html", os=servico, itens=itens, total=total)


@app.route("/os/<int:sid>/editar", methods=["GET", "POST"])
def editar_os(sid):
    if request.method == "POST":
        try:
            sid, avisos = save_os_from_form(request.form, servico_id=sid)
            flash(f"OS #{sid} atualizada sem dar baixa dupla no estoque.", "success")
            for a in avisos:
                flash(a, "warning")
            return redirect(url_for("ver_os", sid=sid))
        except Exception as e:
            flash(str(e), "danger")
    with connect_db() as con:
        servico, itens, total = load_os(con, sid)
    return render_template("form_os.html", brands=BRANDS, catalogo=CATALOGO, os=servico, itens=itens, title=f"Editar OS #{sid}")


# EXCLUIR_NOTA_LISTA_OS_20260831
@app.post("/os/<int:sid>/excluir")
def excluir_os(sid):
    with connect_db() as con:
        reverse_stock_movements(con, sid)
        con.execute("DELETE FROM servicos WHERE id = ?", (sid,))
        con.commit()
    flash(f"OS #{sid} excluída e estoque revertido.", "success")
    return redirect(url_for("listar_os"))


@app.route("/os/<int:sid>/imprimir")
def imprimir_os(sid):
    with connect_db() as con:
        servico, itens, total = load_os(con, sid)
    return render_template("print_os.html", os=servico, itens=itens, total=total)


@app.route("/estoque", methods=["GET", "POST"])
def estoque():
    if request.method == "POST":
        item = (request.form.get("item") or "").strip()
        categoria = (request.form.get("categoria") or "Outros").strip()
        qtde = parse_number(request.form.get("qtde"), 0)
        preco = parse_money(request.form.get("preco"), 0)
        if not item:
            flash("Informe o nome do item.", "danger")
        else:
            with connect_db() as con:
                con.execute("INSERT INTO estoque (item, categoria, qtde, preco) VALUES (?, ?, ?, ?)", (item, categoria, qtde, preco))
                con.commit()
            flash("Item adicionado ao estoque.", "success")
        return redirect(url_for("estoque"))

    q = (request.args.get("q") or "").strip()
    params = []
    where = ""
    if q:
        where = "WHERE item LIKE ? OR categoria LIKE ?"
        params = [f"%{q}%", f"%{q}%"]
    with connect_db() as con:
        rows = con.execute(f"SELECT * FROM estoque {where} ORDER BY categoria, item LIMIT 700", params).fetchall()
        cats = con.execute("SELECT DISTINCT categoria FROM estoque ORDER BY categoria").fetchall()
    return render_template("estoque.html", rows=rows, cats=[c["categoria"] for c in cats], q=q)


@app.route("/estoque/<int:eid>/editar", methods=["GET", "POST"])
def editar_estoque(eid):
    with connect_db() as con:
        item = get_or_404(con, "SELECT * FROM estoque WHERE id = ?", (eid,))
        if request.method == "POST":
            con.execute(
                "UPDATE estoque SET item=?, categoria=?, qtde=?, preco=?, updated_at=? WHERE id=?",
                ((request.form.get("item") or "").strip(), (request.form.get("categoria") or "Outros").strip(), parse_number(request.form.get("qtde"), 0), parse_money(request.form.get("preco"), 0), now_str(), eid),
            )
            con.commit()
            flash("Item do estoque atualizado.", "success")
            return redirect(url_for("estoque", q=request.form.get("item", "")))
    return render_template("editar_estoque.html", item=item)


@app.post("/estoque/<int:eid>/excluir")
def excluir_estoque(eid):
    with connect_db() as con:
        con.execute("DELETE FROM estoque WHERE id = ?", (eid,))
        con.commit()
    flash("Item excluído do estoque.", "success")
    return redirect(url_for("estoque"))


@app.route("/estoque/imprimir")
def imprimir_estoque():
    q = (request.args.get("q") or "").strip()
    params = []
    where = ""
    if q:
        where = "WHERE item LIKE ? OR categoria LIKE ?"
        params = [f"%{q}%", f"%{q}%"]
    with connect_db() as con:
        rows = con.execute(f"SELECT * FROM estoque {where} ORDER BY categoria, item", params).fetchall()
    return render_template("print_estoque.html", rows=rows, q=q)


@app.route("/relatorios")
def relatorios():
    with connect_db() as con:
        resumo = con.execute(
            """SELECT COUNT(DISTINCT s.id) AS total_os,
                      COUNT(DISTINCT c.id) AS clientes,
                      COALESCE(SUM(i.qtde * i.valor_unit), 0) AS faturamento
               FROM servicos s
               JOIN veiculos v ON v.id=s.veiculo_id
               JOIN clientes c ON c.id=v.cliente_id
               LEFT JOIN itens_servico i ON i.servico_id=s.id"""
        ).fetchone()
        baixo = con.execute("SELECT * FROM estoque WHERE qtde <= 1 ORDER BY qtde ASC, item LIMIT 50").fetchall()
        top = con.execute(
            """SELECT item, categoria, SUM(qtde) AS qtde, SUM(qtde*valor_unit) AS total
               FROM itens_servico
               GROUP BY item, categoria
               ORDER BY total DESC LIMIT 20"""
        ).fetchall()
    return render_template("relatorios.html", resumo=resumo, baixo=baixo, top=top)


@app.route("/api/modelos/<path:marca>")
def api_modelos(marca):
    return jsonify(BRANDS.get(marca, BRANDS.get("Outros", [])))


@app.route("/api/estoque")
def api_estoque():
    # BUSCA_ESTOQUE_MODAL_TOPO_FUNCIONANDO_20260831
    q = (request.args.get("q") or "").strip()

    def norm(s):
        s = str(s or "")
        s = unicodedata.normalize("NFD", s)
        s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
        return s.casefold().strip()

    nq = norm(q)
    tokens = [t for t in nq.split() if t]

    with connect_db() as con:
        rows = con.execute(
            """SELECT id, item, categoria, qtde, preco
               FROM estoque
               ORDER BY categoria COLLATE NOCASE, item COLLATE NOCASE"""
        ).fetchall()

    data = [dict(r) for r in rows]

    if tokens:
        scored = []
        for r in data:
            item_n = norm(r.get("item", ""))
            cat_n = norm(r.get("categoria", ""))
            hay = f"{item_n} {cat_n}"
            if all(t in hay for t in tokens):
                score = 0
                if item_n.startswith(nq): score += 100
                if nq in item_n: score += 50
                if cat_n.startswith(nq): score += 25
                if nq in cat_n: score += 15
                score += max(0, 10 - len(item_n)//12)
                scored.append((score, r))
        scored.sort(key=lambda x: (-x[0], norm(x[1].get("categoria", "")), norm(x[1].get("item", ""))))
        data = [r for _, r in scored]

    return jsonify(data[:300])


@app.route("/api/clientes")
def api_clientes():
    q = (request.args.get("q") or "").strip()
    like = f"%{q}%"
    with connect_db() as con:
        rows = con.execute(
            """SELECT c.id AS cliente_id, c.nome, c.telefone, v.id AS veiculo_id, v.marca, v.modelo, v.placa, v.ano, v.km_atual,
                      v.km_troca_corr, v.km_corr_trocada, v.km_corr_proxima
               FROM clientes c
               LEFT JOIN veiculos v ON v.cliente_id=c.id
               WHERE ?='' OR c.nome LIKE ? OR IFNULL(c.telefone,'') LIKE ? OR IFNULL(v.placa,'') LIKE ?
               ORDER BY c.nome, v.id DESC LIMIT 30""",
            (q, like, like, like.upper()),
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404


ensure_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)
