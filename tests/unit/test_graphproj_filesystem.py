import threading
import time
from pathlib import Path
import pytest

from pyarchinit_mini.graphproj.filesystem import (
    atomic_write,
    paradata_flock,
    slugify,
    paradata_dir,
)


def test_atomic_write_creates_file(tmp_path):
    target = tmp_path / "x.txt"
    atomic_write("hello", target)
    assert target.read_text() == "hello"
    assert not (tmp_path / "x.txt.tmp").exists()


def test_atomic_write_overwrites_existing(tmp_path):
    target = tmp_path / "x.txt"
    target.write_text("old")
    atomic_write("new", target)
    assert target.read_text() == "new"


def test_atomic_write_does_not_leave_tmp_on_success(tmp_path):
    target = tmp_path / "x.txt"
    atomic_write("hello", target)
    assert list(tmp_path.glob("*.tmp")) == []


def test_slugify_basic():
    assert slugify("Volterra") == "volterra"
    assert slugify("Sito Archeologico di Esempio") == "sito-archeologico-di-esempio"
    assert slugify("Metro C / Roma 2026") == "metro-c-roma-2026"


def test_slugify_rejects_empty():
    with pytest.raises(ValueError):
        slugify("")


def test_paradata_dir_returns_under_root(tmp_path):
    d = paradata_dir("Volterra", root=tmp_path)
    assert d == tmp_path / "volterra"


def test_flock_serializes_writers(tmp_path):
    results = []

    def writer(value: int) -> None:
        with paradata_flock("X", root=tmp_path):
            time.sleep(0.05)
            results.append(value)

    threads = [threading.Thread(target=writer, args=(i,)) for i in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(results) == [0, 1, 2, 3]
