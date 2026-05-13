"""/admin/backups integration tests."""
import os
import pytest
from pathlib import Path
from flask import Flask
from flask_login import LoginManager, AnonymousUserMixin
from jinja2 import ChoiceLoader, FileSystemLoader


def _make_app(db_manager, tmp_path, monkeypatch):
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path))

    test_templates = os.path.join(os.path.dirname(__file__), "..", "templates")
    real_templates = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..",
                     "pyarchinit_mini", "web_interface", "templates")
    )

    app = Flask(__name__)
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(test_templates),
        FileSystemLoader(real_templates),
    ])
    app.config["TESTING"] = True
    app.config["LOGIN_DISABLED"] = True
    app.config["SECRET_KEY"] = "test"
    app.db_manager = db_manager

    lm = LoginManager(); lm.init_app(app); lm.anonymous_user = AnonymousUserMixin
    @lm.user_loader
    def _u(_id): return None

    @app.route("/")
    def index(): return ""

    @app.template_global()
    def csrf_token(): return "test-csrf-token"
    app.jinja_env.globals["_"] = lambda s: s

    from flask import render_template, request, redirect, url_for, flash, send_file, abort
    from pyarchinit_mini.services.backup_service import BackupService

    @app.route("/admin/backups", methods=["GET"])
    def admin_backups():
        bs = BackupService(app.db_manager)
        return render_template(
            "admin/backups.html",
            backups=bs.list_backups(),
            schedule=bs.get_schedule(),
        )

    @app.route("/admin/backups/now", methods=["POST"])
    def admin_backups_now():
        BackupService(app.db_manager).create_backup_now()
        flash("Backup created", "success")
        return redirect(url_for("admin_backups"))

    @app.route("/admin/backups/schedule", methods=["POST"])
    def admin_backups_schedule():
        bs = BackupService(app.db_manager)
        bs.set_schedule(
            enabled=request.form.get("enabled") == "on",
            frequency=request.form.get("frequency", "weekly"),
            keep_last=int(request.form.get("keep_last", "7")),
        )
        flash("Schedule saved", "success")
        return redirect(url_for("admin_backups"))

    @app.route("/admin/backups/<filename>/delete", methods=["POST"])
    def admin_backups_delete(filename):
        ok = BackupService(app.db_manager).delete_backup(filename)
        if not ok:
            abort(404)
        flash("Backup deleted", "info")
        return redirect(url_for("admin_backups"))

    @app.route("/admin/backups/<filename>/download")
    def admin_backups_download(filename):
        from pathlib import Path as _P
        if "/" in filename or ".." in filename or not filename.startswith("pyarchinit_backup_"):
            abort(404)
        base = _P(os.environ.get("PYARCHINIT_HOME", str(_P.home() / ".pyarchinit_mini"))) / "backups"
        target = base / filename
        if not target.exists():
            abort(404)
        return send_file(str(target), as_attachment=True)

    return app


@pytest.fixture
def app(db_manager, tmp_path, monkeypatch):
    return _make_app(db_manager, tmp_path, monkeypatch)


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_backups_page(client):
    r = client.get("/admin/backups")
    assert r.status_code == 200
    assert b"Backup Now" in r.data


def test_post_backup_now_creates_file(client, app):
    from pyarchinit_mini.services.backup_service import BackupService
    r = client.post("/admin/backups/now")
    assert r.status_code in (302, 303)
    bs = BackupService(app.db_manager)
    assert len(bs.list_backups()) == 1


def test_schedule_save(client, app):
    r = client.post("/admin/backups/schedule", data={
        "enabled": "on", "frequency": "daily", "keep_last": "5",
    })
    assert r.status_code in (302, 303)
    from pyarchinit_mini.services.backup_service import BackupService
    bs = BackupService(app.db_manager)
    sched = bs.get_schedule()
    assert sched == {"enabled": True, "frequency": "daily", "keep_last": 5}


def test_delete_backup(client, app):
    from pyarchinit_mini.services.backup_service import BackupService
    bs = BackupService(app.db_manager)
    info = bs.create_backup_now()
    filename = Path(info["path"]).name
    r = client.post(f"/admin/backups/{filename}/delete")
    assert r.status_code in (302, 303)
    assert bs.list_backups() == []


def test_delete_rejects_path_traversal(client):
    # Werkzeug 2.x/3.x rejects URL-encoded slashes by default and returns 404
    r = client.post("/admin/backups/..%2Fetc%2Fpasswd/delete")
    assert r.status_code in (404, 405)
