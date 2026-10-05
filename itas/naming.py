"""Canonical filename rules for archive video files.

The archive follows a single naming convention so that the Drive folder can
be parsed by machines and read by humans:

    S{SS}E{EE}.{GuestNamePascalCase}-{YYYY.MM.DD}.ITAS.{SD|HD}[cut].{ext}

A handful of legacy files predate the convention. Rather than rename them
(which would break every existing share link), they are listed explicitly in
``LEGACY_EXCEPTIONS`` and only reported when they disappear or change.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

from .model import VIDEO_EXTENSIONS, ArchiveEntry, EpisodeCode

CANONICAL_RE = re.compile(
    r"^S(?P<season>\d{2})E(?P<episode>\d{2})"
    r"\.(?P<guest>[A-Za-z0-9']+)"
    r"-(?P<date>\d{4}\.\d{2}\.\d{2})"
    r"\.ITAS\."
    r"(?P<quality>SD|HD)(?P<cut>\d*)"
    r"\.(?P<ext>mp4)$"
)

#: Extensions the archive accepts for video, in order of preference.
ACCEPTED_VIDEO_EXTENSIONS = ("mp4", "mkv", "avi")

#: Files that intentionally deviate from ``CANONICAL_RE``.
#:
#: Each entry is ``(filename, reason)``. Keep this list sorted by filename so
#: diffs stay readable, and delete entries once a file is renamed upstream.
LEGACY_EXCEPTIONS: dict[str, str] = {
    "S00E03.50YearCelebration.ITAS.SD.mp4": "special: no guest segment in the name",
    "S00E04.RobertDeNiro.DeletedScenes#1.ITAS.SD.mp4": "special: deleted-scene clip, no air date",
    "S00E05.RobertDeNiro.DeletedScenes#2.ITAS.SD.mp4": "special: deleted-scene clip, no air date",
    "S00E06.RobertDeNiro.DeletedScenes#3.ITAS.SD.mp4": "special: deleted-scene clip, no air date",
    "S00E07.RobertDeNiro.DeletedScenes#4.ITAS.SD.mp4": "special: deleted-scene clip, no air date",
    "S00E09-E15.RobinWilliamsExtrasCombined.ITAS.SD.mp4": "special: combined extras, spans an episode range",
    "S00E33.PaulNewman-1994.08.14.DeletedScenes#1.ITAS.SD.mp4": "special: deleted-scene clip",
    "S00E34.PaulNewman-1994.08.14.DeletedScenes#2.ITAS.SD.mp4": "special: deleted-scene clip",
    "S00E35.PaulNewman-1994.08.14.DeletedScenes#3.ITAS.SD.mp4": "special: deleted-scene clip",
    "S00E36.PaulNewman-1994.08.14.DeletedScenes#4.ITAS.SD.mp4": "special: deleted-scene clip",
    "S00E53.DVDIntroduction.ITAS.SD.mp4": "special: DVD extra, no guest or air date",
    "S01E02.AlecBaldwin-1994.06.18.ITAS.SD-incomplete.mp4": "legacy: partial capture, kept for completeness",
    "S03E04.AnjelicaHuston-1996.03.31.ITAS.S.mp4": "legacy: truncated quality tag",
    "S08E01.BenStiller-2001.09.30.ITAS.SD.avi": "legacy: original AVI rip",
    "S08E04.BruceWillis-2001.10.28.ITAS.SD.mkv": "legacy: original MKV rip",
    "S08E05.KevinCostner-2001.11.25.ITAS.SD.avi": "legacy: original AVI rip",
    "S08E06.WillSmith-2002.01.13.ITAS.HD.mkv": "legacy: original MKV rip",
    "S08E06.WillSmith-2002.01.13.ITAS.SD.avi": "legacy: original AVI rip",
    "S08E09.SarahJessicaParker-2002.03.03.ITAS.SD1.avi": "legacy: original AVI rip, alternate cut",
    "S08E09.SarahJessicaParker-2002.03.03.ITAS.SD2.avi": "legacy: original AVI rip, alternate cut",
    "S08E10.BenKingsley-2002.03.17.ITAS.SD.avi": "legacy: original AVI rip",
    "S08E11.DennisQuaid-2002.04.07.ITAS.SD.avi": "legacy: original AVI rip",
    "S08E13.RichardGere-2002.05.05.ITAS.SD.avi": "legacy: original AVI rip",
    "S08E14.HughGrant-2002.05.12.ITAS.SD.avi": "legacy: original AVI rip",
    "S08E15.SamuelLJackson-2002.06.02.ITAS.SD.avi": "legacy: original AVI rip",
    "S08E16.BenicioDelToro-2002.06.30.ITAS.SD.avi": "legacy: original AVI rip",
    "S08E18.BillyBobThornton-2002.08.18.ITAS.SD.avi": "legacy: original AVI rip",
    "S08E19.JohnnyDepp-2002.09.08.ITAS.SD.avi": "legacy: original AVI rip",
    "S11E02.JamesGandolfini-2004.10.17.ITAS.SD.mp4.mp4": "legacy: doubled extension",
    "S11E03.WilliamHMacy-2004.10.24.ITAS.SD.mp4.mp4": "legacy: doubled extension",
    "S11E22.EltonJohn.longcut-2005.10.16.ITAS.SD2.mp4": "legacy: cut marker uses a dot instead of a suffix",
    "S12E03.QueenLatifah(RussianDub)-2006.01.08.ITAS.SD.mp4": "legacy: dub marker in parentheses",
    "S13E07.JuliaLouis-Dreyfus-2007.06.04.ITAS.SD.mp4": "legacy: hyphen inside the guest name",
}


@dataclass(frozen=True)
class NamingProblem:
    """A filename that does not match the convention and is not exempt."""

    name: str
    path: str
    reason: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.path}: {self.reason}"


def parse_filename(name: str) -> dict[str, str] | None:
    """Return the named groups of a canonical filename, or ``None``."""
    match = CANONICAL_RE.match(name)
    return match.groupdict() if match else None


def is_canonical(name: str) -> bool:
    return CANONICAL_RE.match(name) is not None


def is_exempt(name: str) -> bool:
    return name in LEGACY_EXCEPTIONS


def check_entry(entry: ArchiveEntry) -> NamingProblem | None:
    """Return a problem for a single video file, or ``None`` if it is fine."""
    if entry.is_directory:
        return None
    if entry.extension not in ACCEPTED_VIDEO_EXTENSIONS:
        # Any media container we do not accept is a problem regardless of
        # whether the rest of the name follows the convention.
        if entry.extension in VIDEO_EXTENSIONS:
            return NamingProblem(entry.name, entry.path, f"unsupported container .{entry.extension}")
        return None
    if is_canonical(entry.name) or is_exempt(entry.name):
        return None
    return NamingProblem(entry.name, entry.path, "does not match the canonical filename pattern")


def check_entries(entries: Iterable[ArchiveEntry]) -> list[NamingProblem]:
    """Return every naming problem in a set of archive entries."""
    problems = [problem for entry in entries if (problem := check_entry(entry))]
    return sorted(problems, key=lambda p: p.path)


def stale_exceptions(entries: Iterable[ArchiveEntry]) -> list[str]:
    """Return exempt filenames that no longer exist in the archive."""
    present = {entry.name for entry in entries if not entry.is_directory}
    return sorted(set(LEGACY_EXCEPTIONS) - present)


def guest_matches_filename(code: EpisodeCode, entry: ArchiveEntry, guest: str) -> bool:
    """Check whether the guest in a filename plausibly matches Wikipedia.

    Comparison is deliberately loose: punctuation, spacing and accents are
    stripped, and either name may be a substring of the other, so
    ``ReneeZellweger`` matches ``Renée Zellweger`` and
    ``TheWalkingDeadCast`` matches ``Cast of The Walking Dead``.
    """
    parsed = parse_filename(entry.name)
    if parsed is None:
        return True  # legacy files are validated by hand, not here
    if parsed["season"] != f"{code.season:02d}" or parsed["episode"] != f"{code.episode:02d}":
        return False
    file_guest = _normalise(parsed["guest"])
    wiki_guest = _normalise(guest)
    if not file_guest or not wiki_guest:
        return True
    if file_guest in wiki_guest or wiki_guest in file_guest:
        return True
    # Nicknames and mid-name initials: "ChrisMeloni" vs "Christopher Meloni".
    if _alias_match(parsed["guest"], guest):
        return True

    # Ensemble and anniversary episodes are named loosely ("TheCastOfX",
    # "XCast", "10thYearCelebration"); compare the distinctive words instead.
    file_key = _cast_key(file_guest)
    wiki_key = _cast_key(wiki_guest)
    if not file_key or not wiki_key:
        return _anniversary_match(file_guest, wiki_guest)
    return file_key == wiki_key or file_key in wiki_key or wiki_key in file_key


def _anniversary_match(file_guest: str, wiki_guest: str) -> bool:
    """Match milestone specials named by ordinal and year.

    ``10thYearCelebration`` and ``10th Anniversary Special`` both reduce to
    ``10``; the comparison is intentionally narrow so ordinary names never
    reach it.
    """
    ordinal = re.compile(r"^(\d{1,3})(?:st|nd|rd|th)")
    file_match = ordinal.match(file_guest)
    wiki_match = ordinal.match(wiki_guest)
    if not file_match or not wiki_match:
        return False
    if file_match.group(1) != wiki_match.group(1):
        return False
    return ("celebration" in file_guest or "anniversary" in wiki_guest)


def _alias_match(file_name: str, wiki_name: str) -> bool:
    """Match names that share a surname and a compatible first name.

    Handles two cases the plain substring test misses:

    * a shortened first name (``Chris`` vs ``Christopher``)
    * a middle initial present in one form only (``WilliamHMacy`` vs ``William Macy``)

    The surname must match exactly, which keeps this from becoming a
    free-for-all fuzzy match.
    """
    file_parts = _name_parts(file_name)
    wiki_parts = _name_parts(wiki_name)
    if len(file_parts) < 2 or len(wiki_parts) < 2:
        return False
    if file_parts[-1].lower() != wiki_parts[-1].lower():
        return False
    file_first, wiki_first = file_parts[0].lower(), wiki_parts[0].lower()
    if not (file_first.startswith(wiki_first) or wiki_first.startswith(file_first)):
        return False
    file_middle = [p.lower() for p in file_parts[1:-1] if len(p) > 1]
    wiki_middle = [p.lower() for p in wiki_parts[1:-1] if len(p) > 1]
    return file_middle == wiki_middle


def _name_parts(name: str) -> list[str]:
    """Split a guest name into words, dropping single-letter initials.

    Filenames use PascalCase (``WilliamHMacy``) while Wikipedia uses spaces
    (``William H. Macy``); both forms are split into the same word list.
    """
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", name)
    words = re.split(r"[\s.]+", spaced)
    words = [w for w in words if w]
    # "William H Macy" -> a trailing single letter is an initial, not a word.
    if len(words) == 2 and len(words[1]) == 1:
        return [words[0]]
    return words


def _cast_key(normalised: str) -> str:
    """Strip ensemble scaffolding from a guest name.

    ``thecastoflawandorder``, ``castoflawandorder`` and ``lawandordercast``
    all reduce to ``laworder``; non-ensemble names reduce to ``""``.
    """
    for prefix in ("thecastof", "castof"):
        if normalised.startswith(prefix):
            # "willandgrace" and "willgrace" are the same ensemble; drop the
            # conjunction so both forms compare equal.
            return normalised[len(prefix) :].replace("and", "")
    for suffix in ("thecast", "cast"):
        if normalised.endswith(suffix) and len(normalised) > len(suffix):
            return normalised[: -len(suffix)]
    return ""


def _normalise(text: str) -> str:
    import unicodedata

    decomposed = unicodedata.normalize("NFKD", text)
    ascii_only = decomposed.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]", "", ascii_only.lower())
