# Contributing

Two ways to help: report something, or fix something.

## Reporting a missing or better copy

Open an issue with:

* the season and episode number (`S06E10`)
* the guest name as it appears on the
  [Wikipedia episode list](https://en.wikipedia.org/wiki/List_of_Inside_the_Actors_Studio_episodes)
* where the copy came from: broadcast, DVD, streaming rip, private collection
* runtime, and resolution if you know it

If you have the file, attach it to the issue. A maintainer saves it
immediately, deletes the attachment from GitHub, and closes the issue once the
file is verified and in the archive. Nothing stays hosted on GitHub.

## Adding an episode to the archive

1. Save the file from the issue attachment.
2. Name it following the convention below.
3. Run `itas index` to refresh the snapshot, then `itas audit` to confirm the
   file is picked up and matches Wikipedia.
4. Run `itas render --write` to regenerate the checklist in
   `available-global.txt`.
5. Add an entry to `CHANGELOG.md` under today's date.
6. Delete the attachment from the issue and close it.

## Filename convention

```text
S{SS}E{EE}.{GuestNamePascalCase}-{YYYY.MM.DD}.ITAS.{SD|HD}[cut].mp4
```

* season and episode zero-padded to two digits
* guest name in PascalCase, no spaces, no punctuation
* air date from Wikipedia as `YYYY.MM.DD`
* `SD` below 720p, `HD` at or above
* alternate cuts get a numeric suffix: `SD1`, `SD2`, `HD1`

`itas verify-names` checks all of this. Files that predate the convention are
listed by name in `itas/naming.py` with a reason. Do not add new exceptions
without one.

## Working on the tooling

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

make test     # pytest
make lint     # ruff
make audit    # full cross-check
```

| Module | Responsibility |
| --- | --- |
| `model.py` | `Episode`, `ArchiveEntry`, `EpisodeCode`, file loading |
| `wiki.py` | MediaWiki table parser |
| `drive.py` | Drive API v3 client, recursive folder walk |
| `naming.py` | Filename convention, legacy exception list |
| `audit.py` | Cross-checks and the `Finding` model |
| `render.py` | Generates the availability checklist |
| `export.py` | JSON, CSV and TXT exports |
| `cli.py` | The `itas` command |

Keep the audit checks pure. They take data in and return `Finding` objects,
with no printing or file access. The CLI does the I/O. That split keeps the
test suite fast enough to run on every push.

### Adding a check

1. Write `check_something(episodes, entries) -> list[Finding]` in `audit.py`.
2. Call it from `run_audit`.
3. Add tests to `tests/test_audit.py` for the clean case and the dirty case.

### Refreshing the data

Both data files are committed so the repository is auditable offline:

```bash
itas parse-wiki                      # data/episodes.json from the wikitext
itas index --folder <drive-url>      # data/drive_snapshot.{json,csv,txt}
```

`itas index` needs `GDRIVE_API_KEY` set to a key with the Drive API enabled.
Both commands rewrite files in place. Commit the result together with the
changelog entry that explains it.

## Commit messages

Imperative mood, and say why rather than only what:

```
Add S06E10 Philip Seymour Hoffman from the Biography Channel master

The UK broadcast runs 41m21s against the 38m syndicated cut, so this is
the longest version known. Only Mary Tyler Moore remains missing in S6.
```

`Update README.md`-style messages make the history unreadable a year later.
