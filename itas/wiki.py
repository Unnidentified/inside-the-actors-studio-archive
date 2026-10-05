"""Parse the Wikipedia episode list out of raw MediaWiki source.

The list lives at ``List of Inside the Actors Studio episodes``. Rather than
scrape the rendered page, we keep the raw wikitext in ``data/`` and parse the
season tables directly, which keeps the extraction reproducible offline.
"""

from __future__ import annotations

import re
from collections.abc import Iterator

from .model import Episode, EpisodeCode, parse_wiki_date

_SEASON_HEADING_RE = re.compile(r"^===\s*Season\s+(\d+)[^=]*===\s*$", re.MULTILINE)
_SECTION_END_RE = re.compile(r"^==+\s*[^=\n].*==+\s*$", re.MULTILINE)
_REF_RE = re.compile(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>", re.DOTALL)
_LINK_RE = re.compile(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]")
_TAG_RE = re.compile(r"<[^>]+>")
_BOLD_RE = re.compile(r"'{2,}")


def clean_wikitext(text: str) -> str:
    """Strip references, links and markup from a table cell."""
    text = _REF_RE.sub("", text)
    text = _LINK_RE.sub(r"\1", text)
    text = _BOLD_RE.sub("", text)
    text = _TAG_RE.sub("", text)
    return text.strip()


def iter_season_tables(wikitext: str) -> Iterator[tuple[int, str]]:
    """Yield ``(season_number, table_body)`` for every season section."""
    headings = list(_SEASON_HEADING_RE.finditer(wikitext))
    for index, heading in enumerate(headings):
        start = heading.end()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(wikitext)
        body = wikitext[start:end]
        # Stop at the next section heading (References, External links, ...).
        stop = _SECTION_END_RE.search(body)
        if stop:
            body = body[: stop.start()]
        yield int(heading.group(1)), body


def parse_table_rows(table_body: str) -> Iterator[list[str]]:
    """Yield the cells of each data row in a wikitable."""
    for row in table_body.split("|-")[1:]:
        cells: list[str] = []
        for line in row.splitlines():
            line = line.strip()
            if not line or line.startswith("!") or line.startswith("|}"):
                continue
            if not line.startswith("|"):
                continue
            content = line[1:].strip()
            cells.extend(part.strip() for part in content.split("||"))
        if cells:
            yield cells


def parse_episodes(wikitext: str) -> list[Episode]:
    """Parse every series episode out of the wikitext.

    Season 23 tables carry an extra "Host" column, so the guest sits one
    cell further to the right.
    """
    episodes: list[Episode] = []
    for season, body in iter_season_tables(wikitext):
        for cells in parse_table_rows(body):
            if len(cells) < 3:
                continue
            number = re.match(r"^(\d+)", cells[0])
            if not number:
                continue
            air_date = clean_wikitext(cells[1])
            guest_cell = cells[3] if season == 23 and len(cells) >= 4 else cells[2]
            guest = clean_wikitext(guest_cell)
            if not guest:
                continue
            try:
                parsed_date = parse_wiki_date(air_date)
            except ValueError:
                continue
            episodes.append(
                Episode(
                    code=EpisodeCode(season, int(number.group(1))),
                    guest=guest,
                    air_date=parsed_date,
                )
            )
    episodes.sort(key=lambda ep: ep.code)
    return episodes
