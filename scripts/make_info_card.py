"""Hand-authored neofetch-style info card. Edit scripts/config.py, then run this.
STATIC=1 python scripts/make_info_card.py  -> frozen frame (no animation) for previews."""
import os as _os, sys as _sys
_os.chdir(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))   # always run from repo root
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import os
from xml.sax.saxutils import escape
from config import USERNAME, HOST, INFO

STATIC = os.environ.get("STATIC") == "1"
W, H = 640, 490
BG, BAR, FG, DIM = "#0d1117", "#161b22", "#c9d1d9", "#8b949e"
KEY, ACC, GREEN = "#58a6ff", "#d2a8ff", "#39d353"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
PALETTE = ["#ff7b72", "#ffa657", "#e3b341", "#39d353", "#58a6ff", "#d2a8ff", "#c9d1d9", "#6e7681"]

lines = []   # (svg_fragment_factory(y), )

def anim(i):
    if STATIC:
        return ""
    return f' style="opacity:0;animation:in .45s ease-out {0.35 + i*0.14:.2f}s forwards"'

def main():
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
           "<style>@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}"
           f"text{{font-family:{FONT};font-size:17px}}</style>",
           f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>',
           f'<path d="M0 10a10 10 0 0 1 10-10h{W-20}a10 10 0 0 1 10 10v26H0z" fill="{BAR}"/>',
           '<circle cx="22" cy="18" r="6" fill="#ff5f56"/><circle cx="42" cy="18" r="6" fill="#ffbd2e"/><circle cx="62" cy="18" r="6" fill="#27c93f"/>',
           f'<text x="{W/2}" y="23" text-anchor="middle" fill="{DIM}" style="font-size:13px">{escape(HOST)}: ~</text>']
    i, y = 0, 78
    out.append(f'<text x="28" y="{y}" fill="{GREEN}"{anim(i)}>{escape(HOST)}</text>'); i += 1; y += 22
    out.append(f'<text x="28" y="{y}" fill="{DIM}"{anim(i)}>{"─" * (len(HOST))}</text>'); i += 1; y += 38
    for k, v in INFO:
        out.append(f'<text x="28" y="{y}"{anim(i)}><tspan fill="{KEY}" font-weight="bold">{escape(k)}</tspan>'
                   f'<tspan fill="{DIM}">: </tspan><tspan fill="{FG}">{escape(v)}</tspan></text>')
        i += 1; y += 36
    y += 6
    for row in range(2):                      # color swatches, like neofetch
        for n in range(8):
            out.append(f'<rect x="{28 + n*34}" y="{y + row*18}" width="30" height="14" rx="3" fill="{PALETTE[n]}"{anim(i)}/>')
        i += 1
    out.append("</svg>")
    open("info-card.svg", "w", encoding="utf-8").write("\n".join(out))
    print("wrote info-card.svg")

if __name__ == "__main__":
    main()
