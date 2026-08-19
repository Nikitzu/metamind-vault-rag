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


def test_every_consumer_follows_the_override(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """One override must move all of them. A consumer left on its own default
    would write one client's data into another client's directory."""
    monkeypatch.setenv("VAULT_STATE_DIR", str(tmp_path))

    from metamind_vault_rag.backends.fastembed_backend import resolve_cache_dir
    from metamind_vault_rag.calibration import sidecar_path
    from metamind_vault_rag.index_format import stamp_path

    assert stamp_path("vault").parent == tmp_path
    assert sidecar_path("vault").parent == tmp_path
    assert pathlib.Path(resolve_cache_dir()) == tmp_path / "cache" / "fastembed"


def test_no_module_hardcodes_a_state_directory() -> None:
    """paths.py is the only place a state directory name may appear."""
    root = pathlib.Path(__file__).resolve().parent.parent / "metamind_vault_rag"
    offenders = []
    for py in root.rglob("*.py"):
        if py.name == "paths.py":
            continue
        for i, line in enumerate(py.read_text().splitlines(), 1):
            if '".metalmind"' in line or "'.metalmind'" in line:
                offenders.append(f"{py.relative_to(root)}:{i}")
            if '".vault-rag"' in line or "'.vault-rag'" in line:
                offenders.append(f"{py.relative_to(root)}:{i}")
    assert offenders == [], f"hardcoded state dir: {offenders}"


def test_no_module_names_a_client_in_user_facing_text() -> None:
    """The engine has more than one client. Telling one of them to run
    another's command sends a user to a binary they have not installed."""
    root = pathlib.Path(__file__).resolve().parent.parent / "metamind_vault_rag"
    allowed = {".metalmind-stack"}
    offenders = []
    for py in root.rglob("*.py"):
        for i, line in enumerate(py.read_text().splitlines(), 1):
            if "metalmind" not in line.lower():
                continue
            if any(token in line for token in allowed):
                continue
            offenders.append(f"{py.relative_to(root)}:{i}: {line.strip()}")
    assert offenders == [], "client name in engine text:\n" + "\n".join(offenders)
