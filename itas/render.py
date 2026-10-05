"""Render the availability checklist from an audit result.

The checklist in ``available-global.txt`` and ``README.md`` is generated, not
hand-maintained. Keeping it derived from the archive snapshot means the two
can never drift apart again.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from .model import ArchiveEntry, Episode, group_by_code


def render_checklist(
    episodes: Sequence[Episode],
    entries: Sequence[ArchiveEntry],
    *,
    include_specials: bool = True,
) -> str:
    """Render the Markdown availability checklist.

    Available episodes are plain list items; missing ones are struck
    through. Specials (season 0) are grouped separately at the top.
    """
    present = set(group_by_code(entries))
    lines: list[str] = []

    if include_specials:
        specials = _render_specials(entries)
        if specials:
            lines.append("**Specials / Season 0**")
            lines.append("")
            lines.extend(specials)
            lines.append("")

    by_season: dict[int, list[Episode]] = {}
    for episode in episodes:
        by_season.setdefault(episode.code.season, []).append(episode)

    for season in sorted(by_season):
        lines.append(f"**Season {season}**")
        lines.append("")
        for episode in sorted(by_season[season], key=lambda ep: ep.code.episode):
            label = f"S{season:02d}E{episode.code.episode:02d} - {episode.guest}"
            if episode.code in present:
                lines.append(f"* {label}")
            else:
                lines.append(f"* ~~{label}~~")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


#: Human-readable labels for the Season 0 extras. The Drive filenames are
#: machine-oriented, so the checklist spells them out.
SPECIAL_LABELS: dict[str, str] = {
    "S00E02": "100th Episode Special",
    "S00E03": "50 Year Celebration",
    "S00E04": "Robert De Niro (Deleted Scenes) #1",
    "S00E05": "Robert De Niro (Deleted Scenes) #2",
    "S00E06": "Robert De Niro (Deleted Scenes) #3",
    "S00E07": "Robert De Niro (Deleted Scenes) #4",
    "S00E08": "200th Episode (Hosted by Dave Chappelle)",
    "S00E09": "Robin Williams (Extras Combined)",
    "S00E33": "Paul Newman (Deleted Scenes) #1",
    "S00E34": "Paul Newman (Deleted Scenes) #2",
    "S00E35": "Paul Newman (Deleted Scenes) #3",
    "S00E36": "Paul Newman (Deleted Scenes) #4",
    "S00E53": "DVD Introduction",
}


def _render_specials(entries: Iterable[ArchiveEntry]) -> list[str]:
    """List the Season 0 contents using their human-readable labels."""
    codes = sorted(
        {entry.code for entry in entries if entry.code and entry.code.season == 0}
    )
    lines: list[str] = []
    for code in codes:
        assert code is not None
        label = SPECIAL_LABELS.get(str(code))
        if label is None:
            # Fall back to the filename so a new extra is never silently dropped.
            match = next(
                entry for entry in entries if entry.code == code
            )
            label = match.name.rsplit(".", 1)[0]
        lines.append(f"* {code} - {label}")
    return lines
