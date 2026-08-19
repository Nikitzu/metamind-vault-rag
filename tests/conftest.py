"""Keep the suite out of the developer's real home directory.

Several modules resolve paths through `Path.home()`: the index stamp, the
calibration sidecar, the recall token, the watcher log. A test that exercises a
startup path without stubbing every one of them writes into a live install
instead of a temporary directory.

That is not hypothetical. Adding one call to the watcher's startup was enough to
make an existing, fully-stubbed-looking test write a stamp carrying a fake
embedder into a real state directory. Stubbing each path per test is the version
of this that keeps failing, because the leak arrives with the next call added
upstream of a test that never mentioned it.
"""

import pytest


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    home = tmp_path / "home"
    monkeypatch.delenv("VAULT_STATE_DIR", raising=False)
    (home / ".vault-rag").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setattr("pathlib.Path.home", lambda: home)
    return home
