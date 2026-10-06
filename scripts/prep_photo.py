"""Prep a photo for ASCII conversion: isolate subject, boost contrast.
Usage: python scripts/prep_photo.py source-photo.jpg
Outputs: source-prepped.png (grayscale) and source-mask.png (subject mask)."""
import os as _os, sys as _sys
_os.chdir(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))   # always run from repo root
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import sys
import cv2
import numpy as np

# Crop box (fractions of width/height): head + upper chest.
CROP = (0.27, 0.15, 0.71, 0.41)   # x0, y0, x1, y1  (head + shoulders)

def get_mask(img):
    try:                                   # best quality if rembg is installed
        from rembg import remove
        out = remove(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        return (out[..., 3] > 128).astype(np.uint8) * 255
    except Exception:
        pass
    h, w = img.shape[:2]                   # fallback: OpenCV GrabCut with hints
    sx, sy = w / 533.0, h / 800.0          # hints authored on a 533x800 portrait
    def R(x0, y0, x1, y1): return (int(x0*sx), int(y0*sy), int(x1*sx), int(y1*sy))
    mask = np.full((h, w), cv2.GC_PR_BGD, np.uint8)
    def fill(box, v):
        a, b, c, d = R(*box); mask[b:d, a:c] = v
    fill((100, 120, 470, 700), cv2.GC_PR_FGD)        # person-ish region
    fill((215, 150, 305, 285), cv2.GC_FGD)           # face
    cv2.ellipse(mask, (int(262*sx), int(185*sy)), (int(50*sx), int(55*sy)), 0, 0, 360, int(cv2.GC_FGD), -1)  # head + hair
    fill((150, 330, 410, 560), cv2.GC_FGD)           # shirt core
    fill((0, 0, 100, 800), cv2.GC_BGD)               # left background
    fill((470, 0, 533, 800), cv2.GC_BGD)             # right background
    fill((0, 0, 533, 125), cv2.GC_BGD)               # above hair
    fill((335, 0, 470, 285), cv2.GC_BGD)             # brick pillar right of head
    fill((100, 120, 200, 290), cv2.GC_BGD)           # sky left of head
    bg, fg = np.zeros((1, 65)), np.zeros((1, 65))
    cv2.grabCut(img, mask, None, bg, fg, 10, cv2.GC_INIT_WITH_MASK)
    m = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m)
    if n > 1:                              # keep the biggest blob only
        m = np.where(lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA]), 255, 0).astype(np.uint8)
    return cv2.GaussianBlur(m, (5, 5), 0)

def main(path):
    img = cv2.imread(path)
    mask = get_mask(img)
    h, w = img.shape[:2]
    x0, y0, x1, y1 = (int(CROP[0]*w), int(CROP[1]*h), int(CROP[2]*w), int(CROP[3]*h))
    img, mask = img[y0:y1, x0:x1], mask[y0:y1, x0:x1]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8)).apply(gray)
    cv2.imwrite("source-prepped.png", gray)
    cv2.imwrite("source-mask.png", mask)
    print("wrote source-prepped.png + source-mask.png", gray.shape)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg")
