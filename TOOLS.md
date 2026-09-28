# Inside the Actors Studio (1994–2018) - Tools & Developer Reference

Documentation, command line parameters, and workflows for the archive verification suite and encoding toolset.

---

## <a id="1-google-drive-recursive-indexer-drive_indexerpy"></a><a id="google-drive-recursive-indexer"></a>1. Google Drive Recursive Indexer (`drive_indexer.py`)

Scans the public Google Drive directory and generates structured index files with MD5 checksums, file sizes, and download links.

### Usage

```bash
# JSON metadata export
python3 drive_indexer.py "YOUR_FOLDER_ID" --api-key "YOUR_API_KEY" -f json -o itas_episodes.json

# Spreadsheet CSV export
python3 drive_indexer.py "YOUR_FOLDER_ID" --api-key "YOUR_API_KEY" -f csv -o itas_episodes.csv

# Plain text file list
python3 drive_indexer.py "YOUR_FOLDER_ID" --api-key "YOUR_API_KEY" -f txt --files-only -o itas_episodes_files.txt
```

### Options

* `folder_id`: Google Drive folder ID to crawl recursively.
* `--api-key`: Google Cloud API Key with Google Drive API v3 enabled.
* `-f, --format`: Output format (`json`, `csv`, `txt`).
* `-o, --output`: Target output file path.
* `--files-only`: Omit directory paths from the text listing.

---

## <a id="2-full-3-way-archive-auditor-verify_all_episodespy"></a><a id="full-3-way-archive-auditor"></a>2. Full 3-Way Archive Auditor (`verify_all_episodes.py`)

Cross-references every file in the Google Drive database against the canonical [Wikipedia Episode Guide](https://en.wikipedia.org/wiki/List_of_Inside_the_Actors_Studio_episodes) and validates that the crossed/uncrossed statuses in the tracking markdown are 100% accurate.

### Usage

```bash
python3 verify_all_episodes.py
```

### Output Validation

* Verifies 277 canonical Wikipedia series episodes across Seasons 1–23.
* Contrasts live Drive files against `available-global.txt`.
* Reports remaining missing episodes and confirms formatting integrity.

---

## <a id="3-live-drive-contrast-engine-contrast_drive_wiki_postpy"></a><a id="live-drive-contrast-engine"></a>3. Live Drive Contrast Engine (`contrast_drive_wiki_post.py`)

Audits live Drive files against staged files in `Add Later/` and reports newly uploaded files and discrepancy reports.

### Usage

```bash
python3 contrast_drive_wiki_post.py
```

### Key Tasks

* Detects unstaged or unindexed video files.
* Compares file sizes and MD5 checksums between local files and remote storage.
* Prints discrepancy reports for uncatalogued episodes.

---

## <a id="4-ffmpeg-video-standardization-encode_episodespy"></a><a id="ffmpeg-video-standardization"></a>4. FFmpeg Video Standardization (`encode_episodes.py`)

Encodes and standardizes newly found raw broadcast rips into universal H.264/AAC MP4 with 4:3 deinterlacing (`bwdif`) and `+faststart` web optimization.

### Usage

```bash
python3 encode_episodes.py
```

### Encoding Specifications

* **Video Codec**: `libx264`, CRF 18, `preset=slow`, `pix_fmt=yuv420p`.
* **Audio Codec**: AAC stereo, 192 kbps, 48 kHz.
* **Deinterlacing Filter**: `bwdif=mode=1:parity=-1:deint=1` (motion-adaptive field rate doubling).
* **Container**: MP4 with `-movflags +faststart` for progressive streaming.

---

## <a id="5-mediawiki-table-parser-parse_wikipy"></a><a id="mediawiki-table-parser"></a>5. MediaWiki Table Parser (`parse_wiki.py`)

Extracts canonical episode metadata directly from raw MediaWiki source text (`wikipedia_itas.wikitext`) and produces structured JSON datasets (`wiki_episodes.json`).

### Usage

```bash
python3 parse_wiki.py
```

---

## <a id="file-naming-standard"></a>File Naming Standard

Every episode file in the archive follows this strict canonical format:

```text
Season {SS}/S{SS}E{EE}.{GuestNamePascalCase}-{YYYY.MM.DD}.ITAS.{SD|HD}[cut].mp4
```

* **Season & Episode**: Two-digit zero-padded (`S01E06`, `S12E03`).
* **Guest Name**: PascalCase without spaces (`PhilipSeymourHoffman`, `JackLemmon`).
* **Air Date**: Canonical Wikipedia air date formatted as `YYYY.MM.DD`.
* **Quality**: `SD` (standard definition, <720p) or `HD` (>=720p). Alternate cuts use `SD1`, `SD2`, `SD3`.
