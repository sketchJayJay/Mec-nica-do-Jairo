from __future__ import annotations

import io
import os
import secrets
import sqlite3
import tempfile
import zipfile
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    session,
    url_for,
)
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash

from db import (
    adjust_stock,
    as_float,
    as_int,
    br_money,
    connect,
    db_path,
    fetch_os_items,
    init_db,
    now_str,
    parse_items_from_form,
    reconcile_stock_for_os,
    record_stock_movement,
    transaction,
)

APP_VERSION = "2.0.3-web-sem-login"


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "troque-esta-chave-no-coolify"),
        WTF_CSRF_TIME_LIMIT=None,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
    )
    if test_config:
        app.config.update(test_config)

    CSRFProtect(app)
    init_db()

    @app.template_filter("money")
    def _money(v):
        return br_money(v)

    @app.template_filter("datebr")
    def _datebr(v):
        if not v:
            return "—"
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d", "%d/%m/%Y %H:%M"):
            try:
                return datetime.strptime(str(v), fmt).strftime("%d/%m/%Y %H:%M")
            except ValueError:
                continue
        return str(v)

    @app.template_filter("dateonlybr")
    def _dateonlybr(v):
        if not v:
            return "—"
        raw = str(v).strip()
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
            try:
                return datetime.strptime(raw, fmt).strftime("%d/%m/%Y")
            except ValueError:
                continue
        try:
            return datetime.strptime(raw[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            return raw

    @app.context_processor
    def inject_globals():
        return {"APP_VERSION": APP_VERSION}

    def login_required(fn):
        # O sistema fica acessível diretamente, sem tela de login.
        return fn

    @app.route("/manifest.webmanifest")
    def manifest():
        return send_from_directory(app.static_folder, "manifest.webmanifest", mimetype="application/manifest+json")

    @app.route("/service-worker.js")
    def service_worker():
        response = send_from_directory(app.static_folder, "service-worker.js", mimetype="application/javascript")
        response.headers["Service-Worker-Allowed"] = "/"
        response.headers["Cache-Control"] = "no-cache"
        return response

    @app.route("/health")
    def health():
        try:
            with connect() as con:
                con.execute("SELECT 1").fetchone()
            return jsonify(status="ok", version=APP_VERSION)
        except Exception as exc:
            return jsonify(status="error", error=str(exc)), 500

    @app.route("/login", methods=["GET", "POST"])
    def login():
        # Compatibilidade com favoritos/atalhos antigos.
        return redirect(url_for("dashboard"))

    @app.route("/logout", methods=["GET", "POST"])
    def logout():
        return redirect(url_for("dashboard"))


    @app.route("/")
    @login_required
    def dashboard():
        with connect() as con:
            counts = {
                "clientes": con.execute("SELECT COUNT(*) FROM clientes").fetchone()[0],
                "veiculos": con.execute("SELECT COUNT(*) FROM veiculos").fetchone()[0],
                "os": con.execute("SELECT COUNT(*) FROM servicos").fetchone()[0],
                "estoque": con.execute("SELECT COUNT(*) FROM estoque").fetchone()[0],
                "baixo": con.execute("SELECT COUNT(*) FROM estoque WHERE qtde <= 1").fetchone()[0],
            }
            recent = con.execute(
                """SELECT s.id, s.data, s.status, c.nome, v.placa, v.marca, v.modelo,
                          COALESCE(SUM(i.qtde * i.valor_unit), 0) total
                   FROM servicos s
                   JOIN veiculos v ON v.id=s.veiculo_id
                   JOIN clientes c ON c.id=v.cliente_id
                   LEFT JOIN itens_servico i ON i.servico_id=s.id
                   GROUP BY s.id
                   ORDER BY s.id DESC LIMIT 8"""
            ).fetchall()
            low_stock = con.execute(
                "SELECT id, item, categoria, qtde, preco FROM estoque WHERE qtde <= 1 ORDER BY qtde, item COLLATE NOCASE LIMIT 8"
            ).fetchall()
        return render_template("dashboard.html", counts=counts, recent=recent, low_stock=low_stock)

    # ---------------- Clientes / Veículos ----------------
    @app.route("/clientes")
    @login_required
    def clientes():
        q = request.args.get("q", "").strip()
        like = f"%{q}%"
        with connect() as con:
            rows = con.execute(
                """SELECT c.id, c.nome, c.telefone, COUNT(v.id) veiculos
                   FROM clientes c LEFT JOIN veiculos v ON v.cliente_id=c.id
                   WHERE (?='' OR c.nome LIKE ? OR c.telefone LIKE ?)
                   GROUP BY c.id ORDER BY c.nome COLLATE NOCASE LIMIT 500""",
                (q, like, like),
            ).fetchall()
        return render_template("clientes.html", clientes=rows, q=q)

    @app.route("/clientes/<int:cliente_id>/editar", methods=["GET", "POST"])
    @login_required
    def cliente_editar(cliente_id):
        with connect() as con:
            cliente = con.execute("SELECT * FROM clientes WHERE id=?", (cliente_id,)).fetchone()
            veiculos = con.execute(
                "SELECT * FROM veiculos WHERE cliente_id=? ORDER BY id DESC", (cliente_id,)
            ).fetchall()
        if not cliente:
            abort(404)
        if request.method == "POST":
            nome = request.form.get("nome", "").strip()
            if not nome:
                flash("Informe o nome do cliente.", "danger")
            else:
                with transaction() as con:
                    con.execute(
                        "UPDATE clientes SET nome=?, telefone=? WHERE id=?",
                        (nome, request.form.get("telefone", "").strip(), cliente_id),
                    )
                flash("Cliente atualizado.", "success")
                return redirect(url_for("cliente_editar", cliente_id=cliente_id))
        return render_template("cliente_form.html", cliente=cliente, veiculos=veiculos)

    @app.route("/veiculos/<int:veiculo_id>/editar", methods=["GET", "POST"])
    @login_required
    def veiculo_editar(veiculo_id):
        with connect() as con:
            veiculo = con.execute(
                """SELECT v.*, c.nome cliente_nome FROM veiculos v
                   JOIN clientes c ON c.id=v.cliente_id WHERE v.id=?""",
                (veiculo_id,),
            ).fetchone()
        if not veiculo:
            abort(404)
        if request.method == "POST":
            placa = request.form.get("placa", "").strip().upper()
            try:
                with transaction() as con:
                    con.execute(
                        """UPDATE veiculos SET marca=?, modelo=?, placa=?, ano=?, km_atual=?,
                           km_troca_corr=?, km_corr_trocada=?, km_corr_proxima=? WHERE id=?""",
                        (
                            request.form.get("marca", "").strip(),
                            request.form.get("modelo", "").strip(),
                            placa,
                            request.form.get("ano", "").strip(),
                            as_int(request.form.get("km_atual")),
                            as_int(request.form.get("km_troca_corr")),
                            as_int(request.form.get("km_corr_trocada")),
                            as_int(request.form.get("km_corr_proxima")),
                            veiculo_id,
                        ),
                    )
                flash("Veículo atualizado.", "success")
                return redirect(url_for("veiculo_editar", veiculo_id=veiculo_id))
            except sqlite3.IntegrityError:
                flash("Essa placa já está cadastrada em outro veículo.", "danger")
        return render_template("veiculo_form.html", veiculo=veiculo)

    # ---------------- OS ----------------
    @app.route("/os")
    @login_required
    def os_list():
        q = request.args.get("q", "").strip()
        status = request.args.get("status", "").strip()
        like = f"%{q}%"
        with connect() as con:
            rows = con.execute(
                """SELECT s.id, s.data, s.status, s.km_atual, c.nome, c.telefone,
                          v.id veiculo_id, v.marca, v.modelo, v.placa,
                          COALESCE(SUM(i.qtde*i.valor_unit),0) total
                   FROM servicos s
                   JOIN veiculos v ON v.id=s.veiculo_id
                   JOIN clientes c ON c.id=v.cliente_id
                   LEFT JOIN itens_servico i ON i.servico_id=s.id
                   WHERE (?='' OR c.nome LIKE ? OR v.placa LIKE ? OR CAST(s.id AS TEXT) LIKE ?)
                     AND (?='' OR s.status=?)
                   GROUP BY s.id
                   ORDER BY s.id DESC LIMIT 500""",
                (q, like, like, like, status, status),
            ).fetchall()
        return render_template("os_list.html", ordens=rows, q=q, status=status)

    def _load_os(servico_id: int):
        with connect() as con:
            os_row = con.execute(
                """SELECT s.*, v.cliente_id, v.marca, v.modelo, v.placa, v.ano,
                          v.km_atual AS veiculo_km_atual,
                          COALESCE(v.km_troca_corr,0) km_troca_corr,
                          COALESCE(v.km_corr_trocada,0) km_corr_trocada,
                          COALESCE(v.km_corr_proxima,0) km_corr_proxima,
                          c.nome, c.telefone
                   FROM servicos s
                   JOIN veiculos v ON v.id=s.veiculo_id
                   JOIN clientes c ON c.id=v.cliente_id
                   WHERE s.id=?""",
                (servico_id,),
            ).fetchone()
            if not os_row:
                return None, []
            items = fetch_os_items(con, servico_id)
        return os_row, items

    def _upsert_client_vehicle(con, form, current_vehicle_id: int | None = None):
        cliente_id = as_int(form.get("cliente_id"), 0) or None
        veiculo_id = as_int(form.get("veiculo_id"), 0) or current_vehicle_id or None
        nome = form.get("cliente_nome", "").strip()
        telefone = form.get("cliente_telefone", "").strip()
        if not nome:
            raise ValueError("Informe o nome do cliente.")
        if cliente_id and con.execute("SELECT 1 FROM clientes WHERE id=?", (cliente_id,)).fetchone():
            con.execute("UPDATE clientes SET nome=?, telefone=? WHERE id=?", (nome, telefone, cliente_id))
        else:
            con.execute("INSERT INTO clientes(nome, telefone) VALUES(?,?)", (nome, telefone))
            cliente_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]

        placa = form.get("placa", "").strip().upper()
        if not placa:
            raise ValueError("Informe a placa do carro.")
        values = (
            cliente_id,
            form.get("marca", "").strip(),
            form.get("modelo", "").strip(),
            placa,
            form.get("ano", "").strip(),
            as_int(form.get("veiculo_km_atual")),
            as_int(form.get("km_troca_corr")),
            as_int(form.get("km_corr_trocada")),
            as_int(form.get("km_corr_proxima")),
        )
        if veiculo_id and con.execute("SELECT 1 FROM veiculos WHERE id=?", (veiculo_id,)).fetchone():
            conflict = con.execute("SELECT id FROM veiculos WHERE placa=? AND id<>?", (placa, veiculo_id)).fetchone()
            if conflict:
                raise ValueError("Essa placa já pertence a outro veículo cadastrado.")
            con.execute(
                """UPDATE veiculos SET cliente_id=?, marca=?, modelo=?, placa=?, ano=?, km_atual=?,
                   km_troca_corr=?, km_corr_trocada=?, km_corr_proxima=? WHERE id=?""",
                values + (veiculo_id,),
            )
        else:
            existing = con.execute("SELECT id FROM veiculos WHERE placa=?", (placa,)).fetchone()
            if existing:
                veiculo_id = int(existing[0])
                con.execute(
                    """UPDATE veiculos SET cliente_id=?, marca=?, modelo=?, ano=?, km_atual=?,
                       km_troca_corr=?, km_corr_trocada=?, km_corr_proxima=? WHERE id=?""",
                    (values[0], values[1], values[2], values[4], values[5], values[6], values[7], values[8], veiculo_id),
                )
            else:
                con.execute(
                    """INSERT INTO veiculos(cliente_id,marca,modelo,placa,ano,km_atual,
                       km_troca_corr,km_corr_trocada,km_corr_proxima)
                       VALUES(?,?,?,?,?,?,?,?,?)""",
                    values,
                )
                veiculo_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]
        return int(cliente_id), int(veiculo_id)

    @app.route("/os/nova", methods=["GET", "POST"])
    @login_required
    def os_nova():
        if request.method == "POST":
            items = parse_items_from_form(request.form)
            try:
                with transaction() as con:
                    _, veiculo_id = _upsert_client_vehicle(con, request.form)
                    km = as_int(request.form.get("km_atual"))
                    intervalo = as_int(request.form.get("intervalo_km"))
                    proxima = as_int(request.form.get("proxima_manut_km"), km + intervalo if intervalo else km)
                    con.execute(
                        """INSERT INTO servicos(veiculo_id,descricao,km_atual,intervalo_km,
                           proxima_manut_km,data,status,updated_at) VALUES(?,?,?,?,?,?,?,?)""",
                        (
                            veiculo_id,
                            request.form.get("descricao", "").strip(),
                            km,
                            intervalo,
                            proxima,
                            request.form.get("data", "").strip() or now_str(),
                            request.form.get("status", "Aberta"),
                            now_str(),
                        ),
                    )
                    sid = int(con.execute("SELECT last_insert_rowid()").fetchone()[0])
                    reconcile_stock_for_os(con, sid, [], items)
                    for item in items:
                        con.execute(
                            """INSERT INTO itens_servico(servico_id,categoria,item,qtde,valor_unit,estoque_id,origem_estoque)
                               VALUES(?,?,?,?,?,?,?)""",
                            (sid, item["categoria"], item["item"], item["qtde"], item["valor_unit"], item["estoque_id"], item["origem_estoque"]),
                        )
                flash(f"OS #{sid} criada com sucesso.", "success")
                return redirect(url_for("os_view", servico_id=sid))
            except (ValueError, sqlite3.IntegrityError) as exc:
                flash(str(exc), "danger")
        return render_template("os_form.html", ordem=None, items=[], now=now_str())

    @app.route("/os/<int:servico_id>")
    @login_required
    def os_view(servico_id):
        ordem, items = _load_os(servico_id)
        if not ordem:
            abort(404)
        total = sum(int(i["qtde"] or 0) * float(i["valor_unit"] or 0) for i in items)
        return render_template("os_view.html", ordem=ordem, items=items, total=total)

    @app.route("/os/<int:servico_id>/editar", methods=["GET", "POST"])
    @login_required
    def os_editar(servico_id):
        ordem, old_items = _load_os(servico_id)
        if not ordem:
            abort(404)
        if request.method == "POST":
            new_items = parse_items_from_form(request.form)
            try:
                with transaction() as con:
                    _, veiculo_id = _upsert_client_vehicle(con, request.form, int(ordem["veiculo_id"]))
                    km = as_int(request.form.get("km_atual"))
                    intervalo = as_int(request.form.get("intervalo_km"))
                    proxima = as_int(request.form.get("proxima_manut_km"), km + intervalo if intervalo else km)
                    reconcile_stock_for_os(con, servico_id, old_items, new_items)
                    con.execute(
                        """UPDATE servicos SET veiculo_id=?, descricao=?, km_atual=?, intervalo_km=?,
                           proxima_manut_km=?, data=?, status=?, updated_at=? WHERE id=?""",
                        (
                            veiculo_id,
                            request.form.get("descricao", "").strip(),
                            km,
                            intervalo,
                            proxima,
                            request.form.get("data", "").strip() or ordem["data"],
                            request.form.get("status", ordem["status"]),
                            now_str(),
                            servico_id,
                        ),
                    )
                    con.execute("DELETE FROM itens_servico WHERE servico_id=?", (servico_id,))
                    for item in new_items:
                        con.execute(
                            """INSERT INTO itens_servico(servico_id,categoria,item,qtde,valor_unit,estoque_id,origem_estoque)
                               VALUES(?,?,?,?,?,?,?)""",
                            (servico_id, item["categoria"], item["item"], item["qtde"], item["valor_unit"], item["estoque_id"], item["origem_estoque"]),
                        )
                flash(f"OS #{servico_id} atualizada. Você pode editar novamente mesmo finalizada.", "success")
                return redirect(url_for("os_view", servico_id=servico_id))
            except (ValueError, sqlite3.IntegrityError) as exc:
                flash(str(exc), "danger")
        return render_template("os_form.html", ordem=ordem, items=old_items, now=now_str())

    @app.route("/os/<int:servico_id>/excluir", methods=["POST"])
    @login_required
    def os_excluir(servico_id):
        ordem, old_items = _load_os(servico_id)
        if not ordem:
            abort(404)
        try:
            with transaction() as con:
                # Só repõe itens criados no novo sistema com vínculo explícito ao estoque.
                reconcile_stock_for_os(con, servico_id, old_items, [])
                con.execute("DELETE FROM itens_servico WHERE servico_id=?", (servico_id,))
                # Mantém a auditoria, mas solta a referência antes de excluir a OS.
                con.execute("UPDATE movimentos_estoque SET servico_id=NULL WHERE servico_id=?", (servico_id,))
                con.execute("DELETE FROM servicos WHERE id=?", (servico_id,))
            flash(f"OS #{servico_id} excluída.", "success")
        except ValueError as exc:
            flash(str(exc), "danger")
        return redirect(url_for("os_list"))

    @app.route("/os/<int:servico_id>/imprimir")
    @login_required
    def os_print(servico_id):
        ordem, items = _load_os(servico_id)
        if not ordem:
            abort(404)
        total = sum(int(i["qtde"] or 0) * float(i["valor_unit"] or 0) for i in items)
        return render_template("os_print.html", ordem=ordem, items=items, total=total)

    # ---------------- Estoque ----------------
    @app.route("/estoque")
    @login_required
    def estoque():
        q = request.args.get("q", "").strip()
        categoria = request.args.get("categoria", "").strip()
        like = f"%{q}%"
        with connect() as con:
            rows = con.execute(
                """SELECT * FROM estoque WHERE (?='' OR item LIKE ?)
                   AND (?='' OR categoria=?) ORDER BY item COLLATE NOCASE LIMIT 2000""",
                (q, like, categoria, categoria),
            ).fetchall()
            categorias = con.execute(
                "SELECT DISTINCT categoria FROM estoque WHERE COALESCE(categoria,'')<>'' ORDER BY categoria COLLATE NOCASE"
            ).fetchall()
            total_valor = con.execute(
                "SELECT COALESCE(SUM(qtde*preco),0) FROM estoque"
            ).fetchone()[0]
        return render_template(
            "estoque.html", items=rows, q=q, categoria=categoria, categorias=categorias, total_valor=total_valor
        )

    @app.route("/estoque/novo", methods=["GET", "POST"])
    @login_required
    def estoque_novo():
        if request.method == "POST":
            nome = request.form.get("item", "").strip()
            if not nome:
                flash("Informe o nome do item.", "danger")
            else:
                with transaction() as con:
                    con.execute(
                        "INSERT INTO estoque(item,categoria,qtde,preco) VALUES(?,?,?,?)",
                        (
                            nome,
                            request.form.get("categoria", "").strip(),
                            max(0, as_int(request.form.get("qtde"))),
                            max(0.0, as_float(request.form.get("preco"))),
                        ),
                    )
                flash("Item adicionado ao estoque.", "success")
                return redirect(url_for("estoque"))
        return render_template("estoque_form.html", item=None)

    @app.route("/estoque/<int:item_id>/editar", methods=["GET", "POST"])
    @login_required
    def estoque_editar(item_id):
        with connect() as con:
            item = con.execute("SELECT * FROM estoque WHERE id=?", (item_id,)).fetchone()
        if not item:
            abort(404)
        if request.method == "POST":
            nome = request.form.get("item", "").strip()
            if not nome:
                flash("O nome do item não pode ficar vazio.", "danger")
            else:
                new_q = max(0, as_int(request.form.get("qtde")))
                with transaction() as con:
                    current = con.execute("SELECT qtde FROM estoque WHERE id=?", (item_id,)).fetchone()
                    before = int(current[0] or 0)
                    con.execute(
                        "UPDATE estoque SET item=?, categoria=?, qtde=?, preco=? WHERE id=?",
                        (nome, request.form.get("categoria", "").strip(), new_q, max(0.0, as_float(request.form.get("preco"))), item_id),
                    )
                    if new_q != before:
                        record_stock_movement(
                            con, item_id, None, "AJUSTE_MANUAL", abs(new_q-before), before, new_q,
                            "Ajuste manual no cadastro do estoque"
                        )
                flash("Item atualizado. O nome/descrição também foi alterado.", "success")
                return redirect(url_for("estoque", q=nome))
        return render_template("estoque_form.html", item=item)

    @app.route("/estoque/<int:item_id>/excluir", methods=["POST"])
    @login_required
    def estoque_excluir(item_id):
        with transaction() as con:
            linked = con.execute(
                "SELECT COUNT(*) FROM itens_servico WHERE estoque_id=?", (item_id,)
            ).fetchone()[0]
            movements = con.execute(
                "SELECT COUNT(*) FROM movimentos_estoque WHERE estoque_id=?", (item_id,)
            ).fetchone()[0]
            if linked or movements:
                flash("Esse item já possui vínculo ou histórico de movimentação. Em vez de excluir, zere a quantidade ou edite o nome.", "warning")
            else:
                con.execute("DELETE FROM estoque WHERE id=?", (item_id,))
                flash("Item excluído do estoque.", "success")
        return redirect(url_for("estoque"))

    @app.route("/estoque/imprimir")
    @login_required
    def estoque_print():
        with connect() as con:
            rows = con.execute(
                "SELECT * FROM estoque ORDER BY categoria COLLATE NOCASE, item COLLATE NOCASE"
            ).fetchall()
            total = con.execute("SELECT COALESCE(SUM(qtde*preco),0) FROM estoque").fetchone()[0]
        return render_template("estoque_print.html", items=rows, total=total, generated=now_str())

    @app.route("/api/estoque")
    @login_required
    def api_estoque():
        q = request.args.get("q", "").strip()
        like = f"%{q}%"
        with connect() as con:
            rows = con.execute(
                """SELECT id,item,categoria,qtde,preco FROM estoque
                   WHERE (?='' OR item LIKE ? OR categoria LIKE ?)
                   ORDER BY CASE WHEN qtde>0 THEN 0 ELSE 1 END, item COLLATE NOCASE LIMIT 30""",
                (q, like, like),
            ).fetchall()
        return jsonify([dict(r) for r in rows])

    @app.route("/api/clientes")
    @login_required
    def api_clientes():
        q = request.args.get("q", "").strip()
        like = f"%{q}%"
        with connect() as con:
            rows = con.execute(
                """SELECT c.id cliente_id,c.nome,c.telefone,v.id veiculo_id,v.marca,v.modelo,v.placa,v.ano,
                          v.km_atual,v.km_troca_corr,v.km_corr_trocada,v.km_corr_proxima
                   FROM clientes c LEFT JOIN veiculos v ON v.cliente_id=c.id
                   WHERE (?='' OR c.nome LIKE ? OR c.telefone LIKE ? OR v.placa LIKE ?)
                   ORDER BY c.nome COLLATE NOCASE LIMIT 30""",
                (q, like, like, like),
            ).fetchall()
        return jsonify([dict(r) for r in rows])

    # ---------------- Relatórios / Backup ----------------
    @app.route("/relatorios")
    @login_required
    def relatorios():
        with connect() as con:
            top_items = con.execute(
                """SELECT item, SUM(qtde) quantidade, SUM(qtde*valor_unit) valor
                   FROM itens_servico GROUP BY item ORDER BY quantidade DESC LIMIT 15"""
            ).fetchall()
            por_mes = con.execute(
                """SELECT substr(data,1,7) mes, COUNT(*) os_count,
                          COALESCE(SUM((SELECT SUM(i.qtde*i.valor_unit) FROM itens_servico i WHERE i.servico_id=s.id)),0) valor
                   FROM servicos s WHERE data IS NOT NULL AND data<>''
                   GROUP BY substr(data,1,7) ORDER BY mes DESC LIMIT 12"""
            ).fetchall()
            movements = con.execute(
                """SELECT m.*, e.item FROM movimentos_estoque m LEFT JOIN estoque e ON e.id=m.estoque_id
                   ORDER BY m.id DESC LIMIT 30"""
            ).fetchall()
        return render_template("relatorios.html", top_items=top_items, por_mes=por_mes, movements=movements)

    @app.route("/backup/database")
    @login_required
    def backup_database():
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with tempfile.TemporaryDirectory() as td:
            snapshot = Path(td) / f"oficina_{stamp}.db"
            source = connect()
            dest = sqlite3.connect(snapshot)
            try:
                source.backup(dest)
            finally:
                dest.close()
                source.close()
            mem = io.BytesIO()
            with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(snapshot, arcname=snapshot.name)
                zf.writestr(
                    "LEIA-ME.txt",
                    "Backup do banco da Mecânica do Jairo. Guarde este arquivo em local seguro.\n",
                )
            mem.seek(0)
        return send_file(
            mem,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"backup_mecanica_jairo_{stamp}.zip",
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")), debug=os.environ.get("FLASK_DEBUG") == "1")
