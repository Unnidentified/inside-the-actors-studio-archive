import json
import re

with open("wikipedia_itas.wikitext") as f:
    text = f.read()

def clean_wiki_text(s):
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.DOTALL)
    s = re.sub(r"<ref[^>]*/>", "", s)
    s = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", s)
    s = s.replace("'''", "").replace("''", "")
    # remove leading/trailing HTML tags
    s = re.sub(r"<[^>]+>", "", s)
    return s.strip()

# Split by Season
seasons = re.findall(r"===Season (\d+)[^=]*===(.*?)(?====Season|==References|==External links|$)", text, re.DOTALL)

all_episodes = []

for s_num, s_text in seasons:
    s_int = int(s_num)
    # Find table rows
    rows = s_text.split("|-")
    for r in rows:
        lines = [l.strip() for l in r.split("\n") if l.strip()]
        cols = []
        for line in lines:
            if line.startswith("!"):
                continue
            if line.startswith("|"):
                content = line[1:].strip()
                if "||" in content:
                    parts = content.split("||")
                    for p in parts:
                        cols.append(p.strip())
                else:
                    cols.append(content)
        
        if len(cols) >= 3:
            ep_match = re.match(r"^(\d+)", cols[0])
            if ep_match:
                ep_num = int(ep_match.group(1))
                air_date = clean_wiki_text(cols[1])
                if s_int == 23 and len(cols) >= 4:
                    host = clean_wiki_text(cols[2])
                    guest = clean_wiki_text(cols[3])
                else:
                    guest = clean_wiki_text(cols[2])
                all_episodes.append({
                    "season": s_int,
                    "episode": ep_num,
                    "air_date": air_date,
                    "guest": guest,
                })

print(f"Total parsed episodes: {len(all_episodes)}")
with open("wiki_episodes.json", "w") as f:
    json.dump(all_episodes, f, indent=2)
