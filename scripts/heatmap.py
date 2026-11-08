"""Contribution heatmap from GitHub's public contributions endpoint (no token needed)."""
import datetime as dt
import re

import requests
from bs4 import BeautifulSoup

from common import BAR, DIM, IND, W, USER, esc, refreshed_line, svg  # noqa: F401

PAD = 24
COLS = 53
PITCH = (W - 2 * PAD) / COLS
CELL = PITCH - 2.8
GRID_Y = 112
LEVELS = ["#151b23", "#134e6a", "#1d8fc0", "#38bdf8", "#34d399"]


def fetch_days():
    """Return [(date, level 0-4, count)] sorted by date."""
    r = requests.get(
        f"https://github.com/users/{USER}/contributions",
        headers={"User-Agent": "Mozilla/5.0 (profile-heatmap)"},
        timeout=30,
    )
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    counts = {}
    for tip in soup.find_all("tool-tip"):
        m = re.match(r"(\d+|No) contributions?", tip.get_text(strip=True))
        if m:
            counts[tip.get("for")] = 0 if m.group(1) == "No" else int(m.group(1))
    days = [
        (dt.date.fromisoformat(td["data-date"]), int(td["data-level"]), counts.get(td.get("id"), 0))
        for td in soup.select("td.ContributionCalendar-day[data-date]")
    ]
    if not days:
        raise RuntimeError("no contribution cells found; GitHub markup may have changed")
    return sorted(days)


def streak(days):
    """Consecutive days with contributions, ending today (or yesterday if today has none yet)."""
    n, rest = 0, list(reversed(days))
    if rest and rest[0][2] == 0:
        rest = rest[1:]
    for _, _, c in rest:
        if c == 0:
            break
        n += 1
    return n


def longest_streak(days):
    """Longest run of consecutive days with contributions in the fetched year."""
    best = cur = 0
    for _, _, c in days:
        cur = cur + 1 if c > 0 else 0
        best = max(best, cur)
    return best


def build(days):
    offset = (days[0][0].weekday() + 1) % 7  # GitHub weeks start on Sunday
    total = sum(c for _, _, c in days)
    rects, months, seen = [], [], set()
    for i, (d, lvl, cnt) in enumerate(days):
        col, row = divmod(i + offset, 7)
        if col >= COLS:
            continue
        x, y = PAD + col * PITCH, GRID_Y + row * PITCH
        rects.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{CELL:.1f}" height="{CELL:.1f}" rx="3" fill="{LEVELS[lvl]}" '
            f'style="animation-delay:{(col + row) * 0.014:.2f}s"><title>{cnt} on {d.isoformat()}</title></rect>'
        )
        if d.day <= 7 and row == 0 and (d.year, d.month) not in seen and col < COLS - 2:
            seen.add((d.year, d.month))
            months.append(f'<text x="{x:.1f}" y="102" class="m">{d.strftime("%b")}</text>')
    lx = W - PAD - 5 * 22 - 90
    legend = "".join(f'<rect x="{lx + 44 + i * 22}" y="238" width="16" height="16" rx="3" fill="{c}"/>' for i, c in enumerate(LEVELS))
    h = 304
    body = f"""<text class="p" x="{PAD}" y="66"><tspan fill="{IND}">$</tspan> ./contributions --last-year</text>
  {''.join(months)}
  <g class="g">{''.join(rects)}</g>
  <text class="l" x="{PAD}" y="252">{total} contributions in the last year</text>
  <text class="l" x="{lx}" y="252">Less</text>{legend}<text class="l" x="{lx + 44 + 5 * 22 + 4}" y="252">More</text>
  {refreshed_line(288, h)}"""
    css = """.p { font-size: 22px; fill: #c9d1d9; } .m, .l { font-size: 15px; fill: #8b98a5; }
    .g rect { animation: slide 0.7s ease-out both; }
    @keyframes slide { from { opacity: 0; transform: translate(-14px, -14px); } }"""
    return svg(h, f"{total} GitHub contributions in the last year", css, body, "suyash@github: ~/contributions")
