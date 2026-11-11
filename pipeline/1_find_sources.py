"""List the unique photos in the source folder (many are exact copies) -> work/sources.json"""
import hashlib, json, sys
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parents[2]
WORK = Path(__file__).resolve().parent / "work"
IMAGE_EXTS = {".jpg", ".jpeg"}


def file_hash(path):
    return hashlib.md5(path.read_bytes()).hexdigest()


def find_sources():
    paths = sorted(
        p for p in SOURCE_DIR.rglob("*")
        if p.suffix.lower() in IMAGE_EXTS and "genealogy" not in p.parts
    )
    by_hash = {}
    for p in paths:
        by_hash.setdefault(file_hash(p), []).append(p)
    sources = []
    for h, copies in by_hash.items():
        best = min(copies, key=lambda p: ("(Copy" in p.name, len(p.name)))
        sources.append({"id": h[:10], "path": str(best), "copies": len(copies)})
    return sorted(sources, key=lambda s: s["path"])


if __name__ == "__main__":
    WORK.mkdir(exist_ok=True)
    sources = find_sources()
    (WORK / "sources.json").write_text(json.dumps(sources, indent=1))
    print(f"{len(sources)} unique photos", file=sys.stderr)
