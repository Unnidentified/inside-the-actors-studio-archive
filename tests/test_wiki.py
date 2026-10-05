"""Tests for the wikitext parser."""

from __future__ import annotations

from datetime import date

from itas.model import EpisodeCode
from itas.wiki import clean_wikitext, iter_season_tables, parse_episodes, parse_table_rows

SAMPLE = """
==Episodes==
===Season 1 (1994)===
{| class="wikitable"
|-
! No. !! Air Date !! Guest
|-
|1
|June 12, 1994
|[[Paul Newman]]
|-
|2
|June 18, 1994
|[[Alec Baldwin]]
|}
===Season 2 (1995)===
{| class="wikitable"
|-
|1
|March 1, 1995
|[[Some Guest]]<ref name=x>{{cite web|url=http://example.com}}</ref>
|}
==References==
{{reflist}}
"""


class TestCleanWikitext:
    def test_strips_links(self):
        assert clean_wikitext("[[Paul Newman]]") == "Paul Newman"

    def test_strips_piped_links(self):
        assert clean_wikitext("[[Bravo (TV)|Bravo]]") == "Bravo"

    def test_removes_references(self):
        assert clean_wikitext("Guest<ref name=x>stuff</ref>") == "Guest"

    def test_removes_bold(self):
        assert clean_wikitext("'''Guest'''") == "Guest"

    def test_removes_html(self):
        assert clean_wikitext("<small>Guest</small>") == "Guest"


class TestSeasonTables:
    def test_finds_both_seasons(self):
        seasons = list(iter_season_tables(SAMPLE))
        assert [number for number, _ in seasons] == [1, 2]

    def test_stops_before_references(self):
        _, body = list(iter_season_tables(SAMPLE))[1]
        assert "reflist" not in body


class TestTableRows:
    def test_splits_inline_cells(self):
        body = "|-\n|1\n|June 12, 1994\n|[[Paul Newman]]\n"
        assert list(parse_table_rows(body)) == [["1", "June 12, 1994", "[[Paul Newman]]"]]

    def test_skips_header_rows(self):
        body = "|-\n! No. !! Air Date\n|-\n|1\n|June 12, 1994\n|Guest\n"
        rows = list(parse_table_rows(body))
        assert rows == [["1", "June 12, 1994", "Guest"]]


class TestParseEpisodes:
    def test_parses_sample(self):
        episodes = parse_episodes(SAMPLE)
        assert [ep.code for ep in episodes] == [EpisodeCode(1, 1), EpisodeCode(1, 2), EpisodeCode(2, 1)]

    def test_parses_guest_and_date(self):
        first = parse_episodes(SAMPLE)[0]
        assert first.guest == "Paul Newman"
        assert first.air_date == date(1994, 6, 12)

    def test_cleans_references_from_guest(self):
        second_season = parse_episodes(SAMPLE)[2]
        assert second_season.guest == "Some Guest"

    def test_skips_rows_without_an_episode_number(self):
        body = """
===Season 1 (1994)===
{|
|-
|TBA
|June 12, 1994
|Guest
|}
"""
        assert parse_episodes(body) == []

    def test_returns_episodes_in_order(self):
        episodes = parse_episodes(SAMPLE)
        assert episodes == sorted(episodes, key=lambda ep: ep.code)


class TestAgainstRealWikitext:
    """Guard rails around the committed Wikipedia snapshot."""

    def test_parses_all_canonical_episodes(self, wikitext):
        episodes = parse_episodes(wikitext)
        assert len(episodes) == 277

    def test_covers_seasons_one_to_twenty_three(self, wikitext):
        seasons = {ep.code.season for ep in parse_episodes(wikitext)}
        assert seasons == set(range(1, 24))

    def test_first_and_last_episode(self, wikitext):
        episodes = parse_episodes(wikitext)
        assert episodes[0].code == EpisodeCode(1, 1)
        assert episodes[0].guest == "Paul Newman"
        assert episodes[-1].guest == "Lupita Nyong'o"
