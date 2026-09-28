import json
import re

with open("wiki_episodes.json") as f:
    wiki_eps = json.load(f)

with open("itas_episodes.json") as f:
    drive_items = json.load(f)

drive_files = [x for x in drive_items if not x["is_directory"]]

# Set of available (season, episode) from Drive
available = set()
for f in drive_files:
    m = re.match(r"^S(\d+)E(\d+)", f["name"], re.IGNORECASE)
    if m:
        available.add((int(m.group(1)), int(m.group(2))))

# Add all episodes staged in Add Later
# Note: Sydney Pollack (1, 12), Anthony Quinn (3, 11), Queen Latifah (12, 3), Philip Seymour Hoffman (6, 10), Edward Norton (9, 8)
add_later_eps = {
    (1, 12), (3, 11), (4, 10), (5, 11), (6, 10), (6, 13), (7, 1), (7, 15), (7, 18),
    (8, 7), (8, 17), (9, 8), (11, 22), (12, 1), (12, 3), (14, 1), (15, 2), (15, 4),
    (15, 8), (21, 1), (21, 2), (21, 4), (22, 1), (22, 7)
}
available = available.union(add_later_eps)

print(f"Total Canonical Wikipedia Episodes: {len(wiki_eps)}")
print(f"Total Available Episodes: {len(available)} ({len(available)/len(wiki_eps)*100:.1f}%)")
print(f"Total Missing Episodes: {len(wiki_eps) - len(available)}")

# Check dates mentioned in announcement blocks against Wikipedia
announcement_checks = [
    # 09/28/2026
    (6, 10, "Philip Seymour Hoffman", "June 4, 2000"),
    (9, 8, "Edward Norton", "January 12, 2003"),
    # 09/06/2026
    (3, 11, "Anthony Quinn", "May 19, 1996"),
    (12, 3, "Queen Latifah", "January 8, 2006"),
    # 08/27/2026
    (1, 12, "Sydney Pollack", "August 28, 1994"),
    (4, 10, "Jack Lemmon", "October 25, 1998"),
    (5, 11, "Jennifer Jason Leigh", "July 11, 1999"),
    (6, 13, "Sigourney Weaver", "October 29, 2000"),
    (7, 18, "Burt Reynolds", "August 6, 2001"),
    (8, 7, "Stockard Channing", "January 27, 2002"),
    (8, 17, "Vanessa Redgrave", "August 4, 2002"),
    (12, 1, "Cast of The Producers", "December 11, 2005"),
    (14, 1, "Sarah Jessica Parker", "May 19, 2008"),
    (15, 8, "Anthony LaPaglia", "February 2, 2009"),
    (21, 1, "Sarah Silverman", "October 22, 2015"),
    (21, 4, "Jeff Daniels", "January 7, 2016"),
    (22, 1, "Jessica Chastain", "December 21, 2016"),
    # 05/23/2026
    (7, 1, "Bernadette Peters", "November 12, 2000"),
    (7, 15, "Robin Williams", "June 10, 2001"),
    (11, 22, "Elton John", "October 16, 2005"),
    (15, 2, "Dave Chappelle", "November 11, 2008"),
    (15, 4, "Josh Brolin", "January 5, 2009"),
    (21, 2, "Bryan Cranston", "November 25, 2015"),
    (22, 7, "Ted Danson", "January 11, 2018"),
    # 03/01/2026
    (1, 6, "Sally Field", "July 18, 1994"),
    (1, 7, "Dennis Hopper", "July 23, 1994"),
    (1, 11, "Neil Simon", "August 21, 1994"),
    (2, 9, "Christopher Walken", "May 7, 1995"),
    (2, 12, "Martin Landau", "May 28, 1995"),
    (3, 4, "Anjelica Huston", "March 31, 1996"),
    (7, 7, "Ed Harris", "December 17, 2000"),
    (18, 2, "Brad Pitt", "February 10, 2012"),
    # 01/07/2026
    (2, 1, "Lee Grant", "March 12, 1995"),
    (3, 7, "Tommy Lee Jones", "April 21, 1996"),
    (9, 8, "Edward Norton", "January 12, 2003"),
    # 12/23/2025
    (3, 9, "Julia Roberts", "May 5, 1996"),
    (22, 6, "Kristen Wiig", "December 21, 2017")
]

print("\n--- Verifying Announcement Episodes against Wikipedia ---")
wiki_lookup = {(ep["season"], ep["episode"]): ep for ep in wiki_eps}

for s, e, guest, expected_date in announcement_checks:
    w = wiki_lookup.get((s, e))
    if not w:
        print(f"[ERROR] S{s:02d}E{e:02d} not found in Wikipedia!")
    else:
        date_ok = (w["air_date"] == expected_date)
        guest_ok = (guest.lower() in w["guest"].lower() or w["guest"].lower() in guest.lower())
        status = "OK" if (date_ok and guest_ok) else "MISMATCH"
        if not (date_ok and guest_ok):
            print(f"[{status}] S{s:02d}E{e:02d}: {guest} vs Wiki: {w['guest']}, Expected: {expected_date} vs Wiki: {w['air_date']}")

print("Announcement verification finished.")
