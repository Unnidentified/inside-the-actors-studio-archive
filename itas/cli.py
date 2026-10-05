"""Command line interface for the archive tooling.

    itas index   --folder <url|id> [--out data/]     refresh the Drive snapshot
    itas audit   [--strict]                          cross-check everything
    itas verify-names                                check filename conventions
    itas render  [--write]                           regenerate the checklist
    itas parse-wiki                                  rebuild data/episodes.json

Every command reads from ``data/`` by default, so a checkout is auditable
without network access or credentials.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

from . import __version__
from .audit import run_audit
from .drive import DriveClient, extract_folder_id
from .export import write_exports
from .model import DataError, load_archive, load_episodes
from .naming import check_entries, stale_exceptions
from .render import render_checklist
from .wiki import parse_episodes

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA = REPO_ROOT / "data"
DEFAULT_TRACKING = REPO_ROOT / "available-global.txt"

#: Headings that introduce the generated checklist. The master post uses the
#: first; the README uses the second.
CHECKLIST_HEADINGS = ("# Updated Episode List", "## Availability checklist")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="itas",
        description="Audit and maintain the Inside the Actors Studio archive.",
    )
    parser.add_argument("--version", action="version", version=f"itas {__version__}")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA,
        help="directory holding the Drive snapshot and episode list",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    index = sub.add_parser("index", help="refresh the Drive snapshot")
    index.add_argument("--folder", required=True, help="Drive folder URL or id")
    index.add_argument(
        "--api-key",
        default=os.environ.get("GDRIVE_API_KEY"),
        help="Drive API key (defaults to $GDRIVE_API_KEY)",
    )
    index.add_argument("--out", type=Path, help="output directory (defaults to --data-dir)")
    index.add_argument(
        "--dry-run",
        action="store_true",
        help="report what would be written without touching the filesystem",
    )

    audit = sub.add_parser("audit", help="cross-check Wikipedia, Drive and the tracking doc")
    audit.add_argument("--tracking", type=Path, default=DEFAULT_TRACKING)
    audit.add_argument("--strict", action="store_true", help="exit non-zero on warnings too")
    audit.add_argument(
        "--allow-known-issues",
        action="store_true",
        help="treat documented known issues as informational (used by CI)",
    )
    audit.add_argument("--quiet", action="store_true", help="only print the summary")

    names = sub.add_parser("verify-names", help="check filenames against the convention")
    names.add_argument("--strict", action="store_true", help="exit non-zero on any problem")

    render = sub.add_parser("render", help="regenerate the availability checklist")
    render.add_argument(
        "--write",
        action="store_true",
        help="rewrite the checklist section of the tracking document in place",
    )
    render.add_argument(
        "--also",
        type=Path,
        action="append",
        default=[],
        metavar="FILE",
        help="also rewrite the checklist in this file (repeatable)",
    )

    sub.add_parser("parse-wiki", help="rebuild data/episodes.json from the wikitext")
    return parser


def load_inputs(data_dir: Path):
    episodes_path = data_dir / "episodes.json"
    snapshot_path = data_dir / "drive_snapshot.json"
    if not episodes_path.exists():
        raise DataError(f"{episodes_path} is missing; run `itas parse-wiki` first")
    if not snapshot_path.exists():
        raise DataError(f"{snapshot_path} is missing; run `itas index` first")
    return load_episodes(episodes_path), load_archive(snapshot_path)


def cmd_index(args: argparse.Namespace) -> int:
    folder_id = extract_folder_id(args.folder)
    print(f"Indexing Drive folder {folder_id} ...", file=sys.stderr)
    entries = DriveClient(args.api_key).index(folder_id)
    out_dir = args.out or args.data_dir
    if args.dry_run:
        files = [e for e in entries if not e.is_directory]
        print(
            f"Dry run: would write {len(entries)} items ({len(files)} files) to {out_dir}",
            file=sys.stderr,
        )
        return 0
    outputs = write_exports(entries, out_dir)
    files = [e for e in entries if not e.is_directory]
    print(
        f"Indexed {len(entries)} items ({len(files)} files) into {out_dir}",
        file=sys.stderr,
    )
    for kind, path in outputs.items():
        print(f"  {kind}: {path}", file=sys.stderr)
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    episodes, entries = load_inputs(args.data_dir)
    tracking_text = args.tracking.read_text(encoding="utf-8") if args.tracking.exists() else None
    if tracking_text is None:
        print(f"warning: {args.tracking} not found, skipping tracking checks", file=sys.stderr)

    report = run_audit(episodes, entries, tracking_text)
    print(report.coverage.summary())

    if not args.quiet:
        for finding in report.findings:
            print(f"  {finding}")
        if not report.findings:
            print("  no findings")

    print(
        f"\n{len(report.errors)} error(s), {len(report.warnings)} warning(s)",
        file=sys.stderr,
    )
    if report.errors:
        return 1
    if args.strict and report.warnings:
        return 1
    return 0


def cmd_verify_names(args: argparse.Namespace) -> int:
    _, entries = load_inputs(args.data_dir)
    problems = check_entries(entries)
    for problem in problems:
        print(f"  {problem}")
    for name in stale_exceptions(entries):
        print(f"  stale exception, remove from naming.LEGACY_EXCEPTIONS: {name}")
    if not problems:
        print("All video filenames match the convention.")
    return 1 if (problems and args.strict) else 0


def cmd_render(args: argparse.Namespace) -> int:
    episodes, entries = load_inputs(args.data_dir)
    checklist = render_checklist(episodes, entries)
    targets = list(args.also)
    if args.write:
        targets.insert(0, DEFAULT_TRACKING)
    if not targets:
        print(checklist, end="")
        return 0
    for target in targets:
        _replace_checklist(target, checklist)
        print(f"Rewrote the checklist in {target}", file=sys.stderr)
    return 0


def _replace_checklist(path: Path, checklist: str) -> None:
    """Swap the generated checklist into a document.

    The checklist sits between the document's checklist heading and the next
    top-level heading; everything else in the file is left alone.
    """
    text = path.read_text(encoding="utf-8")
    start = -1
    level = 0
    for heading in CHECKLIST_HEADINGS:
        index = text.find(heading)
        if index != -1:
            start, level = index, len(heading) - len(heading.lstrip("#"))
            break
    if start == -1:
        raise DataError(
            f"{path} has none of the checklist headings: {', '.join(CHECKLIST_HEADINGS)}"
        )
    body_start = text.find("\n", start) + 1
    # Stop at the next heading of the same or a higher level.
    boundary = re.compile(rf"^#{{1,{level}}}\s", re.MULTILINE)
    match = boundary.search(text, body_start)
    body_end = match.start() if match else len(text)
    # Keep the horizontal rule that separates the checklist from what follows.
    separator = text[body_end:]
    if separator.lstrip().startswith("---"):
        checklist = checklist + "\n---\n"
    updated = text[:body_start] + "\n" + checklist + "\n" + text[body_start:body_start] + separator
    path.write_text(updated, encoding="utf-8")


def cmd_parse_wiki(args: argparse.Namespace) -> int:
    wikitext_path = args.data_dir / "wikipedia_itas.wikitext"
    if not wikitext_path.exists():
        raise DataError(f"{wikitext_path} is missing")
    episodes = parse_episodes(wikitext_path.read_text(encoding="utf-8"))
    payload = [
        {
            "season": ep.code.season,
            "episode": ep.code.episode,
            "air_date": f"{ep.air_date.strftime('%B')} {ep.air_date.day}, {ep.air_date.year}",
            "guest": ep.guest,
        }
        for ep in episodes
    ]
    out_path = args.data_dir / "episodes.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Parsed {len(episodes)} episodes into {out_path}", file=sys.stderr)
    return 0


COMMANDS = {
    "index": cmd_index,
    "audit": cmd_audit,
    "verify-names": cmd_verify_names,
    "render": cmd_render,
    "parse-wiki": cmd_parse_wiki,
}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return COMMANDS[args.command](args)
    except DataError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
