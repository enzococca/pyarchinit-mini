"""The /3d routes (s3Dgraphy integration) register on every app.

create_app() imports them package-qualified; init_s3d_routes() builds its
blueprint per call, so a second app in the same process (tests, app
factories) gets the routes too.
"""
from flask import Flask

from pyarchinit_mini.web_interface.s3d_routes import init_s3d_routes


def _app(tmp_path):
    app = Flask(__name__)
    app.config["UPLOAD_FOLDER"] = str(tmp_path / "uploads")
    init_s3d_routes(app, db_manager=None, media_handler=None)
    return app


def _rules(app):
    return sorted(r.rule for r in app.url_map.iter_rules() if r.rule.startswith("/3d/"))


def test_s3d_routes_register_on_every_app(tmp_path):
    first, second = _app(tmp_path), _app(tmp_path)
    assert len(_rules(first)) == 8
    assert _rules(second) == _rules(first)
