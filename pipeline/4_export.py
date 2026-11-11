"""Write web images to static/photos/ and the photo list to src/lib/data/.

src/lib/data/captions.json is hand-editable: ids already in it are never
overwritten, so caption corrections survive re-running the pipeline.
"""
import json, re
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "pipeline" / "work"
DATA = ROOT / "src" / "lib" / "data"
OUT = ROOT / "static" / "photos"

SIZES = {"original": 1800, "enhanced": 1800, "thumb": 480}


def tidy(text):
    text = re.sub(r"(\w)- (\w)", r"\1\2", text)          # re-join words hyphenated across lines
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s*\bText\b$", "", text)               # stray "Text" label from Photos markup
    return text


def blank(strip):
    """A plain white or black strip, e.g. the band a caption sat on after it was erased."""
    return strip.std() < 6 and (strip.mean() > 235 or strip.mean() < 20)


def trim_box(img):
    """Fractions (left, top, right, bottom) that cut off blank bands at the edges (max 30% a side)."""
    a = np.asarray(img.convert("L"), np.float32)
    h, w = a.shape
    top = next((y for y in range(int(h * 0.3)) if not blank(a[y])), 0)
    bottom = next((y for y in range(h - 1, int(h * 0.7), -1) if not blank(a[y])), h - 1) + 1
    left = next((x for x in range(int(w * 0.3)) if not blank(a[:, x])), 0)
    right = next((x for x in range(w - 1, int(w * 0.7), -1) if not blank(a[:, x])), w - 1) + 1
    return left / w, top / h, right / w, bottom / h


def save_webp(src, dest, long_edge, box):
    img = Image.open(src).convert("RGB")
    w, h = img.size
    img = img.crop((round(box[0] * w), round(box[1] * h), round(box[2] * w), round(box[3] * h)))
    img.thumbnail((long_edge, long_edge), Image.LANCZOS)
    img.save(dest, "WEBP", quality=80, method=6)
    return img.size


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    captions_file = DATA / "captions.json"
    captions = json.loads(captions_file.read_text()) if captions_file.exists() else {}
    for id_, c in json.loads((WORK / "captions.json").read_text()).items():
        captions.setdefault(id_, tidy(c["caption"]))
    captions_file.write_text(json.dumps(captions, indent=1, ensure_ascii=False))

    photos = []
    for id_ in captions:
        folder = OUT / id_
        folder.mkdir(parents=True, exist_ok=True)
        clean = WORK / "clean" / f"{id_}.jpg"
        box = trim_box(Image.open(clean))
        width, height = save_webp(clean, folder / "original.webp", SIZES["original"], box)
        save_webp(clean, folder / "thumb.webp", SIZES["thumb"], box)
        enhanced = WORK / "enhanced" / f"{id_}.jpg"
        if enhanced.exists():
            save_webp(enhanced, folder / "enhanced.webp", SIZES["enhanced"], box)
        photos.append({"id": id_, "width": width, "height": height, "enhanced": enhanced.exists()})
    (DATA / "photos.json").write_text(json.dumps(photos, indent=1))
    print(f"exported {len(photos)} photos")


if __name__ == "__main__":
    main()
