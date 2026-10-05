"""Tests for the audit checks."""

from __future__ import annotations

from datetime import date

import pytest

from itas.audit import (
    Severity,
    check_air_dates,
    check_duplicate_episodes,
    check_guest_names,
    check_naming,
    check_tracking_document,
    check_unknown_episodes,
    compute_coverage,
    parse_tracking_document,
    run_audit,
)
from itas.model import Episode, EpisodeCode


@pytest.fixture
def episodes():
    return [
        Episode(EpisodeCode(1, 1), "Paul Newman", date(1994, 6, 12)),
        Episode(EpisodeCode(1, 2), "Alec Baldwin", date(1994, 6, 18)),
        Episode(EpisodeCode(1, 3), "Stephen Sondheim", date(1994, 6, 22)),
    ]


@pytest.fixture
def archive(entry_factory):
    return [
        entry_factory("S01E01.PaulNewman-1994.06.12.ITAS.SD.mp4"),
        entry_factory("S01E02.AlecBaldwin-1994.06.18.ITAS.SD.mp4"),
    ]


class TestCoverage:
    def test_counts_present_and_missing(self, episodes, archive):
        coverage = compute_coverage(episodes, archive)
        assert coverage.total == 3
        assert coverage.present == 2
        assert coverage.missing == [EpisodeCode(1, 3)]
        assert coverage.percent == pytest.approx(66.67, abs=0.01)

    def test_counts_specials_separately(self, episodes, archive, entry_factory):
        archive = archive + [entry_factory("S00E02.100thEpisode-2001.08.19.ITAS.SD.mp4")]
        coverage = compute_coverage(episodes, archive)
        assert coverage.specials == 1
        assert coverage.present == 2, "specials must not inflate series coverage"

    def test_handles_empty_episode_list(self, archive):
        coverage = compute_coverage([], archive)
        assert coverage.total == 0
        assert coverage.percent == 0.0

    def test_summary_is_human_readable(self, episodes, archive):
        assert "2/3 series episodes preserved" in compute_coverage(episodes, archive).summary()


class TestGuestNames:
    def test_passes_when_names_agree(self, episodes, archive):
        assert check_guest_names(episodes, archive) == []

    def test_flags_wrong_guest(self, episodes, entry_factory):
        entries = [entry_factory("S01E01.AlecBaldwin-1994.06.12.ITAS.SD.mp4")]
        findings = check_guest_names(episodes, entries)
        assert len(findings) == 1
        assert findings[0].code == "guest-mismatch"
        assert findings[0].episode == EpisodeCode(1, 1)

    def test_ignores_episodes_not_in_wikipedia(self, episodes, entry_factory):
        entries = [entry_factory("S09E09.SomeoneElse-2003.01.01.ITAS.SD.mp4")]
        assert check_guest_names(episodes, entries) == []


class TestAirDates:
    def test_passes_when_years_agree(self, episodes, archive):
        assert check_air_dates(episodes, archive) == []

    def test_flags_wrong_year(self, episodes, entry_factory):
        entries = [entry_factory("S01E01.PaulNewman-1995.06.12.ITAS.SD.mp4")]
        findings = check_air_dates(episodes, entries)
        assert len(findings) == 1
        assert findings[0].code == "air-date-mismatch"

    def test_skips_names_without_a_date(self, episodes, entry_factory):
        entries = [entry_factory("S01E01.PaulNewman.ITAS.SD.mp4")]
        assert check_air_dates(episodes, entries) == []


class TestUnknownEpisodes:
    def test_flags_episodes_missing_from_wikipedia(self, episodes, entry_factory):
        entries = [entry_factory("S09E09.Mystery-2003.01.01.ITAS.SD.mp4")]
        findings = check_unknown_episodes(episodes, entries)
        assert len(findings) == 1
        assert findings[0].severity is Severity.WARNING

    def test_specials_are_not_unknown(self, episodes, entry_factory):
        entries = [entry_factory("S00E02.100thEpisode-2001.08.19.ITAS.SD.mp4")]
        assert check_unknown_episodes(episodes, entries) == []


class TestNamingCheck:
    def test_canonical_archive_is_clean(self, archive):
        assert check_naming(archive) == []

    def test_flags_bad_names(self, entry_factory):
        findings = check_naming([entry_factory("S01E01.paulnewman.mp4")])
        assert [f.code for f in findings] == ["naming"]


class TestDuplicateEpisodes:
    def test_reports_alternate_cuts(self, entry_factory):
        entries = [
            entry_factory("S01E01.PaulNewman-1994.06.12.ITAS.SD.mp4"),
            entry_factory("S01E01.PaulNewman-1994.06.12.ITAS.HD.mp4"),
        ]
        findings = check_duplicate_episodes(entries)
        assert len(findings) == 1
        assert findings[0].severity is Severity.INFO

    def test_single_file_episodes_are_quiet(self, archive):
        assert check_duplicate_episodes(archive) == []


TRACKING = """
**Season 1**

* S01E01 - Paul Newman
* ~~S01E02 - Alec Baldwin~~
* S01E03 - Stephen Sondheim
"""


class TestTrackingDocument:
    def test_parses_plain_and_crossed_lines(self):
        entries = parse_tracking_document(TRACKING)
        assert [e.code for e in entries] == [
            EpisodeCode(1, 1),
            EpisodeCode(1, 2),
            EpisodeCode(1, 3),
        ]
        assert [e.marked_missing for e in entries] == [False, True, False]

    def test_ignores_prose_and_other_bullets(self):
        text = "Some prose\n* not an episode\n* S01E01 - Paul Newman\n"
        assert len(parse_tracking_document(text)) == 1

    def test_flags_episode_marked_missing_but_present(self, episodes, archive):
        findings = check_tracking_document(TRACKING, episodes, archive)
        codes = {f.code for f in findings}
        assert "tracking-stale" in codes

    def test_flags_episode_listed_but_absent(self, episodes, archive):
        text = "* S01E01 - Paul Newman\n* S01E02 - Alec Baldwin\n* S01E03 - Stephen Sondheim\n"
        findings = check_tracking_document(text, episodes, archive)
        assert any(f.code == "tracking-optimistic" for f in findings)

    def test_flags_missing_line(self, episodes, archive):
        text = "* S01E01 - Paul Newman\n* S01E02 - Alec Baldwin\n"
        findings = check_tracking_document(text, episodes, archive)
        assert any(f.code == "tracking-missing-line" for f in findings)

    def test_flags_duplicate_lines(self, episodes, archive):
        text = "* S01E01 - Paul Newman\n* S01E01 - Paul Newman\n* S01E02 - Alec Baldwin\n"
        findings = check_tracking_document(text, episodes, archive)
        assert any(f.code == "tracking-duplicate" for f in findings)

    def test_warns_on_guest_name_drift(self, episodes, archive):
        text = "* S01E01 - Paul Neumann\n* S01E02 - Alec Baldwin\n* S01E03 - Stephen Sondheim\n"
        findings = check_tracking_document(text, episodes, archive)
        assert any(f.code == "tracking-guest" for f in findings)

    def test_clean_document_has_no_findings(self, episodes, archive):
        text = "* S01E01 - Paul Newman\n* S01E02 - Alec Baldwin\n* ~~S01E03 - Stephen Sondheim~~\n"
        assert check_tracking_document(text, episodes, archive) == []


class TestRunAudit:
    def test_combines_checks_and_sorts_by_severity(self, episodes, entry_factory):
        entries = [
            entry_factory("S01E01.AlecBaldwin-1994.06.12.ITAS.SD.mp4"),
            entry_factory("S01E02.bad.mp4"),
        ]
        report = run_audit(episodes, entries)
        assert report.ok is False
        assert report.findings[0].severity is Severity.ERROR

    def test_ok_when_no_errors(self, episodes, archive):
        report = run_audit(episodes, archive)
        assert report.ok is True
        assert report.coverage.present == 2
