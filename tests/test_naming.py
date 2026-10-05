"""Tests for the filename convention and guest matching."""

from __future__ import annotations

import pytest

from itas.model import EpisodeCode
from itas.naming import (
    LEGACY_EXCEPTIONS,
    check_entries,
    check_entry,
    guest_matches_filename,
    is_canonical,
    is_exempt,
    parse_filename,
    stale_exceptions,
)


@pytest.mark.parametrize(
    "name",
    [
        "S06E10.PhilipSeymourHoffman-2000.06.04.ITAS.SD.mp4",
        "S08E09.SarahJessicaParker-2002.03.03.ITAS.SD2.mp4",
        "S17E02.JimCarrey-2011.01.10.ITAS.HD1.mp4",
        "S01E01.PaulNewman-1994.06.12.ITAS.SD.mp4",
    ],
)
def test_canonical_names_are_accepted(name):
    assert is_canonical(name)
    assert parse_filename(name) is not None


@pytest.mark.parametrize(
    "name",
    [
        "S11E02.JamesGandolfini-2004.10.17.ITAS.SD.mp4.mp4",  # doubled extension
        "S08E01.BenStiller-2001.09.30.ITAS.SD.avi",  # legacy container
        "S12E03.QueenLatifah(RussianDub)-2006.01.08.ITAS.SD.mp4",  # parentheses
        "S11E22.EltonJohn.longcut-2005.10.16.ITAS.SD2.mp4",  # dot instead of hyphen
        "S03E04.AnjelicaHuston-1996.03.31.ITAS.S.mp4",  # truncated quality
        "S06E10.PhilipSeymourHoffman.mp4",  # no date
    ],
)
def test_non_canonical_names_are_rejected(name):
    assert not is_canonical(name)


def test_parse_filename_returns_components():
    parsed = parse_filename("S08E09.SarahJessicaParker-2002.03.03.ITAS.SD2.mp4")
    assert parsed == {
        "season": "08",
        "episode": "09",
        "guest": "SarahJessicaParker",
        "date": "2002.03.03",
        "quality": "SD",
        "cut": "2",
        "ext": "mp4",
    }


class TestLegacyExceptions:
    def test_every_exception_is_a_real_deviant_name(self):
        for name in LEGACY_EXCEPTIONS:
            assert not is_canonical(name), f"{name} matches the pattern, drop the exception"
            assert is_exempt(name)

    def test_exceptions_are_documented(self):
        for name, reason in LEGACY_EXCEPTIONS.items():
            assert reason.strip(), f"{name} has no documented reason"


class TestCheckEntry:
    def test_accepts_canonical_video(self, entry_factory):
        entry = entry_factory("S06E10.PhilipSeymourHoffman-2000.06.04.ITAS.SD.mp4")
        assert check_entry(entry) is None

    def test_accepts_exempt_legacy_file(self, entry_factory):
        entry = entry_factory("S08E01.BenStiller-2001.09.30.ITAS.SD.avi")
        assert check_entry(entry) is None

    def test_ignores_non_video_files(self, entry_factory):
        assert check_entry(entry_factory("poster.jpg")) is None

    def test_ignores_directories(self, entry_factory):
        assert check_entry(entry_factory("Season 06", is_directory=True)) is None

    def test_flags_unknown_video_name(self, entry_factory):
        problem = check_entry(entry_factory("S06E10.hoffman.mp4"))
        assert problem is not None
        assert "canonical filename pattern" in problem.reason

    def test_flags_unsupported_container(self, entry_factory):
        problem = check_entry(entry_factory("S06E10.PhilipSeymourHoffman-2000.06.04.ITAS.SD.wmv"))
        assert problem is not None
        assert "unsupported container" in problem.reason


def test_check_entries_sorts_by_path(entry_factory):
    entries = [
        entry_factory("S06E11.bad.mp4"),
        entry_factory("S06E10.worse.mp4"),
    ]
    problems = check_entries(entries)
    assert [p.name for p in problems] == ["S06E10.worse.mp4", "S06E11.bad.mp4"]


def test_stale_exceptions_reports_missing_files(entry_factory):
    entries = [entry_factory("S06E10.PhilipSeymourHoffman-2000.06.04.ITAS.SD.mp4")]
    stale = stale_exceptions(entries)
    assert "S08E01.BenStiller-2001.09.30.ITAS.SD.avi" in stale


class TestGuestMatching:
    @pytest.mark.parametrize(
        "filename,guest",
        [
            ("S09E12.ReneeZellweger-2003.03.09.ITAS.SD.mp4", "Renée Zellweger"),
            ("S08E15.SamuelLJackson-2002.06.02.ITAS.SD.avi", "Samuel L. Jackson"),
            ("S10E03.TheCastOfWillAndGrace-2003.11.16.ITAS.SD.mp4", "Cast of Will & Grace"),
            ("S21E05.TheWalkingDeadCast-2016.02.11.ITAS.SD.mp4", "Cast of The Walking Dead"),
            ("S21E06.ChristopherMeloni-2016.03.31.ITAS.SD.mp4", "Chris Meloni"),
            ("S10E16.10thYearCelebration-2004.06.20.ITAS.SD.mp4", "10th Anniversary Special"),
        ],
    )
    def test_accepts_equivalent_names(self, entry_factory, filename, guest):
        entry = entry_factory(filename)
        assert guest_matches_filename(entry.code, entry, guest)

    @pytest.mark.parametrize(
        "filename,guest",
        [
            ("S15E02.JamesLipton-2008.11.10.ITAS.SD.mp4", "Dave Chappelle"),
            ("S06E10.AlanAlda-2000.06.04.ITAS.SD.mp4", "Philip Seymour Hoffman"),
        ],
    )
    def test_rejects_different_guests(self, entry_factory, filename, guest):
        entry = entry_factory(filename)
        assert not guest_matches_filename(entry.code, entry, guest)

    def test_rejects_mismatched_episode_code(self, entry_factory):
        entry = entry_factory("S06E11.AlanAlda-2000.06.11.ITAS.SD.mp4")
        assert not guest_matches_filename(EpisodeCode(6, 10), entry, "Alan Alda")

    def test_legacy_names_are_not_judged(self, entry_factory):
        entry = entry_factory("S08E01.BenStiller-2001.09.30.ITAS.SD.avi")
        assert guest_matches_filename(entry.code, entry, "Anyone At All")
