# Inside the Actors Studio (1994–2018) — Archive Toolset & Verification Suite

A set of automated Python tools, canonical metadata datasets, and verification scripts for tracking, indexing, restoring, and managing the comprehensive digital preservation archive of James Lipton's **Inside the Actors Studio**.

---

## Current Preservation Status

* **Canonical Wikipedia Series Episodes**: **277 episodes** (Seasons 1–23)
* **Preserved Numbered Episodes in Archive**: **225 / 277** (**81.2% Complete**)
* **Preserved Season 0 Specials & Extras**: **13 items**
* **Total Media in Archive**: **319 items** (294 video files across 25 season folders, ~165+ GB)
* **Remaining Missing Episodes**: **52 episodes**

---

## Repository Structure

```text
itas-episodes/
├── drive_indexer.py              # Recursive Google Drive API v3 folder crawler & exporter
├── wiki_episodes.json            # Structured dataset of all 277 canonical series episodes
├── wikipedia_itas.wikitext       # Raw MediaWiki source wikitext
├── parse_wiki.py                 # MediaWiki table parser for canonical metadata extraction
│
├── itas_episodes.json            # Google Drive archive metadata database (319 items)
├── itas_episodes.csv             # Spreadsheet export of drive contents
├── itas_episodes_files.txt       # Flat relative path list of drive archive
│
├── verify_all_episodes.py        # 3-way auditor (Wikipedia vs. Drive vs. Post Markdown)
├── contrast_drive_wiki_post.py   # Live audit & discrepancy engine
├── verify_announcements.py       # Validates changelog dates against Wikipedia air dates
│
├── reddit_post_global-new.txt    # Master Reddit Markdown post with mirrors & update log
├── reddit_post_dhexchange.txt    # r/DHExchange community variant
├── reddit_post_lostmedia.txt     # r/lostmedia community variant
├── reddit_post_forgottentv.txt   # r/ForgottenTV community variant
├── generate_community_posts.py   # Generates all community variants from master post
│
├── encode_episodes.py            # FFmpeg deinterlacer & MP4 standardizer (+faststart)
├── CATCHUP.md                    # Developer and archive state reference
└── .gitignore                    # Media exclusions (video files, ISOs, staging directories)
```

---

## Tools & Usage

### 1. Google Drive Recursive Indexer (`drive_indexer.py`)
Scans any public Google Drive directory and generates structured index files with MD5 checksums, file sizes, and download links:

```bash
python3 drive_indexer.py "YOUR_FOLDER_ID" --api-key "YOUR_API_KEY" -f json -o itas_episodes.json
python3 drive_indexer.py "YOUR_FOLDER_ID" --api-key "YOUR_API_KEY" -f csv -o itas_episodes.csv
python3 drive_indexer.py "YOUR_FOLDER_ID" --api-key "YOUR_API_KEY" -f txt --files-only -o itas_episodes_files.txt
```

### 2. Full Archive Verification (`verify_all_episodes.py`)
Cross-references every file in the Google Drive database against the canonical [Wikipedia: List of Inside the Actors Studio episodes](https://en.wikipedia.org/wiki/List_of_Inside_the_Actors_Studio_episodes) and validates that the crossed/uncrossed statuses in the tracking markdown are 100% accurate:

```bash
python3 verify_all_episodes.py
```

### 3. File Naming Standard
Every episode file in the archive follows this strict canonical format:
```text
Season {SS}/S{SS}E{EE}.{GuestNamePascalCase}-{YYYY.MM.DD}.ITAS.{SD|HD}[cut].mp4
```

---

## Canonical Source of Truth
All episode numbers, season boundaries, original broadcast air dates, and guest names are prioritized strictly and exclusively from Wikipedia.
