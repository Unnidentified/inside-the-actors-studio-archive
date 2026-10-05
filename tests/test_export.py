"""Tests for the export and rendering helpers."""

from __future__ import annotations

import csv
import io
import json
from datetime import date

from itas.export import format_size, to_csv, to_json, to_path_list, write_exports
from itas.model import Episode, EpisodeCode
from itas.render import render_checklist


class TestFormatSize:
    def test_handles_none(self):
        assert format_size(None) == "N/A"

    def test_formats_bytes(self):
        assert format_size(512) == "512 B"

    def test_formats_megabytes(self):
        assert format_size(1024 * 1024) == "1.00 MB"

    def test_formats_gigabytes(self):
        assert format_size(5 * 1024**3) == "5.00 GB"


class TestExports:
    def test_json_round_trips(self, entry_factory):
        entries = [entry_factory("S01E01.PaulNewman-1994.06.12.ITAS.SD.mp4")]
        payload = json.loads(to_json(entries))
        assert payload[0]["name"] == "S01E01.PaulNewman-1994.06.12.ITAS.SD.mp4"
        assert payload[0]["size_formatted"] == "1.00 KB"

    def test_csv_has_stable_columns(self, entry_factory):
        entries = [entry_factory("S01E01.PaulNewman-1994.06.12.ITAS.SD.mp4")]
        rows = list(csv.DictReader(io.StringIO(to_csv(entries))))
        assert list(rows[0]) == [
            "id",
            "name",
            "path",
            "is_directory",
            "mime_type",
            "size_bytes",
            "size_formatted",
            "modified_time",
        ]

    def test_path_list_includes_directories_with_a_trailing_slash(self, entry_factory):
        entries = [
            entry_factory("Season 01", is_directory=True),
            entry_factory("S01E01.PaulNewman-1994.06.12.ITAS.SD.mp4"),
        ]
        assert to_path_list(entries) == (
            "Season 01/\nSeason 01/S01E01.PaulNewman-1994.06.12.ITAS.SD.mp4\n"
        )

    def test_path_list_can_skip_directories(self, entry_factory):
        entries = [
            entry_factory("Season 01", is_directory=True),
            entry_factory("S01E01.PaulNewman-1994.06.12.ITAS.SD.mp4"),
        ]
        assert to_path_list(entries, files_only=True) == (
            "Season 01/S01E01.PaulNewman-1994.06.12.ITAS.SD.mp4\n"
        )

    def test_write_exports_creates_three_files(self, tmp_path, entry_factory):
        entries = [entry_factory("S01E01.PaulNewman-1994.06.12.ITAS.SD.mp4")]
        outputs = write_exports(entries, tmp_path)
        assert set(outputs) == {"json", "csv", "txt"}
        for path in outputs.values():
            assert path.exists()


class TestRenderChecklist:
    def test_marks_missing_episodes(self, entry_factory):
        episodes = [
            Episode(EpisodeCode(1, 1), "Paul Newman", date(1994, 6, 12)),
            Episode(EpisodeCode(1, 2), "Alec Baldwin", date(1994, 6, 18)),
        ]
        entries = [entry_factory("S01E01.PaulNewman-1994.06.12.ITAS.SD.mp4")]
        checklist = render_checklist(episodes, entries)
        assert "* S01E01 - Paul Newman" in checklist
        assert "* ~~S01E02 - Alec Baldwin~~" in checklist

    def test_groups_by_season(self, entry_factory):
        episodes = [
            Episode(EpisodeCode(1, 1), "Paul Newman", date(1994, 6, 12)),
            Episode(EpisodeCode(2, 1), "Lee Grant", date(1995, 1, 1)),
        ]
        checklist = render_checklist(episodes, [])
        assert "**Season 1**" in checklist
        assert "**Season 2**" in checklist

    def test_lists_specials_with_labels(self, entry_factory):
        entries = [entry_factory("S00E02.100thEpisode-2001.08.19.ITAS.SD.mp4")]
        checklist = render_checklist([], entries)
        assert "* S00E02 - 100th Episode Special" in checklist

    def test_can_omit_specials(self, entry_factory):
        entries = [entry_factory("S00E02.100thEpisode-2001.08.19.ITAS.SD.mp4")]
        assert "Season 0" not in render_checklist([], entries, include_specials=False)
