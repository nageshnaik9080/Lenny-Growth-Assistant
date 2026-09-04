"""
Download/clone a permitted transcript archive into /app/transcripts.

Usage examples:
  TRANSCRIPT_SOURCE_URL=https://example.com/repo.git GIT_REPOSITORY=1 python scripts/download_transcripts.py
  TRANSCRIPT_SOURCE_URL=https://example.com/archive.zip python scripts/download_transcripts.py

The assignment calls for a public Lenny transcript repository. This script intentionally
takes the source URL as configuration so the repository owner can change its public
location without changing application code.
"""
import os
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path

DEST = Path(os.getenv("TRANSCRIPT_DIR", "/app/transcripts"))
URL = os.getenv("TRANSCRIPT_SOURCE_URL", "").strip()

if not URL:
    raise SystemExit("Set TRANSCRIPT_SOURCE_URL to the permitted public transcript archive/repository URL.")

DEST.mkdir(parents=True, exist_ok=True)

if os.getenv("GIT_REPOSITORY", "0") == "1" or URL.endswith(".git"):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["git", "clone", "--depth", "1", URL, tmp], check=True)
        for p in Path(tmp).rglob("*"):
            if p.is_file() and p.suffix.lower() in {".md", ".txt"}:
                target = DEST / p.name
                shutil.copy2(p, target)
    print(f"Copied transcript files to {DEST}")
elif URL.lower().endswith(".zip"):
    with tempfile.NamedTemporaryFile(suffix=".zip") as f:
        urllib.request.urlretrieve(URL, f.name)
        with zipfile.ZipFile(f.name) as z:
            for name in z.namelist():
                if Path(name).suffix.lower() in {".md", ".txt"} and not name.endswith("/"):
                    target = DEST / Path(name).name
                    target.write_bytes(z.read(name))
    print(f"Extracted transcript files to {DEST}")
else:
    raise SystemExit("Unsupported source. Use a Git repository or .zip archive, or copy .md/.txt files into transcripts/.")
