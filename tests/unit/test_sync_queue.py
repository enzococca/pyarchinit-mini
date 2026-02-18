"""Test sync queue."""
import tempfile
import os
from pyarchinit_mini.stratigraph.sync_queue import SyncQueue, QueueEntry


def test_enqueue_and_dequeue():
    with tempfile.TemporaryDirectory() as tmpdir:
        q = SyncQueue(db_path=os.path.join(tmpdir, "queue.sqlite"))
        entry_id = q.enqueue("/path/to/bundle.zip", "abc123hash")
        assert entry_id > 0

        entry = q.dequeue()
        assert entry is not None
        assert entry.bundle_path == "/path/to/bundle.zip"
        assert entry.status == "uploading"
        assert entry.attempts == 1


def test_mark_completed():
    with tempfile.TemporaryDirectory() as tmpdir:
        q = SyncQueue(db_path=os.path.join(tmpdir, "queue.sqlite"))
        entry_id = q.enqueue("/path/bundle.zip", "hash123")
        entry = q.dequeue()
        q.mark_completed(entry.id)
        stats = q.get_stats()
        assert stats["completed"] == 1
        assert stats["pending"] == 0


def test_mark_failed_retries():
    with tempfile.TemporaryDirectory() as tmpdir:
        q = SyncQueue(db_path=os.path.join(tmpdir, "queue.sqlite"))
        entry_id = q.enqueue("/path/bundle.zip", "hash123")
        entry = q.dequeue()
        q.mark_failed(entry.id, "Network error")
        # Should be back to pending (attempts < MAX_ATTEMPTS)
        stats = q.get_stats()
        assert stats["pending"] == 1


def test_get_stats():
    with tempfile.TemporaryDirectory() as tmpdir:
        q = SyncQueue(db_path=os.path.join(tmpdir, "queue.sqlite"))
        q.enqueue("/a.zip", "h1")
        q.enqueue("/b.zip", "h2")
        stats = q.get_stats()
        assert stats["pending"] == 2
