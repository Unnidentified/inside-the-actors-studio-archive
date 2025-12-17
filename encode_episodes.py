import os
import subprocess
import sys

base_dir = "/Users/gefaass/Desktop/Documents/agent stuff/itas-episodes/Add Later"

tasks = [
    {
        "name": "Philip Seymour Hoffman",
        "input": "/tmp/title2_hoffman.mp4",
        "season_folder": "Season 06",
        "filename": "S06E10.PhilipSeymourHoffman-2000.06.04.ITAS.SD.mp4"
    },
    {
        "name": "Edward Norton",
        "input": "/tmp/title1_norton.mp4",
        "season_folder": "Season 09",
        "filename": "S09E08.EdwardNorton-2002.12.15.ITAS.SD3.mp4"
    }
]

for t in tasks:
    out_dir = os.path.join(base_dir, t["season_folder"])
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, t["filename"])
    
    print(f"\n==========================================")
    print(f"Encoding: {t['name']}")
    print(f"Target: {out_path}")
    print(f"==========================================")
    
    cmd = [
        "/opt/homebrew/bin/ffmpeg",
        "-y",
        "-i", t["input"],
        "-vf", "bwdif=mode=send_frame:parity=auto:deint=all,scale=768:576",
        "-c:v", "libx264",
        "-crf", "19",
        "-preset", "fast",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        out_path
    ]
    
    res = subprocess.run(cmd)
    if res.returncode == 0:
        sz_mb = os.path.getsize(out_path) / (1024 * 1024)
        print(f"[Done] Finished {t['name']} -> {out_path} ({sz_mb:.2f} MB)")
    else:
        print(f"[Error] Encoding failed for {t['name']} with code {res.returncode}", file=sys.stderr)
        sys.exit(res.returncode)

print("\nAll encodings completed successfully!")
