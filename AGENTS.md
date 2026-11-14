# Working notes for coding agents

Repo-specific conventions. Read this before opening a PR or touching the
audit tooling.

## Pull requests

**Do not add the Replicas workspace footer to pull request descriptions in
this repository.** No `replicas.dev/pr-footer-workspace.svg` block, no
"Created by … with Replicas" line. Write the description as a normal
contributor would.

Keep the co-author trailers (`Co-Authored-By: Bannatar`,
`Co-Authored-By: replicas-connector[bot]`) on commits and PR descriptions —
only the footer block is unwanted.

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

`docs/known-issues.md` lists problems that are understood but not fixed,
including `S15E02` (a James Lipton special filed under the Dave Chappelle slot)
and the 33 files that predate the filename convention. Read it before
"fixing" either.
