"""Test concurrency manager - optimistic locking + soft locks."""
from pyarchinit_mini.models.site import Site
from pyarchinit_mini.database.concurrency_manager import ConcurrencyManager


def test_check_no_conflict(temp_db, db_manager, sample_site_data):
    site = db_manager.create(Site, sample_site_data)
    cm = ConcurrencyManager(temp_db)
    conflict = cm.check_version_conflict('site_table', site.id_sito, site.version_number)
    assert conflict is None


def test_check_version_conflict(temp_db, db_manager, sample_site_data):
    site = db_manager.create(Site, sample_site_data)
    cm = ConcurrencyManager(temp_db)
    conflict = cm.check_version_conflict('site_table', site.id_sito, 0)
    assert conflict is not None
    assert conflict["current_version"] == 1


def test_lock_and_unlock_record(temp_db, db_manager, sample_site_data):
    site = db_manager.create(Site, sample_site_data)
    cm = ConcurrencyManager(temp_db)
    assert cm.lock_record('site_table', site.id_sito, 'test_user') is True
    editors = cm.get_active_editors('site_table')
    assert any(e["record_id"] == site.id_sito for e in editors)
    assert cm.unlock_record('site_table', site.id_sito, 'test_user') is True


def test_lock_record_already_locked(temp_db, db_manager, sample_site_data):
    site = db_manager.create(Site, sample_site_data)
    cm = ConcurrencyManager(temp_db)
    cm.lock_record('site_table', site.id_sito, 'user_a')
    assert cm.lock_record('site_table', site.id_sito, 'user_b') is False


def test_increment_version(temp_db, db_manager, sample_site_data):
    site = db_manager.create(Site, sample_site_data)
    cm = ConcurrencyManager(temp_db)
    cm.increment_version('site_table', site.id_sito, 'editor')
    conflict = cm.check_version_conflict('site_table', site.id_sito, 1)
    assert conflict is not None
    assert conflict["current_version"] == 2
