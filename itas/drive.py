"""Google Drive access for the archive.

Two backends are supported:

``api``
    The public Drive REST API v3 with an API key. This is what most people
    will use; set ``GDRIVE_API_KEY`` and pass the folder URL.

``snapshot``
    Read a previously exported snapshot from disk. Useful for offline work,
    CI, and reviewing a change without hitting the network.

Both produce the same :class:`~itas.model.ArchiveEntry` records.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .model import ArchiveEntry, DataError

API_ROOT = "https://www.googleapis.com/drive/v3/files"
FOLDER_MIME = "application/vnd.google-apps.folder"
DEFAULT_TIMEOUT = 30


def extract_folder_id(url_or_id: str) -> str:
    """Return the folder id from a Drive URL, or the value if it is one."""
    value = url_or_id.strip()
    for pattern in (r"folders/([A-Za-z0-9_-]+)", r"id=([A-Za-z0-9_-]+)"):
        match = re.search(pattern, value)
        if match:
            return match.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{10,}", value):
        return value
    raise DataError(f"could not find a Drive folder id in {url_or_id!r}")


class DriveClient:
    """Minimal Drive v3 client for public folders."""

    def __init__(self, api_key: str, *, timeout: int = DEFAULT_TIMEOUT) -> None:
        if not api_key:
            raise DataError("a Google Drive API key is required (set GDRIVE_API_KEY)")
        self.api_key = api_key
        self.timeout = timeout

    def list_children(self, folder_id: str) -> list[dict[str, Any]]:
        """List every non-trashed child of a folder, following pagination."""
        items: list[dict[str, Any]] = []
        page_token: str | None = None
        while True:
            params = {
                "q": f"'{folder_id}' in parents and trashed = false",
                "key": self.api_key,
                "fields": "nextPageToken, files(id, name, mimeType, size, modifiedTime)",
                "pageSize": 1000,
                "supportsAllDrives": "true",
                "includeItemsFromAllDrives": "true",
            }
            if page_token:
                params["pageToken"] = page_token
            payload = self._get(params)
            items.extend(payload.get("files", []))
            page_token = payload.get("nextPageToken")
            if not page_token:
                return items

    def _get(self, params: dict[str, str]) -> dict[str, Any]:
        url = f"{API_ROOT}?{urllib.parse.urlencode(params)}"
        request = urllib.request.Request(url, headers={"User-Agent": "itas-archive/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise DataError(f"Drive API returned HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise DataError(f"could not reach the Drive API: {exc.reason}") from exc

    def index(self, root_id: str) -> list[ArchiveEntry]:
        """Walk a folder tree and return a flat list of entries."""
        entries: list[ArchiveEntry] = []
        self._walk(root_id, "", entries)
        entries.sort(key=lambda e: e.path)
        return entries

    def _walk(self, folder_id: str, prefix: str, out: list[ArchiveEntry]) -> None:
        for item in self.list_children(folder_id):
            name = item.get("name", "unnamed")
            path = f"{prefix}/{name}" if prefix else name
            is_directory = item.get("mimeType") == FOLDER_MIME
            raw_size = item.get("size")
            out.append(
                ArchiveEntry(
                    id=item["id"],
                    name=name,
                    path=path,
                    is_directory=is_directory,
                    mime_type=item.get("mimeType", ""),
                    size_bytes=int(raw_size) if raw_size is not None else None,
                    modified_time=item.get("modifiedTime"),
                )
            )
            if is_directory:
                self._walk(item["id"], path, out)
