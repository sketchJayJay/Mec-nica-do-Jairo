from __future__ import annotations

import os
import shutil
import sqlite3
import unicodedata
import re
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterable

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB = BASE_DIR / "data" / "oficina.db"
SEED_DB = BASE_DIR / "seed" / "oficina.db"


def db_path() -> Path:
    return Path(os.environ.get("DATABASE_PATH", str(DEFAULT_DB))).expanduser().resolve()


def ensure_database_file() -> Path:
    target = db_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        if SEED_DB.exists():
            shutil.copy2(SEED_DB, target)
        else:
            sqlite3.connect(target).close()
    return target


def connect(path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(path) if path else ensure_database_file()
    con = sqlite3.connect(str(path), timeout=20)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    con.execute("PRAGMA busy_timeout=10000")
    return con


@contextmanager
def transaction():
    con = connect()
    try:
        con.execute("BEGIN IMMEDIATE")
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def column_names(con: sqlite3.Connection, table: str) -> set[str]:
    return {r[1] for r in con.execute(f"PRAGMA table_info({table})").fetchall()}


def _backup_before_web_migration(target: Path) -> None:
    marker = target.with_suffix(target.suffix + ".pre-web-v2.bak")
    if target.exists() and not marker.exists():
        source = sqlite3.connect(str(target))
        dest = sqlite3.connect(str(marker))
        try:
            source.backup(dest)
        finally:
            dest.close()
            source.close()


def init_db() -> None:
    target = ensure_database_file()
    _backup_before_web_migration(target)
    with connect(target) as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone TEXT
            );
            CREATE TABLE IF NOT EXISTS veiculos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                marca TEXT,
                modelo TEXT,
                placa TEXT UNIQUE,
                ano TEXT,
                km_atual INTEGER DEFAULT 0,
                km_troca_corr INTEGER DEFAULT 0,
                km_corr_trocada INTEGER DEFAULT 0,
                km_corr_proxima INTEGER DEFAULT 0,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            );
            CREATE TABLE IF NOT EXISTS servicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                veiculo_id INTEGER NOT NULL,
                descricao TEXT,
                km_atual INTEGER DEFAULT 0,
                intervalo_km INTEGER DEFAULT 10000,
                proxima_manut_km INTEGER DEFAULT 0,
                data TEXT,
                FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)
            );
            CREATE TABLE IF NOT EXISTS itens_servico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                servico_id INTEGER NOT NULL,
                categoria TEXT,
                item TEXT NOT NULL,
                qtde INTEGER DEFAULT 1,
                valor_unit REAL DEFAULT 0,
                FOREIGN KEY (servico_id) REFERENCES servicos(id)
            );
            CREATE TABLE IF NOT EXISTS estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                categoria TEXT,
                qtde INTEGER DEFAULT 0,
                preco REAL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS movimentos_estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estoque_id INTEGER,
                servico_id INTEGER,
                tipo TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                saldo_antes INTEGER NOT NULL,
                saldo_depois INTEGER NOT NULL,
                data TEXT NOT NULL,
                observacao TEXT,
                FOREIGN KEY (estoque_id) REFERENCES estoque(id),
                FOREIGN KEY (servico_id) REFERENCES servicos(id)
            );
            CREATE TABLE IF NOT EXISTS app_meta (
                chave TEXT PRIMARY KEY,
                valor TEXT
            );
            """
        )

        vcols = column_names(con, "veiculos")
        for name in ("km_troca_corr", "km_corr_trocada", "km_corr_proxima"):
            if name not in vcols:
                con.execute(f"ALTER TABLE veiculos ADD COLUMN {name} INTEGER DEFAULT 0")

        scols = column_names(con, "servicos")
        if "status" not in scols:
            con.execute("ALTER TABLE servicos ADD COLUMN status TEXT NOT NULL DEFAULT 'Finalizada'")
        if "updated_at" not in scols:
            con.execute("ALTER TABLE servicos ADD COLUMN updated_at TEXT")

        icols = column_names(con, "itens_servico")
        if "estoque_id" not in icols:
            con.execute("ALTER TABLE itens_servico ADD COLUMN estoque_id INTEGER")
        if "origem_estoque" not in icols:
            con.execute("ALTER TABLE itens_servico ADD COLUMN origem_estoque INTEGER NOT NULL DEFAULT 0")

        con.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_clientes_nome ON clientes(nome COLLATE NOCASE);
            CREATE INDEX IF NOT EXISTS idx_veiculos_placa ON veiculos(placa COLLATE NOCASE);
            CREATE INDEX IF NOT EXISTS idx_servicos_data ON servicos(data);
            CREATE INDEX IF NOT EXISTS idx_servicos_veiculo ON servicos(veiculo_id);
            CREATE INDEX IF NOT EXISTS idx_itens_servico_sid ON itens_servico(servico_id);
            CREATE INDEX IF NOT EXISTS idx_itens_estoque_id ON itens_servico(estoque_id);
            CREATE INDEX IF NOT EXISTS idx_estoque_item ON estoque(item COLLATE NOCASE);
            """
        )
        con.execute(
            "INSERT OR REPLACE INTO app_meta(chave, valor) VALUES('schema_version', '2')"
        )
        con.commit()


def normalize(text: str | None) -> str:
    text = (text or "").strip().lower()
    text = "".join(
        c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)
    )
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def as_int(value, default=0) -> int:
    try:
        return int(str(value or "").strip().replace(".", "").replace(",", ""))
    except (TypeError, ValueError):
        return default


def as_float(value, default=0.0) -> float:
    try:
        return float(str(value or "").strip().replace(".", "").replace(",", ".")) if "," in str(value or "") else float(str(value or "").strip() or default)
    except (TypeError, ValueError):
        return default


def br_money(value) -> str:
    value = float(value or 0)
    s = f"{value:,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def record_stock_movement(
    con: sqlite3.Connection,
    estoque_id: int,
    servico_id: int | None,
    tipo: str,
    quantidade: int,
    before: int,
    after: int,
    observacao: str = "",
) -> None:
    con.execute(
        """INSERT INTO movimentos_estoque
           (estoque_id, servico_id, tipo, quantidade, saldo_antes, saldo_depois, data, observacao)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (estoque_id, servico_id, tipo, quantidade, before, after, now_str(), observacao),
    )


def adjust_stock(
    con: sqlite3.Connection,
    estoque_id: int,
    delta_consumo: int,
    servico_id: int | None,
    observacao: str,
) -> None:
    """Ajusta estoque. delta_consumo > 0 consome, < 0 repõe."""
    row = con.execute("SELECT id, item, qtde FROM estoque WHERE id=?", (estoque_id,)).fetchone()
    if not row:
        raise ValueError(f"Item de estoque #{estoque_id} não existe.")
    before = int(row["qtde"] or 0)
    after = before - int(delta_consumo)
    if after < 0:
        raise ValueError(
            f'Estoque insuficiente para "{row["item"]}". Disponível: {before}; necessário a mais: {delta_consumo}.'
        )
    con.execute("UPDATE estoque SET qtde=? WHERE id=?", (after, estoque_id))
    if delta_consumo:
        tipo = "SAIDA_OS" if delta_consumo > 0 else "REPOSICAO_OS"
        record_stock_movement(
            con,
            estoque_id,
            servico_id,
            tipo,
            abs(int(delta_consumo)),
            before,
            after,
            observacao,
        )


def parse_items_from_form(form) -> list[dict]:
    stock_ids = form.getlist("item_estoque_id[]")
    item_ids = form.getlist("item_id[]")
    origins = form.getlist("item_origem_estoque[]")
    cats = form.getlist("item_categoria[]")
    names = form.getlist("item_nome[]")
    qtys = form.getlist("item_qtde[]")
    prices = form.getlist("item_preco[]")
    n = max(len(names), len(cats), len(qtys), len(prices), len(stock_ids), 0)
    items: list[dict] = []
    for i in range(n):
        name = (names[i] if i < len(names) else "").strip()
        if not name:
            continue
        stock_raw = stock_ids[i] if i < len(stock_ids) else ""
        item_raw = item_ids[i] if i < len(item_ids) else ""
        origin_raw = origins[i] if i < len(origins) else "0"
        stock_id = as_int(stock_raw, 0) or None
        item_id = as_int(item_raw, 0) or None
        items.append(
            {
                "id": item_id,
                "estoque_id": stock_id,
                "origem_estoque": 1 if stock_id and str(origin_raw) != "0" else 0,
                "categoria": (cats[i] if i < len(cats) else "").strip(),
                "item": name,
                "qtde": max(1, as_int(qtys[i] if i < len(qtys) else 1, 1)),
                "valor_unit": max(0.0, as_float(prices[i] if i < len(prices) else 0, 0.0)),
            }
        )
    return items


def stock_totals(items: Iterable[dict]) -> dict[int, int]:
    totals: dict[int, int] = {}
    for item in items:
        sid = item.get("estoque_id")
        if sid and item.get("origem_estoque"):
            totals[int(sid)] = totals.get(int(sid), 0) + int(item.get("qtde") or 0)
    return totals


def reconcile_stock_for_os(
    con: sqlite3.Connection,
    servico_id: int,
    old_items: list[dict],
    new_items: list[dict],
) -> None:
    old_totals = stock_totals(old_items)
    new_totals = stock_totals(new_items)
    ids = set(old_totals) | set(new_totals)
    # Primeiro valida todos os consumos adicionais para manter a operação atômica.
    for stock_id in ids:
        delta = new_totals.get(stock_id, 0) - old_totals.get(stock_id, 0)
        if delta > 0:
            row = con.execute("SELECT item, qtde FROM estoque WHERE id=?", (stock_id,)).fetchone()
            if not row:
                raise ValueError(f"Item de estoque #{stock_id} não encontrado.")
            if int(row["qtde"] or 0) < delta:
                raise ValueError(
                    f'Estoque insuficiente para "{row["item"]}". Disponível: {int(row["qtde"] or 0)}; precisa acrescentar {delta} unidade(s) na OS.'
                )
    for stock_id in ids:
        delta = new_totals.get(stock_id, 0) - old_totals.get(stock_id, 0)
        if delta:
            adjust_stock(
                con,
                stock_id,
                delta,
                servico_id,
                f"Ajuste automático da OS #{servico_id}",
            )


def fetch_os_items(con: sqlite3.Connection, servico_id: int) -> list[dict]:
    rows = con.execute(
        """SELECT id, servico_id, categoria, item, qtde, valor_unit,
                  estoque_id, COALESCE(origem_estoque, 0) AS origem_estoque
           FROM itens_servico WHERE servico_id=? ORDER BY id""",
        (servico_id,),
    ).fetchall()
    return [dict(r) for r in rows]
