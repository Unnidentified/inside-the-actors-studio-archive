"""Shared pytest fixtures."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from itas.model import ArchiveEntry, Episode, EpisodeCode

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def wikitext(repo_root: Path) -> str:
    return (repo_root / "data" / "wikipedia_itas.wikitext").read_text(encoding="utf-8")


@pytest.fixture
def episode() -> Episode:
    return Episode(
        code=EpisodeCode(6, 10),
        guest="Philip Seymour Hoffman",
        air_date=date(2000, 6, 4),
    )


def make_entry(name: str, *, is_directory: bool = False, size: int = 1024) -> ArchiveEntry:
    """Build an archive entry with a plausible path for tests."""
    path = name if is_directory else f"Season 01/{name}"
    return ArchiveEntry(
        id=f"id-{name}",
        name=name,
        path=path,
        is_directory=is_directory,
        mime_type="application/vnd.google-apps.folder" if is_directory else "video/mp4",
        size_bytes=None if is_directory else size,
    )


@pytest.fixture
def entry_factory():
    return make_entry
