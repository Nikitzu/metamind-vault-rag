"""Skip-dir filtering: .trash (scribe soft-delete target), .obsidian, and
.metalmind-stack must never be indexed. Regression for trashed notes
outranking live ones in recall after a scribe delete."""

from __future__ import annotations

from pathlib import Path, PurePath

from metamind_vault_rag.core import SKIP_DIRS, in_skip_dir
from metamind_vault_rag.watcher import _md_change


def test_skip_dirs_cover_trash() -> None:
    assert ".trash" in SKIP_DIRS


def test_in_skip_dir_matches_any_path_segment() -> None:
    assert in_skip_dir(PurePath(".trash/2026-07-19__note.md"))
    assert in_skip_dir(PurePath("/vault/.trash/nested/deep.md"))
    assert in_skip_dir(PurePath(".obsidian/workspace.md"))
    assert not in_skip_dir(PurePath("Plans/2026-07-19-topic.md"))
    assert not in_skip_dir(PurePath("Learnings/trash-handling-notes.md"))


def test_md_change_ignores_trash_moves() -> None:
    assert not _md_change("/vault/.trash/2026-07-19__note.md")
    assert not _md_change("/vault/.obsidian/anything.md")
    assert not _md_change("/vault/Plans/live-note.txt")
    assert _md_change("/vault/Plans/live-note.md")


def test_skip_dirs_cover_a_repository_corpus() -> None:
    """A corpus is often a git repository, which carries markdown that is not
    corpus. A dependency's README says nothing about the project holding it,
    and there are typically ten times more of them than real documents."""
    for name in ("node_modules", ".git", "dist", "build", "target", "vendor"):
        assert name in SKIP_DIRS


def test_a_dependency_readme_is_not_indexed() -> None:
    assert in_skip_dir(PurePath("node_modules/commander/README.md"))
    assert in_skip_dir(PurePath("/work/knowledge/node_modules/zod/README.md"))
    assert in_skip_dir(PurePath("target/generated-docs/api.md"))


def test_a_document_that_merely_mentions_a_skipped_name_is_kept() -> None:
    assert not in_skip_dir(PurePath("systems/node_modules-hygiene.md"))
    assert not in_skip_dir(PurePath("decisions/how-we-build-dist-artifacts.md"))
