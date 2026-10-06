"""data/contributions.json -> contrib-heatmap.svg (53x7 rounded boxes, diagonal reveal)."""
import os as _os, sys as _sys
_os.chdir(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))   # always run from repo root
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import json
from datetime import date

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG, FG, DIM = "#0d1117", "#c9d1d9", "#8b949e"
BOX, GAP = 12, 3.6
PITCH = BOX + GAP
LEFT, TOP = 44, 52
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def level_for(d, maxc):
    """GitHub's own level, with a neon level 5 for the very busiest days."""
    lv = d["level"]
    if lv == 4 and maxc > 0 and d["count"] >= 0.8 * maxc and d["count"] >= 10:
        return 5
    return lv

def main():
    data = json.load(open("data/contributions.json"))
    days, st = data["days"], data["stats"]
    maxc = max(d["count"] for d in days)
    first = date.fromisoformat(days[0]["date"])
    first_sun = first.toordinal() - ((first.weekday() + 1) % 7)
    weeks = (date.fromisoformat(days[-1]["date"]).toordinal() - first_sun) // 7 + 1
    W = LEFT + weeks * PITCH + 20
    H = TOP + 7 * PITCH + 70
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}">',
         "<style>@keyframes pop{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}"
         f".c{{opacity:0;animation:pop .5s ease-out forwards}} text{{font-family:{FONT};fill:{DIM};font-size:11px}}</style>",
         f'<rect width="{W:.0f}" height="{H:.0f}" rx="10" fill="{BG}"/>',
         f'<text x="{LEFT}" y="26" style="fill:{FG};font-size:13px">{st["total"]:,} contributions in the last year</text>']
    last_month = None
    for d in days:
        dt = date.fromisoformat(d["date"])
        wk = (dt.toordinal() - first_sun) // 7
        dow = (dt.weekday() + 1) % 7
        x, y = LEFT + wk * PITCH, TOP + dow * PITCH
        if dow == 0 and dt.month != last_month and (last_month is None or dt.day <= 7):
            o.append(f'<text x="{x:.1f}" y="{TOP-10}">{MONTHS[dt.month-1]}</text>')
            last_month = dt.month
        delay = (wk + dow) * 0.013
        tip = f'{d["count"]} contribution{"s" if d["count"] != 1 else ""} on {d["date"]}'
        o.append(f'<rect class="c" x="{x:.1f}" y="{y:.1f}" width="{BOX}" height="{BOX}" rx="3" '
                 f'fill="{PALETTE[level_for(d, maxc)]}" style="animation-delay:{delay:.2f}s"><title>{tip}</title></rect>')
    for dow, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        o.append(f'<text x="8" y="{TOP + dow*PITCH + 10}">{name}</text>')
    fy = TOP + 7 * PITCH + 22                               # footer: stats + legend
    b = st["best_day"]
    o.append(f'<text x="{LEFT}" y="{fy}">current streak <tspan style="fill:{FG}">{st["current_streak"]}d</tspan>   '
             f'longest <tspan style="fill:{FG}">{st["longest_streak"]}d</tspan>   '
             f'best day <tspan style="fill:{FG}">{b["count"]}</tspan> ({b["date"]})</text>')
    lx = W - 20 - (6 * PITCH + 70)
    o.append(f'<text x="{lx}" y="{fy}">Less</text>')
    for i, c in enumerate(PALETTE):
        o.append(f'<rect x="{lx + 32 + i*PITCH:.1f}" y="{fy-10}" width="{BOX}" height="{BOX}" rx="3" fill="{c}"/>')
    o.append(f'<text x="{lx + 38 + 6*PITCH:.1f}" y="{fy}">More</text>')
    o.append("</svg>")
    open("contrib-heatmap.svg", "w", encoding="utf-8").write("\n".join(o))
    print(f"wrote contrib-heatmap.svg ({weeks} weeks)")

if __name__ == "__main__":
    main()
