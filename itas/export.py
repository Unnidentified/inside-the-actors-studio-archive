"""Export helpers for the Drive snapshot.

The snapshot is stored as JSON and exported to CSV and a flat path list for
people who would rather work in a spreadsheet or a text editor.
"""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Sequence
from pathlib import Path

from .model import ArchiveEntry

CSV_COLUMNS = [
    "id",
    "name",
    "path",
    "is_directory",
    "mime_type",
    "size_bytes",
    "size_formatted",
    "modified_time",
]


def format_size(size_bytes: int | None) -> str:
    """Format a byte count the way a human would read it."""
    if size_bytes is None:
        return "N/A"
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024.0 or unit == "TB":
            return f"{size:.2f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024.0
    return f"{size:.2f} TB"  # pragma: no cover - unreachable


def to_json(entries: Sequence[ArchiveEntry]) -> str:
    return json.dumps([_as_dict(e) for e in entries], indent=2, ensure_ascii=False) + "\n"


def to_csv(entries: Sequence[ArchiveEntry]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for entry in entries:
        writer.writerow(_as_dict(entry))
    return buffer.getvalue()


def to_path_list(entries: Sequence[ArchiveEntry], *, files_only: bool = False) -> str:
    lines: list[str] = []
    for entry in entries:
        if files_only and entry.is_directory:
            continue
        suffix = "/" if entry.is_directory else ""
        lines.append(f"{entry.path}{suffix}")
    return "\n".join(lines) + "\n"


def write_exports(entries: Sequence[ArchiveEntry], directory: Path | str) -> dict[str, Path]:
    """Write JSON, CSV and TXT exports into ``directory``."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    outputs = {
        "json": directory / "drive_snapshot.json",
        "csv": directory / "drive_snapshot.csv",
        "txt": directory / "drive_snapshot_files.txt",
    }
    outputs["json"].write_text(to_json(entries), encoding="utf-8")
    outputs["csv"].write_text(to_csv(entries), encoding="utf-8")
    outputs["txt"].write_text(to_path_list(entries, files_only=True), encoding="utf-8")
    return outputs


def _as_dict(entry: ArchiveEntry) -> dict[str, object]:
    return {
        "id": entry.id,
        "name": entry.name,
        "path": entry.path,
        "is_directory": entry.is_directory,
        "mime_type": entry.mime_type,
        "size_bytes": entry.size_bytes,
        "size_formatted": format_size(entry.size_bytes),
        "modified_time": entry.modified_time,
    }
