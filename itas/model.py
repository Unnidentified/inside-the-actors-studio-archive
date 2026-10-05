"""Shared data model for episodes and archive entries.

Everything downstream works with two small records:

``Episode``
    A canonical series episode as listed by Wikipedia (season, episode,
    air date, guest).

``ArchiveEntry``
    A single file or folder in the public Google Drive archive.

Keeping these as plain dataclasses rather than raw dicts means the audit
code reads like prose and the tests can build fixtures without ceremony.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

# Matches the leading "S06E10" of a canonical filename.
EPISODE_CODE_RE = re.compile(r"^S(\d{2,3})E(\d{2,3})", re.IGNORECASE)

# Wikipedia writes dates as "June 12, 1994".
_WIKI_DATE_RE = re.compile(r"^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$")


class DataError(ValueError):
    """Raised when a data file cannot be parsed or is internally inconsistent."""


@dataclass(frozen=True, order=True)
class EpisodeCode:
    """A (season, episode) pair. Season 0 holds specials and extras."""

    season: int
    episode: int

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"S{self.season:02d}E{self.episode:02d}"

    @classmethod
    def from_filename(cls, name: str) -> EpisodeCode | None:
        """Return the code a filename starts with, or ``None``.

        Files such as ``S00E09-E15.RobinWilliamsExtrasCombined...`` map to
        the first episode of the range; the range itself is preserved in
        the filename and is not modelled here.
        """
        match = EPISODE_CODE_RE.match(name)
        if not match:
            return None
        return cls(int(match.group(1)), int(match.group(2)))


@dataclass(frozen=True)
class Episode:
    """A canonical series episode, as listed by Wikipedia."""

    code: EpisodeCode
    guest: str
    air_date: date

    @property
    def year(self) -> int:
        return self.air_date.year

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Episode:
        try:
            code = EpisodeCode(int(raw["season"]), int(raw["episode"]))
            guest = str(raw["guest"]).strip()
            air_date = parse_wiki_date(str(raw["air_date"]))
        except KeyError as exc:
            raise DataError(f"episode record missing field {exc}") from exc
        if not guest:
            raise DataError(f"{code}: empty guest name")
        return cls(code=code, guest=guest, air_date=air_date)


@dataclass(frozen=True)
class ArchiveEntry:
    """One file or folder in the Drive archive."""

    id: str
    name: str
    path: str
    is_directory: bool
    mime_type: str = ""
    size_bytes: int | None = None
    modified_time: str | None = None

    @property
    def code(self) -> EpisodeCode | None:
        if self.is_directory:
            return None
        return EpisodeCode.from_filename(self.name)

    @property
    def extension(self) -> str:
        return Path(self.name).suffix.lower().lstrip(".")

    @property
    def is_video(self) -> bool:
        return self.extension in VIDEO_EXTENSIONS

    @property
    def size_gb(self) -> float:
        return (self.size_bytes or 0) / 1024**3

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> ArchiveEntry:
        try:
            return cls(
                id=str(raw["id"]),
                name=str(raw["name"]),
                path=str(raw["path"]),
                is_directory=bool(raw["is_directory"]),
                mime_type=str(raw.get("mime_type") or ""),
                size_bytes=raw.get("size_bytes"),
                modified_time=raw.get("modified_time"),
            )
        except KeyError as exc:
            raise DataError(f"archive entry missing field {exc}") from exc


VIDEO_EXTENSIONS = frozenset({"mp4", "mkv", "avi", "mov", "m4v", "webm", "mpg", "mpeg", "wmv", "flv", "ts", "m2ts"})


def parse_wiki_date(text: str) -> date:
    """Parse a Wikipedia-style date such as ``June 12, 1994``."""
    match = _WIKI_DATE_RE.match(text.strip())
    if not match:
        raise DataError(f"unrecognised air date: {text!r}")
    month_name, day, year = match.groups()
    try:
        return datetime.strptime(f"{month_name} {day} {year}", "%B %d %Y").date()
    except ValueError as exc:
        raise DataError(f"unrecognised air date: {text!r}") from exc


def load_episodes(path: Path | str) -> list[Episode]:
    """Load the canonical episode list."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise DataError(f"{path}: expected a JSON list")
    episodes = [Episode.from_json(item) for item in raw]
    seen: set[EpisodeCode] = set()
    for episode in episodes:
        if episode.code in seen:
            raise DataError(f"{path}: duplicate episode {episode.code}")
        seen.add(episode.code)
    return episodes


def load_archive(path: Path | str) -> list[ArchiveEntry]:
    """Load a Drive archive snapshot."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise DataError(f"{path}: expected a JSON list")
    entries = [ArchiveEntry.from_json(item) for item in raw]
    seen_ids: set[str] = set()
    for entry in entries:
        if entry.id in seen_ids:
            raise DataError(f"{path}: duplicate file id {entry.id}")
        seen_ids.add(entry.id)
    return entries


def group_by_code(entries: Iterable[ArchiveEntry]) -> dict[EpisodeCode, list[ArchiveEntry]]:
    """Group files by episode code, ignoring folders and unparsable names."""
    grouped: dict[EpisodeCode, list[ArchiveEntry]] = {}
    for entry in entries:
        code = entry.code
        if code is None:
            continue
        grouped.setdefault(code, []).append(entry)
    return grouped


def iter_files(entries: Iterable[ArchiveEntry]) -> Iterator[ArchiveEntry]:
    return (entry for entry in entries if not entry.is_directory)
