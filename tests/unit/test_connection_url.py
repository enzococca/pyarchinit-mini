import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from pyarchinit_mini.graphproj.connection_url import connection_url_from_session
from pyarchinit_mini.graphproj.exceptions import ProjectionError


def test_sqlite_file_becomes_absolute_file_url(tmp_path):
    db = tmp_path / "x.db"
    with Session(create_engine(f"sqlite:///{db}")) as s:
        assert connection_url_from_session(s) == f"sqlite:///{db.resolve()}"


def test_relative_sqlite_path_is_made_absolute(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with Session(create_engine("sqlite:///rel.db")) as s:
        assert connection_url_from_session(s) == f"sqlite:///{(tmp_path / 'rel.db').resolve()}"


def test_in_memory_sqlite_is_rejected():
    with Session(create_engine("sqlite://")) as s:
        with pytest.raises(ProjectionError):
            connection_url_from_session(s)


def test_postgres_url_keeps_password_and_driver():
    url = "postgresql+psycopg2://u:p%40ss@db.example:5432/mini"
    with Session(create_engine(url)) as s:   # no connection is opened
        assert connection_url_from_session(s) == url


def test_other_backends_are_rejected():
    pytest.importorskip("pymysql")
    with Session(create_engine("mysql+pymysql://u:p@h/db")) as s:
        with pytest.raises(ProjectionError):
            connection_url_from_session(s)
