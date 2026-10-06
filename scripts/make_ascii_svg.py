"""Convert source-prepped.png + source-mask.png into a self-typing monochrome ASCII SVG.

THEME = "paper"    -> dark ink on a light card, dark areas = dense glyphs (most faithful for faces)
THEME = "terminal" -> light ink on a dark card, bright areas = dense glyphs
"""
import os as _os, sys as _sys
_os.chdir(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))   # always run from repo root
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import cv2
import numpy as np
from xml.sax.saxutils import escape

THEME = "paper"
COLS = 100
CHAR_W, LINE_H, FONT = 6.0, 10.0, 10
RAMP = " .`:-=+*cs#%@"      # sparse -> dense
GAMMA = 0.9
ROW_DELAY, ROW_DUR = 0.045, 0.55
THEMES = {
    "paper":    dict(bg="#f6f8fa", fg="#24292f", cursor="#2da44e", invert=True),
    "terminal": dict(bg="#0d1117", fg="#c9d1d9", cursor="#39d353", invert=False),
}
T = THEMES[THEME]

def build_rows():
    g = cv2.imread("source-prepped.png", 0)
    m = cv2.imread("source-mask.png", 0)
    h, w = g.shape
    rows = max(1, int(round(COLS * h / w * (CHAR_W / LINE_H))))
    g = cv2.resize(g, (COLS, rows), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    m = cv2.resize(m, (COLS, rows), interpolation=cv2.INTER_AREA)
    inside = g[m > 110]
    lo, hi = np.percentile(inside, 3), np.percentile(inside, 97)      # stretch tones inside the subject
    g = np.clip((g - lo) / max(hi - lo, 1e-3), 0, 1)
    blur = cv2.GaussianBlur(g, (0, 0), 1.2)
    g = np.clip(g + 0.9 * (g - blur), 0, 1)                           # unsharp: crisper eyes/mouth/hair
    out = []
    for y in range(rows):
        line = ""
        for x in range(COLS):
            if m[y, x] < 110:
                line += " "                                           # background prints nothing
                continue
            v = (1 - g[y, x]) if T["invert"] else g[y, x]
            line += RAMP[int((v ** GAMMA) * (len(RAMP) - 1))]
        out.append(line.rstrip())
    return out

def main():
    rows = build_rows()
    pad = 10
    W = COLS * CHAR_W + pad * 2
    H = len(rows) * LINE_H + pad * 2
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}">',
         f'<rect width="100%" height="100%" rx="10" fill="{T["bg"]}"/>', "<defs>"]
    for i in range(len(rows)):
        t = i * ROW_DELAY
        p.append(f'<clipPath id="c{i}"><rect x="{pad}" y="{pad + i*LINE_H:.1f}" width="0" height="{LINE_H}">'
                 f'<animate attributeName="width" from="0" to="{COLS*CHAR_W:.0f}" begin="{t:.3f}s" dur="{ROW_DUR}s" fill="freeze"/>'
                 f'</rect></clipPath>')
    p.append("</defs>")
    for i, line in enumerate(rows):
        if not line.strip():
            continue
        y = pad + i * LINE_H
        t = i * ROW_DELAY
        p.append(f'<text x="{pad}" y="{y + LINE_H*0.8:.1f}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" '
                 f'font-size="{FONT}" fill="{T["fg"]}" xml:space="preserve" clip-path="url(#c{i})" '
                 f'textLength="{len(line)*CHAR_W:.0f}" lengthAdjust="spacing">{escape(line)}</text>')
        # small block cursor riding the wipe edge, then disappearing
        p.append(f'<rect x="{pad}" y="{y + 1:.1f}" width="{CHAR_W}" height="{LINE_H-2}" fill="{T["cursor"]}" opacity="0">'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.01;0.98;1" begin="{t:.3f}s" dur="{ROW_DUR}s" fill="freeze"/>'
                 f'<animate attributeName="x" from="{pad}" to="{pad + COLS*CHAR_W - CHAR_W:.0f}" begin="{t:.3f}s" dur="{ROW_DUR}s" fill="freeze"/></rect>')
    p.append("</svg>")
    open("avi-ascii.svg", "w", encoding="utf-8").write("\n".join(p))
    print(f"wrote avi-ascii.svg ({len(rows)} rows x {COLS} cols)")

if __name__ == "__main__":
    main()
