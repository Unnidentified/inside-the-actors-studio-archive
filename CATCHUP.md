# CATCHUP — Inside the Actors Studio Archive Project

- **Workspace**: `/Users/gefaass/Desktop/Documents/agent stuff/itas-episodes`
- **GitHub Repository**: [Unnidentified/inside-the-actors-studio-archive](https://github.com/Unnidentified/inside-the-actors-studio-archive)
- **GitHub Account / Committer**: `Bannatar <107312024+Unnidentified@users.noreply.github.com>`
- **Last Updated**: 2026-09-28

---

## 1. Project Overview & Rules
* **Curator**: User ("Inside the Actors Studio Library Guy") preserving all episodes with correct metadata, dates, and order.
* **Canonical Source of Truth**: Metadata (seasons, episode numbering, dates, guests) comes **strictly and exclusively** from [Wikipedia: List of Inside the Actors Studio episodes](https://en.wikipedia.org/wiki/List_of_Inside_the_Actors_Studio_episodes).
* **Canonical Dataset**: 277 numbered series episodes (Seasons 1–23) parsed into `wiki_episodes.json` via `parse_wiki.py` and `wikipedia_itas.wikitext`.
* **Drive File Naming Standard**:
  `Season {SS}/S{SS}E{EE}.{GuestNamePascalCase}-{YYYY.MM.DD}.ITAS.{SD|HD}[cut].mp4`
* **Video Quality Standard**: H.264 video, AAC stereo audio (192 kbps), 4:3 deinterlaced (`bwdif`), `+faststart` web-optimized container.

---

## 2. Archive Preservation Status
* **Canonical Series Episodes**: **277 total**
* **Series Episodes in Google Drive**: **225 / 277** (**81.2% Complete**)
* **Season 0 Specials / Extras in Google Drive**: **13 items**
* **Total Drive Entries**: **238 items** (319 files including alt cuts/qualities, ~165+ GB)
* **Remaining Missing Episodes**: **52 episodes**

---

## 3. Recent Restorations
* **2026-09-28**:
  * `[S06E10]` **Philip Seymour Hoffman** (June 4, 2000) — Recovered from UK/Europe Biography Channel DVD master (41m 21s). Only 1 missing episode remains in Season 6 (*Mary Tyler Moore*).
  * `[S09E08]` **Edward Norton** (January 12, 2003) — Upgraded to 1.08 GB broadcast master cut.
* **2026-09-06**:
  * `[S03E11]` **Anthony Quinn** (May 19, 1996) — Recovered full English episode (809 MB).
  * `[S12E03]` **Queen Latifah** (January 8, 2006) — Recovered broadcast recording (Russian dub overdub).
* **2026-08-27**:
  * `[S01E12]` **Sydney Pollack** (August 28, 1994) — Recovered full episode.
  * Plus 13 additional restores (Jack Lemmon, Jennifer Jason Leigh, Sigourney Weaver, Burt Reynolds, Stockard Channing, Vanessa Redgrave, Cast of The Producers, Sarah Jessica Parker, Anthony LaPaglia, Sarah Silverman, Jeff Daniels, Jessica Chastain).

---

## 4. Key Project Files
* **Master Reddit Post**: [`reddit_post_global-new.txt`](file:///Users/gefaass/Desktop/Documents/agent%20stuff/itas-episodes/reddit_post_global-new.txt)
  * Includes mirrors (`r/lostmedia`, `r/ForgottenTV`, `r/DHExchange`, `r/acting`) and updated changelog.
* **Community Variants**: `reddit_post_dhexchange.txt`, `reddit_post_lostmedia.txt`, `reddit_post_forgottentv.txt` (generated via `generate_community_posts.py`).
* **Google Drive Index**: `itas_episodes.json`, `itas_episodes.csv`, `itas_episodes_files.txt`.
* **Auditing Tools**:
  * `verify_all_episodes.py`: 3-way check verifying Wikipedia vs. Drive vs. Reddit post.
  * `contrast_drive_wiki_post.py`: Detailed live audit tool.
  * `drive_indexer.py`: Public Google Drive folder crawler.
  * `encode_episodes.py`: Standardized FFmpeg deinterlacing & encoding tool.

---

## 5. Workflow for Future Episodes
1. New files land in `Add Later/`.
2. Check `ffprobe` for stream info, aspect ratio, audio layout.
3. Look up exact canonical season, episode number, and original broadcast air date on Wikipedia.
4. Encode to universal H.264/AAC MP4 (`+faststart`) into `Add Later/Season XX/S{SS}E{EE}.{Guest}-{YYYY.MM.DD}.ITAS.{SD|HD}.mp4`.
5. User uploads file to Google Drive.
6. Re-run `drive_indexer.py` & `verify_all_episodes.py`.
7. Update `reddit_post_global-new.txt` (uncross episode, update header count, add dated changelog block).
8. Delete local files from `Add Later/` after verifying online in Drive to preserve disk space.
9. Commit changes to Git with author `Bannatar <107312024+Unnidentified@users.noreply.github.com>`.
