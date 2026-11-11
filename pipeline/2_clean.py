"""Erase the typed-on captions and save the clean photo + caption text.

Reads work/ocr.json (from ocr.swift). Writes work/clean/<id>.jpg,
work/masks/<id>.jpg (review sheet) and work/captions.json.
"""
import json, sys
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image, ImageOps
from simple_lama_inpainting import SimpleLama

WORK = Path(__file__).resolve().parent / "work"
CLEAN, MASKS = WORK / "clean", WORK / "masks"
# Photos whose text is all genuine (e.g. a newspaper clipping): never erase anything
KEEP_TEXT = {l.split("#")[0].strip() for l in (WORK.parent / "keep_text.txt").read_text().splitlines()} - {""}

WHITE_MIN, BLACK_MAX = 215, 50   # caption pixels incl. soft edges (what gets erased)
WHITE_CORE, BLACK_CORE = 242, 12 # typed text is near-pure; printed/photographed text is not
MIN_CONTRAST = 0.03              # text colour must be this much denser inside the box than around it


def color_masks(rgb):
    """(core, soft) masks per colour: core decides what is a caption, soft is what gets erased."""
    lo, hi = rgb.min(axis=2), rgb.max(axis=2)
    core = {"white": lo >= WHITE_CORE, "black": hi <= BLACK_CORE}
    soft = {"white": lo >= WHITE_MIN, "black": hi <= BLACK_MAX}
    return core, soft


def caption_color(masks, box, ring):
    """Which colour (white/black) is the typed text in this box, or None if it isn't typed text."""
    best, best_score = None, MIN_CONTRAST
    for name, m in masks.items():
        inside = m[box].mean()
        around = m[ring].mean() if ring.any() else 0.0
        if inside - around > best_score:
            best, best_score = name, inside - around
    return best


def line_mask(rgb, masks, line, text_area):
    """Pixel mask of the caption text for one OCR line (empty if it isn't caption text)."""
    H, W = rgb.shape[:2]
    pad = int(line["h"] * 0.35)
    y0, y1 = max(0, line["y"] - pad), min(H, line["y"] + line["h"] + pad)
    x0, x1 = max(0, line["x"] - pad), min(W, line["x"] + line["w"] + pad)
    r = line["h"]
    box = (slice(y0, y1), slice(x0, x1))
    ring_full = np.zeros((H, W), bool)
    ring_full[max(0, y0 - r):min(H, y1 + r), max(0, x0 - r):min(W, x1 + r)] = True
    ring_full &= ~text_area
    tight = (slice(line["y"], line["y"] + line["h"]), slice(line["x"], line["x"] + line["w"]))
    core, soft = masks
    color = caption_color(core, tight, ring_full)
    out = np.zeros((H, W), np.uint8)
    if color:
        out[box] = soft[color][box]
    return out, color


def caption_mask(rgb, lines):
    masks = color_masks(rgb)
    total = np.zeros(rgb.shape[:2], np.uint8)
    kept = []
    text_area = np.zeros(rgb.shape[:2], bool)
    for l in lines:
        pad = int(l["h"] * 0.35)
        text_area[max(0, l["y"] - pad):l["y"] + l["h"] + pad, max(0, l["x"] - pad):l["x"] + l["w"] + pad] = True
    for line in sorted(lines, key=lambda l: l["y"]):
        if line["conf"] < 0.5:
            continue
        m, color = line_mask(rgb, masks, line, text_area)
        if color:
            total |= m
            kept.append(line)
    if kept:
        grow = max(3, int(np.median([l["h"] for l in kept]) * 0.2))
        total = cv2.dilate(total, np.ones((grow, grow), np.uint8))
    return total, kept


def inpaint(lama, rgb, mask):
    """Run LaMa on a window around each caption block and paste the result back."""
    out = rgb.copy()
    H, W = mask.shape
    blocks = cv2.dilate(mask, np.ones((61, 61), np.uint8))
    n, _, stats, _ = cv2.connectedComponentsWithStats(blocks)
    for i in range(1, n):
        x, y, w, h = stats[i][:4]
        margin = max(96, h // 2)
        x0, y0 = max(0, x - margin), max(0, y - margin)
        x1, y1 = min(W, x + w + margin), min(H, y + h + margin)
        crop, m = rgb[y0:y1, x0:x1], mask[y0:y1, x0:x1]
        filled = np.array(lama(Image.fromarray(crop), Image.fromarray(m * 255)))[: y1 - y0, : x1 - x0]
        region = out[y0:y1, x0:x1]
        region[m > 0] = filled[m > 0]
    return out


def review_sheet(rgb, mask, clean):
    """Side-by-side: before (mask in red) | after. Small, for eyeballing."""
    before = rgb.copy()
    before[mask > 0] = [255, 0, 0]
    sheet = np.concatenate([before, clean], axis=1)
    img = Image.fromarray(sheet)
    img.thumbnail((1400, 1400))
    return img


def main(only=None):
    CLEAN.mkdir(exist_ok=True)
    MASKS.mkdir(exist_ok=True)
    sources = {s["path"]: s for s in json.loads((WORK / "sources.json").read_text())}
    ocr = json.loads((WORK / "ocr.json").read_text())
    captions_path = WORK / "captions.json"
    captions = json.loads(captions_path.read_text()) if captions_path.exists() else {}
    lama = SimpleLama(device=torch.device("mps"))
    for k, item in enumerate(ocr):
        src = sources[item["file"]]
        if only and src["id"] not in only:
            continue
        img = ImageOps.exif_transpose(Image.open(item["file"])).convert("RGB")
        if img.size != (item["width"], item["height"]):
            print("size mismatch", src["id"], img.size, file=sys.stderr)
        rgb = np.array(img)
        mask, kept = caption_mask(rgb, item["lines"]) if src["id"] not in KEEP_TEXT else (np.zeros(rgb.shape[:2], np.uint8), [])
        clean = inpaint(lama, rgb, mask) if kept else rgb
        Image.fromarray(clean).save(CLEAN / f"{src['id']}.jpg", quality=95)
        review_sheet(rgb, mask, clean).save(MASKS / f"{src['id']}.jpg", quality=80)
        captions[src["id"]] = {
            "caption": " ".join(l["text"] for l in kept),
            "otherText": [l["text"] for l in item["lines"] if l not in kept],
        }
        print(f"{k + 1}/{len(ocr)} {src['id']} lines={len(kept)}", file=sys.stderr)
    captions_path.write_text(json.dumps(captions, indent=1))


if __name__ == "__main__":
    main(set(sys.argv[1:]) or None)
