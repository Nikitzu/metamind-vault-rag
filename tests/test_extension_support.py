"""The vector store is a SQLite extension, and not every Python can load one.

Python built with --disable-loadable-sqlite-extensions raises AttributeError
deep inside a connection open, which tells the reader nothing about what to do.
"""

import sqlite3

import pytest

from metamind_vault_rag.stores import sqlite_vec_store


def test_this_interpreter_supports_extensions() -> None:
    """If this fails, the suite below is running somewhere the store cannot
    work, which is worth knowing explicitly rather than through ten errors."""
    assert sqlite_vec_store.extensions_supported()


def test_support_is_read_off_the_connection_class() -> None:
    assert sqlite_vec_store.extensions_supported() == hasattr(
        sqlite3.Connection, "enable_load_extension"
    )


def test_requiring_support_is_silent_when_it_is_there() -> None:
    sqlite_vec_store.require_extension_support()


def test_the_error_names_the_cause_and_a_way_out(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sqlite_vec_store, "extensions_supported", lambda: False)
    with pytest.raises(RuntimeError) as info:
        sqlite_vec_store.require_extension_support()

    message = str(info.value)
    assert "disable-loadable-sqlite-extensions" in message
    assert "uv python install" in message


def test_the_error_arrives_before_the_attribute_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Opening a store on such an interpreter must say why, not fail with
    AttributeError from inside sqlite3."""
    monkeypatch.setattr(sqlite_vec_store, "extensions_supported", lambda: False)
    with pytest.raises(RuntimeError):
        sqlite_vec_store.require_extension_support()
