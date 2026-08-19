"""Paths stored in the index must read the same on every platform.

The index is built once, in continuous integration, and pulled by clients on
Linux, macOS and Windows. A path written with a backslash means a Windows
client's lookups never match the index it just downloaded, and nothing errors:
supersede links, backlinks and staleness quietly stop finding anything.
"""

import pathlib

from metamind_vault_rag.paths import vault_relative


def test_a_nested_path_is_stored_with_forward_slashes() -> None:
    # PurePosixPath on both sides. PurePath resolves to the running platform's
    # flavour, so on Windows this compared a posix path against a windows root.
    root = pathlib.PurePosixPath("/corpus")
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


def test_a_recalled_note_is_not_reported_as_never_recalled(tmp_path, monkeypatch) -> None:
    """The stale report asks the recall log whether a note was ever used, and
    the log's keys come out of the index, forward-slashed. A native separator
    here reports every note as never recalled on Windows: not an error, just a
    report that is wrong about everything."""
    import os
    import time

    from metamind_vault_rag import doctor

    monkeypatch.setattr(doctor, "VAULT", tmp_path)
    note = tmp_path / "Work" / "old.md"
    note.parent.mkdir(parents=True)
    note.write_text("body\n", encoding="utf-8")
    old = time.time() - 120 * 86400
    os.utime(note, (old, old))

    entries = doctor.collect_stale_vault(days=90, recalled={"Work/old.md"})

    assert [rel for _, rel, _ in entries] == ["Work/old.md"]
    assert entries[0][2] is False, "a note present in the recall log is not never-recalled"
