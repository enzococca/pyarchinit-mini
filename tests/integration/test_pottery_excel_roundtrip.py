"""Excel and CSV export/import round-trip tests for pottery."""
import io
from openpyxl import load_workbook

# Re-use the flask_app + client + pottery_service fixtures from the other test file
from tests.integration.test_pottery_routes import flask_app, client, pottery_service


def test_excel_export_returns_xlsx(client, pottery_service):
    pottery_service.create_pottery({"sito": "X", "form": "Olla", "fabric": "Coarse", "qty": 1})
    r = client.get("/export/pottery/excel")
    assert r.status_code == 200
    assert r.headers["Content-Type"].startswith("application/")
    wb = load_workbook(io.BytesIO(r.data))
    assert "pottery" in wb.sheetnames


def test_csv_export(client, pottery_service):
    pottery_service.create_pottery({"sito": "X", "form": "Olla"})
    r = client.get("/export/pottery/csv")
    assert r.status_code == 200
    body = r.data.decode("utf-8")
    assert "sito" in body and "Olla" in body
