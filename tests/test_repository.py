"""End-to-end checks against the committed data.

These tests are the ones that would have caught the drift that prompted the
repository restructure: they assert the shipped snapshot, the Wikipedia
listing and the tracking document all agree.
"""

from __future__ import annotations

import pytest

from itas.audit import Severity, run_audit
from itas.model import load_archive, load_episodes
from itas.naming import check_entries, stale_exceptions


@pytest.fixture(scope="module")
def episodes(repo_root):
    return load_episodes(repo_root / "data" / "episodes.json")


@pytest.fixture(scope="module")
def archive(repo_root):
    return load_archive(repo_root / "data" / "drive_snapshot.json")


@pytest.fixture(scope="module")
def tracking_text(repo_root):
    return (repo_root / "available-global.txt").read_text(encoding="utf-8")


class TestCommittedData:
    def test_episode_list_matches_wikipedia_snapshot(self, episodes, wikitext):
        from itas.wiki import parse_episodes

        reparsed = parse_episodes(wikitext)
        assert [ep.code for ep in reparsed] == [ep.code for ep in episodes]
        assert [ep.guest for ep in reparsed] == [ep.guest for ep in episodes]

    def test_snapshot_has_no_duplicate_ids(self, archive):
        ids = [entry.id for entry in archive]
        assert len(ids) == len(set(ids))

    def test_all_video_files_follow_the_convention(self, archive):
        problems = check_entries(archive)
        assert problems == [], "\n".join(str(p) for p in problems)

    def test_no_stale_legacy_exceptions(self, archive):
        assert stale_exceptions(archive) == []


class TestAuditOnRealData:
    def test_coverage_matches_the_readme(self, episodes, archive):
        report = run_audit(episodes, archive)
        assert report.coverage.total == 277
        assert report.coverage.present == 225
        assert report.coverage.specials == 13
        assert report.coverage.distinct_episodes == 238

    def test_tracking_document_is_consistent(self, episodes, archive, tracking_text):
        report = run_audit(episodes, archive, tracking_text)
        tracking_errors = [
            f for f in report.errors if f.code.startswith("tracking-")
        ]
        assert tracking_errors == []

    def test_only_the_known_s15e02_mismatch_remains(self, episodes, archive):
        """S15E02 is filed as a James Lipton special; see docs/known-issues.md."""
        report = run_audit(episodes, archive)
        guest_findings = [f for f in report.findings if f.code == "guest-mismatch"]
        assert [str(f.episode) for f in guest_findings] == ["S15E02"]
        assert guest_findings[0].severity is Severity.INFO, (
            "the S15E02 mismatch should stay downgraded until it is resolved"
        )
