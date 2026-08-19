"""The engine has more than one consumer and must not hardcode either one's name.

The state directory is where indexes, caches, logs and the recall token live.
A client that wants the historical location sets VAULT_STATE_DIR to it.
"""

import pathlib

import pytest


def test_default_is_neutral(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VAULT_STATE_DIR", raising=False)
    monkeypatch.setattr(pathlib.Path, "home", classmethod(lambda cls: pathlib.Path("/home/tester")))
    from metamind_vault_rag.paths import state_dir

    assert state_dir() == pathlib.Path("/home/tester/.vault-rag")


def test_env_var_overrides_the_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VAULT_STATE_DIR", "/tmp/tzmem-state")
    from metamind_vault_rag.paths import state_dir

    assert state_dir() == pathlib.Path("/tmp/tzmem-state")


def test_a_client_can_keep_the_historical_location(monkeypatch: pytest.MonkeyPatch) -> None:
    """metalmind adopts this package by setting one variable, with no migration."""
    monkeypatch.setenv("VAULT_STATE_DIR", "/home/tester/.metalmind")
    from metamind_vault_rag.paths import state_dir

    assert state_dir() == pathlib.Path("/home/tester/.metalmind")


def test_tilde_in_the_override_is_expanded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VAULT_STATE_DIR", "~/.tzmem")
    monkeypatch.setattr(
        pathlib.Path, "expanduser", lambda self: pathlib.Path("/home/tester/.tzmem")
    )
    from metamind_vault_rag.paths import state_dir

    assert state_dir() == pathlib.Path("/home/tester/.tzmem")
