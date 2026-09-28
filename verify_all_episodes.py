import json
import re

with open("wiki_episodes.json") as f:
    wiki_eps = json.load(f)

with open("itas_episodes.json") as f:
    drive_items = json.load(f)

with open("reddit_post_global-new.txt") as f:
    text = f.read()

drive_files = [x for x in drive_items if not x["is_directory"]]

# Set of (season, episode) in Drive
drive_available = set()
for f in drive_files:
    m = re.match(r"^S(\d+)E(\d+)", f["name"], re.IGNORECASE)
    if m:
        drive_available.add((int(m.group(1)), int(m.group(2))))

# Episodes staged in Add Later:
# 1.12 Pollack, 3.11 Quinn, 4.10 Lemmon, 5.11 Leigh, 6.10 Hoffman, 6.13 Weaver, 7.1 Peters, 7.15 Williams, 7.18 Reynolds,
# 8.7 Channing, 8.17 Redgrave, 9.8 Norton, 11.22 Elton John, 12.1 Producers, 12.3 Latifah, 14.1 SJP, 15.2 Chappelle,
# 15.4 Brolin, 15.8 LaPaglia, 21.1 Silverman, 21.2 Cranston, 21.4 Daniels, 22.1 Chastain, 22.7 Danson
add_later = {
    (1, 12), (3, 11), (4, 10), (5, 11), (6, 10), (6, 13), (7, 1), (7, 15), (7, 18),
    (8, 7), (8, 17), (9, 8), (11, 22), (12, 1), (12, 3), (14, 1), (15, 2), (15, 4),
    (15, 8), (21, 1), (21, 2), (21, 4), (22, 1), (22, 7)
}

all_available = drive_available.union(add_later)

# Parse episodes from text
text_lines = {}
for line in text.splitlines():
    m = re.search(r"^\*\s+(?:~~)?(S(\d+)E(\d+)\s+-\s+([^~]+))(?:~~)?", line)
    if m:
        s = int(m.group(2))
        e = int(m.group(3))
        if s > 0: # only seasons 1-23
            guest_text = m.group(4).strip()
            crossed = line.strip().startswith("* ~~")
            text_lines[(s, e)] = {"guest": guest_text, "crossed": crossed, "line": line}

print(f"Total series episodes parsed from text: {len(text_lines)} / {len(wiki_eps)}")

# Verification checks
discrepancies = []
for ep in wiki_eps:
    key = (ep["season"], ep["episode"])
    wiki_guest = ep["guest"]
    
    if key not in text_lines:
        discrepancies.append(f"MISSING FROM TEXT: S{key[0]:02d}E{key[1]:02d} - {wiki_guest}")
        continue
    
    t = text_lines[key]
    text_guest = t["guest"]
    is_crossed = t["crossed"]
    is_avail = key in all_available
    
    # 1. Guest name check (case-insensitive substring)
    clean_text_guest = re.sub(r"\s*-\s*second visit|\s*\(\d+\)", "", text_guest, flags=re.I).strip()
    clean_wiki_guest = re.sub(r"\s*\(second visit\)|\s*\(2\)", "", wiki_guest, flags=re.I).strip()
    if clean_wiki_guest.lower() not in clean_text_guest.lower() and clean_text_guest.lower() not in clean_wiki_guest.lower():
        # Special check for Cast of
        if not ("cast of" in clean_wiki_guest.lower() and "cast of" in clean_text_guest.lower()):
            discrepancies.append(f"NAME MISMATCH S{key[0]:02d}E{key[1]:02d}: text='{text_guest}' vs wiki='{wiki_guest}'")
            
    # 2. Availability / crossed check
    # If is_avail is True, it should NOT be crossed (except S06E10 which is pending uncross!)
    if is_avail and is_crossed:
        discrepancies.append(f"SHOULD BE UNCROSSED: S{key[0]:02d}E{key[1]:02d} - {wiki_guest} (found in archive/Add Later)")
    elif not is_avail and not is_crossed:
        discrepancies.append(f"SHOULD BE CROSSED: S{key[0]:02d}E{key[1]:02d} - {wiki_guest} (NOT found in archive/Add Later)")

print("\n--- Discrepancies Found ---")
if not discrepancies:
    print("None! 100% Match!")
else:
    for d in discrepancies:
        print(" ", d)

print(f"\nTotal Available: {len(all_available)} / {len(wiki_eps)} ({len(all_available)/len(wiki_eps)*100:.1f}%)")
print(f"Total Missing: {len(wiki_eps) - len(all_available)}")
