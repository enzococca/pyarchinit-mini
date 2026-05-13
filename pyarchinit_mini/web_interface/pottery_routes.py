"""Pottery web routes. Call _register_pottery_routes(app) from create_app()."""
from __future__ import annotations

from flask import (
    render_template, request, redirect, url_for, flash, jsonify, abort,
)
from flask_login import login_required

from ..services.pottery_service import PotteryService
from ..services.pottery_dto import PotteryDTO


_POTTERY_FORM_FIELDS = (
    "id_number", "sito", "area", "us", "box", "photo", "drawing", "anno",
    "fabric", "percent", "material", "form", "specific_form", "ware",
    "munsell", "surf_trat", "exdeco", "intdeco", "wheel_made",
    "descrip_ex_deco", "descrip_in_deco", "note", "diametro_max", "qty",
    "diametro_rim", "diametro_bottom", "diametro_height",
    "diametro_preserved", "specific_shape", "bag", "sector",
)
_INT_FIELDS = {"id_number", "us", "box", "anno", "qty", "bag"}
_NUM_FIELDS = {
    "diametro_max", "diametro_rim", "diametro_bottom",
    "diametro_height", "diametro_preserved",
}


def _extract_pottery_form(form) -> dict:
    """Pull pottery fields from a Flask request.form, coercing types."""
    out = {}
    for k in _POTTERY_FORM_FIELDS:
        v = form.get(k)
        if v in (None, ""):
            continue
        if k in _INT_FIELDS:
            try:
                out[k] = int(v)
            except ValueError:
                continue
        elif k in _NUM_FIELDS:
            try:
                out[k] = float(v)
            except ValueError:
                continue
        else:
            out[k] = v
    return out


def _distinct_values(app, column_name: str):
    """Return distinct non-null values for a Pottery column as JSON."""
    from ..models.pottery import Pottery
    with app.db_manager.connection.get_session() as session:
        col = getattr(Pottery, column_name)
        rows = session.query(col).filter(col.isnot(None)).distinct().all()
        return jsonify({"values": sorted({r[0] for r in rows if r[0]})})


def _register_pottery_routes(app):
    """Register pottery URL rules on the Flask app."""

    @app.route("/pottery")
    @login_required
    def pottery_list():
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", 25))
        filters = {
            k: request.args.get(k)
            for k in ("sito", "area", "us", "form", "fabric", "ware", "q")
            if request.args.get(k)
        }
        if "us" in filters:
            try:
                filters["us"] = int(filters["us"])
            except ValueError:
                filters.pop("us")
        svc = PotteryService(app.db_manager)
        items, total = svc.get_all_pottery(page=page, size=size, filters=filters)
        return render_template(
            "pottery/list.html",
            items=[PotteryDTO.from_model(p) for p in items],
            total=total, page=page, size=size, filters=filters,
        )

    @app.route("/pottery/create", methods=["GET", "POST"])
    @login_required
    def pottery_create():
        svc = PotteryService(app.db_manager)
        if request.method == "POST":
            data = _extract_pottery_form(request.form)
            try:
                p = svc.create_pottery(data)
            except ValueError as e:
                flash(str(e), "danger")
                return render_template(
                    "pottery/form.html",
                    pottery=None, form_data=data, mode="create",
                )
            flash(f"Pottery #{p.id_rep} created.", "success")
            try:
                return redirect(url_for("pottery_detail", id_rep=p.id_rep))
            except Exception:
                # pottery_detail not yet registered (during T11 development) — go to list
                return redirect(url_for("pottery_list"))
        return render_template(
            "pottery/form.html", pottery=None, form_data={}, mode="create"
        )

    @app.route("/pottery/<int:id_rep>")
    @login_required
    def pottery_detail(id_rep: int):
        svc = PotteryService(app.db_manager)
        p = svc.get_pottery_by_id(id_rep)
        if not p:
            abort(404)
        return render_template(
            "pottery/detail.html",
            pottery=PotteryDTO.from_model(p),
        )

    @app.route("/pottery/<int:id_rep>/edit", methods=["GET", "POST"])
    @login_required
    def pottery_edit(id_rep: int):
        svc = PotteryService(app.db_manager)
        p = svc.get_pottery_by_id(id_rep)
        if not p:
            abort(404)
        if request.method == "POST":
            data = _extract_pottery_form(request.form)
            try:
                svc.update_pottery(id_rep, data)
            except ValueError as e:
                flash(str(e), "danger")
                return render_template(
                    "pottery/form.html",
                    pottery=PotteryDTO.from_model(p),
                    form_data=data, mode="edit",
                )
            flash(f"Pottery #{id_rep} updated.", "success")
            return redirect(url_for("pottery_detail", id_rep=id_rep))
        return render_template(
            "pottery/form.html",
            pottery=PotteryDTO.from_model(p),
            form_data={}, mode="edit",
        )

    @app.route("/pottery/<int:id_rep>/delete", methods=["POST"])
    @login_required
    def pottery_delete(id_rep: int):
        svc = PotteryService(app.db_manager)
        if not svc.delete_pottery(id_rep):
            abort(404)
        flash(f"Pottery #{id_rep} deleted.", "info")
        return redirect(url_for("pottery_list"))

    @app.route("/api/pottery/forms")
    @login_required
    def pottery_api_forms():
        return _distinct_values(app, "form")

    @app.route("/api/pottery/fabrics")
    @login_required
    def pottery_api_fabrics():
        return _distinct_values(app, "fabric")

    @app.route("/api/pottery/wares")
    @login_required
    def pottery_api_wares():
        return _distinct_values(app, "ware")

    @app.route("/api/pottery/stats")
    @login_required
    def pottery_api_stats():
        from sqlalchemy import func as f
        from ..models.pottery import Pottery as _Pottery
        svc = PotteryService(app.db_manager)
        sito = request.args.get("sito")
        area = request.args.get("area")
        us = request.args.get("us")
        us_int = int(us) if us and us.isdigit() else None

        by_form = svc.get_form_distribution(sito) if sito else svc.get_form_distribution()
        by_fabric = svc.get_fabric_distribution(sito) if sito else svc.get_fabric_distribution()
        by_ware = svc.get_ware_distribution(sito) if sito else svc.get_ware_distribution()

        filters = {k: v for k, v in {"sito": sito, "area": area, "us": us_int}.items() if v}
        total = svc.count_pottery(filters or None)
        mni = svc.calculate_mni(sito, area, us_int)["total"] if sito else 0

        with app.db_manager.connection.get_session() as session:
            q = session.query(_Pottery.anno, f.count(_Pottery.id_rep)).group_by(_Pottery.anno)
            if sito:
                q = q.filter(_Pottery.sito == sito)
            by_anno = [{"anno": a, "count": c} for a, c in q.all() if a is not None]

        return jsonify({
            "total": total,
            "by_form": [{"form": k, "count": v} for k, v in by_form.items()],
            "by_fabric": [{"fabric": k, "count": v} for k, v in by_fabric.items()],
            "by_ware": [{"ware": k, "count": v} for k, v in by_ware.items()],
            "by_anno": by_anno,
            "mni": mni,
        })
