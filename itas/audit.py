"""Audit the archive against the canonical Wikipedia episode list.

The audit answers three questions:

1. Which canonical episodes are present in the archive?
2. Do the filenames agree with Wikipedia on guest and air date?
3. Do the tracking documents (``available-global.txt``) agree with reality?

Every check returns structured :class:`Finding` objects so both the CLI and
the tests can inspect them without parsing printed output.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum

from .model import ArchiveEntry, Episode, EpisodeCode, group_by_code, iter_files
from .naming import check_entries, guest_matches_filename, stale_exceptions


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class Finding:
    """A single audit result."""

    severity: Severity
    code: str
    message: str
    episode: EpisodeCode | None = None

    def __str__(self) -> str:  # pragma: no cover - trivial
        prefix = f"{self.episode}: " if self.episode else ""
        return f"[{self.severity.value}] {prefix}{self.message}"


@dataclass
class Coverage:
    """How much of the canonical series is preserved."""

    total: int
    present: int
    missing: list[EpisodeCode] = field(default_factory=list)
    specials: int = 0
    files: int = 0
    distinct_episodes: int = 0
    size_gb: float = 0.0

    @property
    def percent(self) -> float:
        return (self.present / self.total * 100) if self.total else 0.0

    def summary(self) -> str:
        return (
            f"{self.present}/{self.total} series episodes preserved "
            f"({self.percent:.1f}%), {self.specials} specials, "
            f"{self.files} files / {self.distinct_episodes} distinct episodes, "
            f"{self.size_gb:.1f} GB"
        )


@dataclass
class AuditReport:
    """The full result of an audit run."""

    coverage: Coverage
    findings: list[Finding]

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity is Severity.ERROR]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity is Severity.WARNING]

    @property
    def ok(self) -> bool:
        return not self.errors


#: Findings that are understood and accepted, keyed by ``(code, episode)``.
#:
#: Anything listed here is downgraded to ``INFO`` so CI can stay green while
#: the underlying question is still open. Remove an entry once it is fixed.
KNOWN_ISSUES: dict[tuple[str, str], str] = {
    ("guest-mismatch", "S15E02"): (
        "the file is a James Lipton tribute special filed under the "
        "Dave Chappelle slot; see docs/known-issues.md"
    ),
}


# --------------------------------------------------------------------------
# Coverage
# --------------------------------------------------------------------------


def compute_coverage(
    episodes: Sequence[Episode], entries: Sequence[ArchiveEntry]
) -> Coverage:
    """Compare the canonical episode list with the archive contents."""
    grouped = group_by_code(entries)
    series_codes = {ep.code for ep in episodes}
    present = sorted(series_codes & grouped.keys())
    missing = sorted(series_codes - grouped.keys())
    specials = sorted(code for code in grouped if code.season == 0)

    files = list(iter_files(entries))
    return Coverage(
        total=len(series_codes),
        present=len(present),
        missing=missing,
        specials=len(specials),
        files=len([f for f in files if f.code is not None]),
        distinct_episodes=len(grouped),
        size_gb=sum(f.size_gb for f in files),
    )


# --------------------------------------------------------------------------
# Individual checks
# --------------------------------------------------------------------------


def check_guest_names(
    episodes: Sequence[Episode], entries: Sequence[ArchiveEntry]
) -> list[Finding]:
    """Flag filenames whose guest does not match the Wikipedia listing."""
    by_code = {ep.code: ep for ep in episodes}
    findings: list[Finding] = []
    for code, files in sorted(group_by_code(entries).items()):
        episode = by_code.get(code)
        if episode is None:
            continue
        for entry in files:
            if not guest_matches_filename(code, entry, episode.guest):
                findings.append(
                    Finding(
                        Severity.ERROR,
                        "guest-mismatch",
                        f"{entry.name} does not match Wikipedia guest "
                        f"'{episode.guest}' ({episode.air_date.isoformat()})",
                        code,
                    )
                )
    return findings


def check_air_dates(
    episodes: Sequence[Episode], entries: Sequence[ArchiveEntry]
) -> list[Finding]:
    """Flag filenames whose embedded year disagrees with Wikipedia."""
    by_code = {ep.code: ep for ep in episodes}
    findings: list[Finding] = []
    date_re = re.compile(r"(\d{4})\.(\d{2})\.(\d{2})")
    for code, files in sorted(group_by_code(entries).items()):
        episode = by_code.get(code)
        if episode is None:
            continue
        for entry in files:
            match = date_re.search(entry.name)
            if not match:
                continue
            year = int(match.group(1))
            if year != episode.year:
                findings.append(
                    Finding(
                        Severity.ERROR,
                        "air-date-mismatch",
                        f"{entry.name} has year {year}, Wikipedia says "
                        f"{episode.air_date.isoformat()}",
                        code,
                    )
                )
    return findings


def check_unknown_episodes(
    episodes: Sequence[Episode], entries: Sequence[ArchiveEntry]
) -> list[Finding]:
    """Flag archive files for episodes Wikipedia does not list."""
    known = {ep.code for ep in episodes}
    findings: list[Finding] = []
    for code, files in sorted(group_by_code(entries).items()):
        if code.season == 0 or code in known:
            continue
        findings.append(
            Finding(
                Severity.WARNING,
                "unknown-episode",
                f"{len(files)} file(s) for an episode missing from the Wikipedia list",
                code,
            )
        )
    return findings


def check_naming(entries: Sequence[ArchiveEntry]) -> list[Finding]:
    """Flag video files that break the naming convention."""
    return [
        Finding(Severity.WARNING, "naming", problem.reason + f" ({problem.name})")
        for problem in check_entries(entries)
    ]


def check_legacy_exceptions(entries: Sequence[ArchiveEntry]) -> list[Finding]:
    """Flag entries in ``LEGACY_EXCEPTIONS`` that no longer exist."""
    findings: list[Finding] = []
    for name in stale_exceptions(entries):
        findings.append(
            Finding(
                Severity.INFO,
                "stale-exception",
                f"legacy exception '{name}' is no longer present; remove it from naming.LEGACY_EXCEPTIONS",
            )
        )
    return findings


def check_duplicate_episodes(entries: Sequence[ArchiveEntry]) -> list[Finding]:
    """Report episodes that ship more than one file (alternate cuts, qualities)."""
    findings: list[Finding] = []
    for code, files in sorted(group_by_code(entries).items()):
        if len(files) < 2:
            continue
        findings.append(
            Finding(
                Severity.INFO,
                "alternate-cuts",
                f"{len(files)} files: " + ", ".join(sorted(f.name for f in files)),
                code,
            )
        )
    return findings


# --------------------------------------------------------------------------
# Tracking document parsing
# --------------------------------------------------------------------------

_TRACKING_LINE_RE = re.compile(
    r"^\*\s+(?P<crossed>~~)?S(?P<season>\d+)E(?P<episode>\d+)\s+-\s+(?P<guest>.+?)(?:~~)?\s*$"
)


@dataclass(frozen=True)
class TrackingEntry:
    """One line of the ``available-global.txt`` checklist."""

    code: EpisodeCode
    guest: str
    marked_missing: bool


def parse_tracking_document(text: str) -> list[TrackingEntry]:
    """Parse the availability checklist out of the tracking document.

    Lines look like::

        * S01E01 - Paul Newman
        * ~~S01E04 - Sidney Lumet~~

    Anything else is ignored, so the surrounding prose can change freely.
    """
    entries: list[TrackingEntry] = []
    for line in text.splitlines():
        match = _TRACKING_LINE_RE.match(line.strip())
        if not match:
            continue
        entries.append(
            TrackingEntry(
                code=EpisodeCode(int(match.group("season")), int(match.group("episode"))),
                guest=match.group("guest").strip(),
                marked_missing=bool(match.group("crossed")),
            )
        )
    return entries


def check_tracking_document(
    text: str, episodes: Sequence[Episode], entries: Sequence[ArchiveEntry]
) -> list[Finding]:
    """Verify the tracking checklist against Wikipedia and the archive."""
    tracked = parse_tracking_document(text)
    by_code = {ep.code: ep for ep in episodes}
    present = set(group_by_code(entries))
    findings: list[Finding] = []

    seen: set[EpisodeCode] = set()
    for entry in tracked:
        if entry.code in seen:
            findings.append(
                Finding(Severity.ERROR, "tracking-duplicate", "listed more than once", entry.code)
            )
        seen.add(entry.code)

        episode = by_code.get(entry.code)
        if episode is None:
            if entry.code.season > 0:
                findings.append(
                    Finding(
                        Severity.ERROR,
                        "tracking-unknown",
                        f"tracking document lists an episode Wikipedia does not ({entry.guest})",
                        entry.code,
                    )
                )
            continue

        if entry.guest != episode.guest:
            findings.append(
                Finding(
                    Severity.WARNING,
                    "tracking-guest",
                    f"tracking document says '{entry.guest}', Wikipedia says '{episode.guest}'",
                    entry.code,
                )
            )

        archived = entry.code in present
        if archived and entry.marked_missing:
            findings.append(
                Finding(
                    Severity.ERROR,
                    "tracking-stale",
                    "marked as missing but present in the archive",
                    entry.code,
                )
            )
        elif not archived and not entry.marked_missing:
            findings.append(
                Finding(
                    Severity.ERROR,
                    "tracking-optimistic",
                    "listed as available but not present in the archive",
                    entry.code,
                )
            )

    for code in sorted(set(by_code) - seen):
        findings.append(
            Finding(
                Severity.ERROR,
                "tracking-missing-line",
                f"not listed in the tracking document ({by_code[code].guest})",
                code,
            )
        )

    return findings


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def run_audit(
    episodes: Sequence[Episode],
    entries: Sequence[ArchiveEntry],
    tracking_text: str | None = None,
) -> AuditReport:
    """Run every check and return a combined report."""
    findings: list[Finding] = []
    findings.extend(check_guest_names(episodes, entries))
    findings.extend(check_air_dates(episodes, entries))
    findings.extend(check_unknown_episodes(episodes, entries))
    findings.extend(check_naming(entries))
    findings.extend(check_legacy_exceptions(entries))
    findings.extend(check_duplicate_episodes(entries))
    if tracking_text is not None:
        findings.extend(check_tracking_document(tracking_text, episodes, entries))

    findings = [apply_known_issues(f) for f in findings]
    order = {Severity.ERROR: 0, Severity.WARNING: 1, Severity.INFO: 2}
    findings.sort(key=lambda f: (order[f.severity], f.episode or EpisodeCode(99, 99), f.code))
    return AuditReport(coverage=compute_coverage(episodes, entries), findings=findings)


def apply_known_issues(finding: Finding) -> Finding:
    """Downgrade a finding that matches an entry in :data:`KNOWN_ISSUES`."""
    key = (finding.code, str(finding.episode) if finding.episode else "")
    reason = KNOWN_ISSUES.get(key)
    if reason is None:
        return finding
    return Finding(
        Severity.INFO,
        finding.code,
        f"{finding.message} (known: {reason})",
        finding.episode,
    )
