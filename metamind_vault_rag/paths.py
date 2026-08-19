"""Filesystem locations the engine owns.

The engine is consumed by more than one client, so the directory holding
indexes, caches, logs and the recall token is configurable through
VAULT_STATE_DIR. The default names no client. A client with an existing
installation elsewhere sets the variable and needs no migration.
"""

import os
import pathlib

DEFAULT_STATE_DIR_NAME = ".vault-rag"


def state_dir() -> pathlib.Path:
    override = os.environ.get("VAULT_STATE_DIR")
    if override:
        return pathlib.Path(override).expanduser()
    return pathlib.Path.home() / DEFAULT_STATE_DIR_NAME
