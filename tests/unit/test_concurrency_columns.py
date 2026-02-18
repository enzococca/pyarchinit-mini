"""Test that concurrency columns exist on all models."""
import pytest
from pyarchinit_mini.models.base import BaseModel
from pyarchinit_mini.models.site import Site
from pyarchinit_mini.models.us import US
from pyarchinit_mini.models.inventario_materiali import InventarioMateriali


def test_base_model_has_concurrency_columns():
    """BaseModel must declare the 7 concurrency columns."""
    expected = [
        'entity_uuid', 'version_number', 'last_modified_by',
        'last_modified_timestamp', 'sync_status', 'editing_by', 'editing_since'
    ]
    for col in expected:
        assert hasattr(BaseModel, col), f"BaseModel missing column: {col}"


def test_site_inherits_concurrency_columns(temp_db):
    """Site table must have concurrency columns in the DB."""
    from sqlalchemy import inspect as sa_inspect
    inspector = sa_inspect(temp_db.engine)
    columns = [c['name'] for c in inspector.get_columns('site_table')]
    for col in ['entity_uuid', 'version_number', 'sync_status']:
        assert col in columns, f"site_table missing column: {col}"


def test_entity_uuid_auto_generated(temp_db, db_manager, sample_site_data):
    """New records should get an auto-generated entity_uuid."""
    from pyarchinit_mini.models.site import Site
    site = db_manager.create(Site, sample_site_data)
    assert site.entity_uuid is not None
    assert len(site.entity_uuid) == 36  # UUID v4 format


def test_version_number_defaults_to_one(temp_db, db_manager, sample_site_data):
    """New records should have version_number=1."""
    from pyarchinit_mini.models.site import Site
    site = db_manager.create(Site, sample_site_data)
    assert site.version_number == 1
