"""Paths stored in the index must read the same on every platform.

The index is built once, in continuous integration, and pulled by clients on
Linux, macOS and Windows. A path written with a backslash means a Windows
client's lookups never match the index it just downloaded, and nothing errors:
supersede links, backlinks and staleness quietly stop finding anything.
"""

import pathlib

from metamind_vault_rag.paths import vault_relative


def test_a_nested_path_is_stored_with_forward_slashes() -> None:
    root = pathlib.PurePath("/corpus")
    assert vault_relative(pathlib.PurePosixPath("/corpus/Work/old.md"), root) == "Work/old.md"


def test_a_windows_style_path_is_normalised_too() -> None:
    root = pathlib.PureWindowsPath(r"C:\corpus")
    file = pathlib.PureWindowsPath(r"C:\corpus\Work\old.md")
    assert vault_relative(file, root) == "Work/old.md"


def test_a_file_at_the_root_keeps_its_name() -> None:
    root = pathlib.PurePosixPath("/corpus")
    assert vault_relative(pathlib.PurePosixPath("/corpus/README.md"), root) == "README.md"


def test_a_deeply_nested_path_keeps_every_segment() -> None:
    root = pathlib.PureWindowsPath(r"C:\corpus")
    file = pathlib.PureWindowsPath(r"C:\corpus\a\b\c\d.md")
    assert vault_relative(file, root) == "a/b/c/d.md"


def test_no_stored_path_ever_contains_a_backslash() -> None:
    root = pathlib.PureWindowsPath(r"C:\corpus")
    file = pathlib.PureWindowsPath(r"C:\corpus\Work\MOCs\index.md")
    assert "\\" not in vault_relative(file, root)


def test_the_two_platforms_agree_on_the_same_logical_file() -> None:
    """The point of the whole exercise: one corpus, two machines, one string."""
    posix = vault_relative(pathlib.PurePosixPath("/corpus/Work/old.md"), pathlib.PurePosixPath("/corpus"))
    windows = vault_relative(
        pathlib.PureWindowsPath(r"C:\corpus\Work\old.md"), pathlib.PureWindowsPath(r"C:\corpus")
    )
    assert posix == windows
