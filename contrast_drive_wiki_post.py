import json
import re
import os

with open("wiki_episodes.json") as f:
    wiki_eps = json.load(f)

with open("itas_episodes.json") as f:
    drive_items = json.load(f)

with open("reddit_post_global-new.txt") as f:
    post_text = f.read()

drive_files = [x for x in drive_items if not x["is_directory"]]

# 1. Map (Season, Episode) from Drive
drive_episodes = {}
for f in drive_files:
    m = re.match(r"^S(\d+)E(\d+)", f["name"], re.IGNORECASE)
    if m:
        s = int(m.group(1))
        e = int(m.group(2))
        drive_episodes.setdefault((s, e), []).append(f)

# 2. Map (Season, Episode) from local Add Later
add_later_dir = "/Users/gefaass/Desktop/Documents/agent stuff/itas-episodes/Add Later"
add_later_episodes = {}
for root, dirs, files in os.walk(add_later_dir):
    for fn in files:
        m = re.match(r"^S(\d+)E(\d+)", fn, re.IGNORECASE)
        if m:
            s = int(m.group(1))
            e = int(m.group(2))
            full_p = os.path.join(root, fn)
            add_later_episodes.setdefault((s, e), []).append({
                "name": fn,
                "path": full_p,
                "size_mb": os.path.getsize(full_p) / (1024*1024)
            })

# 3. Parse post lines
post_lines = {}
for line in post_text.splitlines():
    m = re.search(r"^\*\s+(?:~~)?(S(\d+)E(\d+)\s+-\s+([^~]+))(?:~~)?", line)
    if m:
        s = int(m.group(2))
        e = int(m.group(3))
        if s > 0:
            post_lines[(s, e)] = {
                "guest": m.group(4).strip(),
                "crossed": line.strip().startswith("* ~~"),
                "raw_line": line
            }

print(f"==================================================")
print(f"LIVE DRIVE AUDIT SUMMARY")
print(f"==================================================")
print(f"Total Canonical Wikipedia Episodes: {len(wiki_eps)}")
print(f"Unique Episodes in Google Drive:     {len(drive_episodes)}")
print(f"Unique Episodes in Add Later:        {len(add_later_episodes)}")

# Episodes in Add Later that are NOT yet in Drive:
pending_upload = []
for k, v in add_later_episodes.items():
    if k not in drive_episodes:
        pending_upload.append((k, v))
print(f"Episodes in Add Later pending Drive upload: {len(pending_upload)}")
for k, v in sorted(pending_upload):
    for item in v:
        print(f"  Pending: S{k[0]:02d}E{k[1]:02d} -> {item['name']} ({item['size_mb']:.1f} MB)")

# Episodes in Drive that are crossed in Post:
errors_in_post = []
for k, v in sorted(drive_episodes.items()):
    if k in post_lines:
        if post_lines[k]["crossed"]:
            errors_in_post.append(f"IN DRIVE BUT CROSSED IN POST: S{k[0]:02d}E{k[1]:02d} ({post_lines[k]['guest']})")

# Episodes NOT in Drive and NOT in Add Later that are UNCROSSED in Post:
for k, v in sorted(post_lines.items()):
    if not v["crossed"]:
        if k not in drive_episodes and k not in add_later_episodes:
            errors_in_post.append(f"UNCROSSED IN POST BUT MISSING EVERYWHERE: S{k[0]:02d}E{k[1]:02d} ({v['guest']})")

print(f"\n==================================================")
print(f"POST VS DRIVE CONTRAST")
print(f"==================================================")
if not errors_in_post:
    print("ALL post episode statuses 100% MATCH Drive & Add Later reality!")
else:
    for err in errors_in_post:
        print("  [ERROR]", err)

# Check all Drive filenames against Wikipedia guest names and dates
print(f"\n==================================================")
print(f"DRIVE FILENAME VS WIKIPEDIA AUDIT")
print(f"==================================================")
wiki_map = {(ep["season"], ep["episode"]): ep for ep in wiki_eps}
naming_issues = []
for (s, e), flist in sorted(drive_episodes.items()):
    w = wiki_map.get((s, e))
    if not w:
        naming_issues.append(f"Episode S{s:02d}E{e:02d} in Drive is NOT in Wikipedia series table!")
        continue
    for f in flist:
        fn = f["name"]
        # check year in filename
        # Date pattern: YYYY.MM.DD
        m_date = re.search(r"(\d{4})\.(\d{2})\.(\d{2})", fn)
        # We know wiki air_date format: Month DD, YYYY
        # We can extract year from wiki
        m_wiki_year = re.search(r"\b(\d{4})\b", w["air_date"])
        if m_date and m_wiki_year:
            file_year = m_date.group(1)
            wiki_year = m_wiki_year.group(1)
            if file_year != wiki_year:
                naming_issues.append(f"Year mismatch in {fn}: file has {file_year}, wiki has {wiki_year} ({w['air_date']})")

if not naming_issues:
    print("All Drive file years and series episodes match Wikipedia!")
else:
    for issue in naming_issues[:10]:
        print("  [NOTE]", issue)

print(f"\nTotal Drive Episodes Count: {len(drive_episodes)} / {len(wiki_eps)} ({len(drive_episodes)/len(wiki_eps)*100:.1f}%)")
