"""Tests for the data model and date parsing."""

from __future__ import annotations

from datetime import date

import pytest

from itas.model import (
    ArchiveEntry,
    DataError,
    Episode,
    EpisodeCode,
    group_by_code,
    iter_files,
    parse_wiki_date,
)


class TestEpisodeCode:
    def test_formats_with_zero_padding(self):
        assert str(EpisodeCode(6, 10)) == "S06E10"
        assert str(EpisodeCode(23, 8)) == "S23E08"

    @pytest.mark.parametrize(
        "name,expected",
        [
            ("S06E10.PhilipSeymourHoffman-2000.06.04.ITAS.SD.mp4", EpisodeCode(6, 10)),
            ("s01e01.paulnewman.mp4", EpisodeCode(1, 1)),
            ("S00E09-E15.RobinWilliamsExtrasCombined.ITAS.SD.mp4", EpisodeCode(0, 9)),
        ],
    )
    def test_parses_from_filename(self, name, expected):
        assert EpisodeCode.from_filename(name) == expected

    @pytest.mark.parametrize("name", ["poster.jpg", "inside.txt", "S06-Philip.mp4"])
    def test_returns_none_for_non_episode_names(self, name):
        assert EpisodeCode.from_filename(name) is None


class TestParseWikiDate:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("June 12, 1994", date(1994, 6, 12)),
            ("December 15, 2019", date(2019, 12, 15)),
            ("  March 9, 2003  ", date(2003, 3, 9)),
        ],
    )
    def test_parses_long_dates(self, text, expected):
        assert parse_wiki_date(text) == expected

    @pytest.mark.parametrize("text", ["1994-06-12", "June 1994", "", "Smarch 1, 1994"])
    def test_rejects_other_formats(self, text):
        with pytest.raises(DataError):
            parse_wiki_date(text)


class TestEpisode:
    def test_exposes_year(self, episode):
        assert episode.year == 2000

    def test_rejects_empty_guest(self):
        with pytest.raises(DataError):
            Episode.from_json({"season": 1, "episode": 1, "air_date": "June 12, 1994", "guest": " "})

    def test_rejects_missing_field(self):
        with pytest.raises(DataError):
            Episode.from_json({"season": 1, "episode": 1, "guest": "Paul Newman"})


class TestArchiveEntry:
    def test_detects_video_and_extension(self, entry_factory):
        entry = entry_factory("S08E01.BenStiller-2001.09.30.ITAS.SD.avi")
        assert entry.is_video
        assert entry.extension == "avi"

    def test_images_are_not_video(self, entry_factory):
        assert not entry_factory("poster.jpg").is_video

    def test_directories_have_no_code(self, entry_factory):
        assert entry_factory("Season 06", is_directory=True).code is None

    def test_size_in_gb_handles_missing_size(self, entry_factory):
        entry = ArchiveEntry(id="x", name="a.mp4", path="a.mp4", is_directory=False)
        assert entry.size_gb == 0.0


class TestGrouping:
    def test_groups_files_by_episode(self, entry_factory):
        entries = [
            entry_factory("S06E10.PhilipSeymourHoffman-2000.06.04.ITAS.SD.mp4"),
            entry_factory("S06E10.PhilipSeymourHoffman-2000.06.04.ITAS.HD.mp4"),
            entry_factory("S06E11.AlanAlda-2000.06.11.ITAS.SD.mp4"),
        ]
        grouped = group_by_code(entries)
        assert len(grouped[EpisodeCode(6, 10)]) == 2
        assert len(grouped[EpisodeCode(6, 11)]) == 1

    def test_ignores_directories_and_loose_files(self, entry_factory):
        entries = [
            entry_factory("Season 06", is_directory=True),
            entry_factory("poster.jpg"),
        ]
        assert group_by_code(entries) == {}

    def test_iter_files_skips_directories(self, entry_factory):
        entries = [
            entry_factory("Season 06", is_directory=True),
            entry_factory("S06E10.PhilipSeymourHoffman-2000.06.04.ITAS.SD.mp4"),
        ]
        assert [e.name for e in iter_files(entries)] == [
            "S06E10.PhilipSeymourHoffman-2000.06.04.ITAS.SD.mp4"
        ]
