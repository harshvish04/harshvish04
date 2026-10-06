"""Scrape the public contribution calendar (no token needed) -> data/contributions.json"""
import os as _os, sys as _sys
_os.chdir(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))   # always run from repo root
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import json, re, sys, os
from datetime import date, datetime, timezone
import requests
from bs4 import BeautifulSoup

from config import USERNAME

URL = f"https://github.com/users/{USERNAME}/contributions"

def fetch_days():
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    tips = {t.get("for"): t.get_text(" ", strip=True) for t in soup.find_all("tool-tip")}
    days = []
    for td in soup.select("td[data-date]"):
        tip = tips.get(td.get("id"), "")
        m = re.match(r"([\d,]+)\s+contribution", tip)
        count = int(m.group(1).replace(",", "")) if m else 0
        days.append({"date": td["data-date"], "count": count, "level": int(td.get("data-level", 0))})
    days.sort(key=lambda d: d["date"])
    if not days:
        raise SystemExit("No contribution cells found - GitHub markup may have changed.")
    return days

def stats(days):
    total = sum(d["count"] for d in days)
    longest = cur = 0
    for d in days:
        cur = cur + 1 if d["count"] > 0 else 0
        longest = max(longest, cur)
    cs = 0                                   # current streak (today may still be empty)
    for d in reversed(days):
        if d["count"] > 0:
            cs += 1
        elif d is days[-1]:
            continue
        else:
            break
    best = max(days, key=lambda d: d["count"])
    months = {}
    for d in days:
        months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["count"]
    return dict(total=total, current_streak=cs, longest_streak=longest,
                best_day=best, monthly=months)

def main():
    days = fetch_days()
    data = {"username": USERNAME, "generated": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "stats": stats(days), "days": days}
    os.makedirs("data", exist_ok=True)
    json.dump(data, open("data/contributions.json", "w"), indent=1)
    print(f"{len(days)} days, {data['stats']['total']} contributions")

if __name__ == "__main__":
    main()
