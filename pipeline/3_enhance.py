"""Make an AI-enhanced version of each clean photo -> work/enhanced/<id>.jpg

1. LaMa fills in thin bright scratches, cracks and dust specks.
2. Real-ESRGAN x2 restores detail and removes grain / JPEG noise.
3. Contrast is stretched on lightness only, so sepia stays sepia.
Face restoration (GFPGAN) was tried and rejected: it invents a different person.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image
from simple_lama_inpainting import SimpleLama
from spandrel import ModelLoader

HERE = Path(__file__).resolve().parent
WORK, MODELS = HERE / "work", HERE / "models"
DEVICE = torch.device("mps")
TILE = 384
INPUT_EDGE = 1000      # photos are shrunk to this before the x2 upscale

def load(name):
    return ModelLoader(DEVICE).load_from_file(MODELS / name).eval()


def to_tensor(rgb):
    return torch.from_numpy(rgb).permute(2, 0, 1)[None].float().div(255).to(DEVICE)


def upscale(model, rgb):
    """Run the upscaler over overlapping tiles so big photos fit in memory."""
    s, (h, w), pad = model.scale, rgb.shape[:2], 16
    out = np.zeros((h * s, w * s, 3), np.float32)
    for y in range(0, h, TILE):
        for x in range(0, w, TILE):
            y0, x0 = max(0, y - pad), max(0, x - pad)
            y1, x1 = min(h, y + TILE + pad), min(w, x + TILE + pad)
            with torch.inference_mode():
                r = model(to_tensor(rgb[y0:y1, x0:x1]))[0].permute(1, 2, 0).clamp(0, 1).cpu().numpy()
            cy, cx = (y - y0) * s, (x - x0) * s
            th, tw = min(TILE, h - y) * s, min(TILE, w - x) * s
            out[y * s:y * s + th, x * s:x * s + tw] = r[cy:cy + th, cx:cx + tw]
    return (out * 255).round().astype(np.uint8)


def stretch_tone(rgb, low_pct=0.5, high_pct=99.5):
    """Stretch lightness only (LAB L channel), so faded photos gain contrast without colour shifts."""
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    L = lab[..., 0].astype(np.float32)
    lo, hi = np.percentile(L, [low_pct, high_pct])
    if hi - lo < 10:
        return rgb
    lab[..., 0] = np.clip((L - lo) * (255 / (hi - lo)), 0, 255).astype(np.uint8)
    return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)


def damage_mask(rgb):
    """Thin bright marks (scratches, cracks, dust) that stand out from their surroundings."""
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    k = max(9, min(rgb.shape[:2]) // 60) | 1
    tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    mask = (tophat > 40).astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
    keep = np.zeros(n, bool)
    for i in range(1, n):
        w, h, area = stats[i][2], stats[i][3], stats[i][4]
        thin = area < 0.35 * w * h or max(w, h) > 4 * min(w, h)
        keep[i] = area <= 3 or (thin and max(w, h) >= 6)
    mask = keep[labels].astype(np.uint8)
    return cv2.dilate(mask, np.ones((3, 3), np.uint8))


def repair(lama, rgb):
    mask = damage_mask(rgb)
    if not mask.any():
        return rgb
    filled = np.array(lama(Image.fromarray(rgb), Image.fromarray(mask * 255)))[: rgb.shape[0], : rgb.shape[1]]
    out = rgb.copy()
    out[mask > 0] = filled[mask > 0]
    return out


def enhance(models, img):
    upscaler, lama = models
    img = img.copy()
    img.thumbnail((INPUT_EDGE, INPUT_EDGE), Image.LANCZOS)
    rgb = repair(lama, np.array(img))
    return Image.fromarray(stretch_tone(upscale(upscaler, rgb)))


def main(ids):
    out_dir = WORK / "enhanced"
    out_dir.mkdir(exist_ok=True)
    models = (load("RealESRGAN_x2plus.pth"), SimpleLama(device=DEVICE))
    for i, id_ in enumerate(ids):
        img = Image.open(WORK / "clean" / f"{id_}.jpg").convert("RGB")
        enhance(models, img).save(out_dir / f"{id_}.jpg", quality=92)
        print(f"{i + 1}/{len(ids)} {id_}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:] or sorted(p.stem for p in (WORK / "clean").glob("*.jpg")))
