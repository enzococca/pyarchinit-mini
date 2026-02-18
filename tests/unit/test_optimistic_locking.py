"""Test optimistic locking on API update endpoints."""
from pyarchinit_mini.database.concurrency_manager import ConcurrencyManager, ID_FIELD_MAPPINGS


def test_concurrency_manager_id_field_mappings():
    """Test that ID field mappings cover expected tables."""
    assert ID_FIELD_MAPPINGS['site_table'] == 'id_sito'
    assert ID_FIELD_MAPPINGS['us_table'] == 'id_us'
    assert ID_FIELD_MAPPINGS['inventario_materiali_table'] == 'id_invmat'


def test_concurrency_manager_unknown_table():
    """Test that unknown table returns None for conflict check."""
    from unittest.mock import MagicMock
    mock_conn = MagicMock()
    cm = ConcurrencyManager(mock_conn)
    result = cm.check_version_conflict('nonexistent_table', 1, 1)
    assert result is None


def test_concurrency_manager_lock_unknown_table():
    """Test lock_record returns False for unknown table."""
    from unittest.mock import MagicMock
    mock_conn = MagicMock()
    cm = ConcurrencyManager(mock_conn)
    result = cm.lock_record('nonexistent_table', 1, 'user')
    assert result is False


def test_if_match_header_import():
    """Test that updated endpoints import correctly."""
    from pyarchinit_mini.api.site import update_site
    from pyarchinit_mini.api.us import update_us
    from pyarchinit_mini.api.inventario import update_inventario_item
    # Just verify the functions exist and are callable
    assert callable(update_site)
    assert callable(update_us)
    assert callable(update_inventario_item)
