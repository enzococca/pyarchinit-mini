"""pottery_list pre-loads media via MediaService.get_media_for_entity_ids."""
from pathlib import Path
import pytest

from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.models.base import Base
from pyarchinit_mini.models.site import Site
from pyarchinit_mini.models.pottery import Pottery
from pyarchinit_mini.services.media_service import MediaService


@pytest.fixture
def db_manager(tmp_path):
    db = tmp_path / "media_batch.db"
    conn = DatabaseConnection.from_url(f"sqlite:///{db}")
    Base.metadata.create_all(conn.engine)
    return DatabaseManager(conn)


def test_get_media_for_entity_ids_empty_input(db_manager):
    svc = MediaService(db_manager)
    out = svc.get_media_for_entity_ids("pottery", [])
    assert out == {}


def test_get_media_for_entity_ids_returns_dict_by_id(db_manager):
    """With no rows in media_table, every id maps to an empty list."""
    svc = MediaService(db_manager)
    out = svc.get_media_for_entity_ids("pottery", [1, 2, 3])
    assert out == {1: [], 2: [], 3: []}
