"""Round-trip: DB → export GraphML → wipe → import → assert parity."""
import io
from pathlib import Path

import pytest
from flask import Flask
from sqlalchemy import create_engine, text


_APP_TEMPLATES = (
    Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"
)


@pytest.fixture
def app_and_engine(tmp_path, monkeypatch):
    db_url = f"sqlite:///{tmp_path}/rt.db"
    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setenv("SWIMLANE_PIPELINE", "s3dgraphy")
    engine = create_engine(db_url)
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT UNIQUE)"""))
        conn.execute(text("INSERT INTO site_table (sito) VALUES ('S')"))
        conn.execute(text("""CREATE TABLE period_table (id_period INTEGER PRIMARY KEY,
            sito TEXT, periodo TEXT, fase TEXT, datazione TEXT)"""))
        conn.execute(text("""CREATE TABLE periodizzazione_table (id_periodizzazione INTEGER PRIMARY KEY,
            sito TEXT, periodo_iniziale INTEGER, fase_iniziale INTEGER, periodo_finale INTEGER,
            fase_finale INTEGER, cronologia_iniziale TEXT, cronologia_finale TEXT, descrizione TEXT)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT, area TEXT, us TEXT,
            unita_tipo TEXT, descrizione TEXT, fase_iniziale TEXT, fase_finale TEXT,
            settore TEXT, quadrato TEXT, attivita TEXT, struttura TEXT,
            rapporti TEXT, data_origine TEXT, UNIQUE(sito, area, us))"""))
        conn.execute(text(
            "INSERT INTO us_table (sito,area,us,unita_tipo,rapporti) VALUES "
            "('S','A','1','USM','[[\"Copre\",\"2\",\"A\",\"S\"]]')"
        ))
        conn.execute(text(
            "INSERT INTO us_table (sito,area,us,unita_tipo) VALUES ('S','A','2','USV')"
        ))
    from pyarchinit_mini.web_interface.harris_creator_routes import harris_creator_bp
    app = Flask(__name__, template_folder=str(_APP_TEMPLATES))
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "t"
    app.config["WTF_CSRF_ENABLED"] = False
    app.register_blueprint(harris_creator_bp)
    return app.test_client(), engine


def test_roundtrip_graphml_preserves_us_and_rapporti(app_and_engine):
    client, engine = app_and_engine

    # 1) Export
    r_export = client.get("/harris-creator/api/export/S/yed-graphml")
    assert r_export.status_code == 200, r_export.data[:300]
    exported_bytes = r_export.data

    # 2) Wipe US data (keep schema)
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM us_table"))
        count_after_wipe = conn.execute(text("SELECT COUNT(*) FROM us_table")).scalar()
        assert count_after_wipe == 0

    # 3) Re-import
    r_import = client.post(
        "/harris-creator/api/import/S/graphml",
        data={"file": (io.BytesIO(exported_bytes), "rt.graphml")},
        content_type="multipart/form-data",
    )
    assert r_import.status_code == 200, r_import.data[:300]
    body = r_import.get_json()
    assert body["imported_us"] >= 2

    # 4) Verify US back in place
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT us, rapporti FROM us_table ORDER BY us")).fetchall()
        # US numbers preserved (labels carry the original US value)
        us_nums = sorted(r[0] for r in rows)
        assert "1" in us_nums
        assert "2" in us_nums
        # Rapporti restored on at least one side (forward or inverse)
        r1 = next((r[1] for r in rows if r[0] == "1"), "")
        r2 = next((r[1] for r in rows if r[0] == "2"), "")
        assert ("Copre" in (r1 or "")) or ("Coperto da" in (r2 or "")), \
            f"Neither forward nor inverse relation present after roundtrip: r1={r1!r} r2={r2!r}"
