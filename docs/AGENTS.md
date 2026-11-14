# Working notes for coding agents

Repo-specific conventions. Read this before opening a PR or touching the
audit tooling.

## Writing style

Write like a person, not like a model.

**No em dashes anywhere.** Not in chat replies, PR descriptions, commit
messages, documentation, code comments or generated output. Use a comma, a
colon, a semicolon, parentheses, or split the sentence in two. En dashes in
numeric ranges (`1994-2018`, `seasons 1-23`) are fine. The ban is on the em
dash character only.

**No rhetorical tics.** Specifically avoid:

- `It's not X, it's Y` and every variant of the pattern: `This isn't about X,
  it's about Y`, `The problem isn't X. It's Y.`, `Not X. Not Y. But Z.`
- `honest`, `honestly`, `to be honest`, `let me be candid`, `I'll be blunt`
- `delve`, `leverage`, `robust`, `seamless`, `elevate`, `unlock`, `foster`,
  `landscape`, `testament to`, `at the end of the day`
- `Let's break it down`, `Here's the thing`, `The bottom line is`, `It's worth
  noting that`, `It's important to note that`
- Rule-of-three lists used for rhythm rather than content
- Opening with a summary paragraph that repeats the heading
- Closing with a restatement of what was just said
- Bolded lead-ins on every bullet
- Emoji in prose

State the thing. Give the reason. Stop.

## Attribution

**Do not list the agent tooling as a contributor or participant anywhere.**
Not as a commit author, not as a co-author trailer, not as a PR author or
reviewer, not in changelogs or acknowledgements, not in `package.json`-style
metadata. Commits are authored and committed by Bannatar
(`107312024+Unnidentified@users.noreply.github.com`).

## Pull requests

Do not add a generated workspace footer to pull request descriptions. Write
the description as a normal contributor would: what changed, why, and how it
was verified.

## Contributing flow

Contributors attach episode files **directly to a GitHub issue**. A maintainer
saves the file, deletes the attachment from GitHub, and closes the issue once
it is verified and in the archive. Do not point people at a Drive staging
folder; nothing should stay hosted on GitHub.

## Checks before pushing

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

pytest                  # 118 tests
ruff check .            # lint
itas audit --strict     # cross-check Wikipedia / Drive / checklist
itas verify-names --strict
```

All four must pass. `itas audit` exits non-zero on any error; known issues are
downgraded to INFO in `itas/audit.py::KNOWN_ISSUES` so CI stays green.

## Data files are generated

`data/episodes.json`, `data/drive_snapshot.*` and the availability checklist in
`README.md` and `available-global.txt` are all generated. Do not hand-edit
them:

```bash
itas parse-wiki                              # rebuild data/episodes.json
itas index --folder <drive-url>              # rebuild the snapshot (needs GDRIVE_API_KEY)
itas render --write --also README.md         # regenerate both checklists
```

## Known issues

`known-issues.md` in this folder lists problems that are understood but not fixed,
including `S15E02` (a James Lipton special filed under the Dave Chappelle slot)
and the 33 files that predate the filename convention. Read it before
"fixing" either.
