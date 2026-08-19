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


def vault_relative(path: pathlib.PurePath, root: pathlib.PurePath) -> str:
    """A corpus-relative path as it is stored in the index.

    Always forward slashes, whatever the platform. The index is built once and
    pulled by every client, so a path written on one operating system is read on
    another. A backslash here means a Windows client's lookups never match the
    index it just downloaded, and nothing errors: supersede links, backlinks and
    staleness simply stop finding anything.
    """
    return path.relative_to(root).as_posix()
