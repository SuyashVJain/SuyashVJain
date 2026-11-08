"""Shared helpers: terminal-window SVG frame, GitHub API session, relative time."""
import datetime as dt
import html
import os

import requests

USER = os.environ.get("GH_USER", "SuyashVJain")
MONO = 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace'
BG, SKY, IND, EME, TXT, DIM, RED = "#0b0f14", "#38bdf8", "#818cf8", "#34d399", "#c9d1d9", "#6b7785", "#f87171"

esc = html.escape


def now_utc():
    return dt.datetime.now(dt.timezone.utc)


def refreshed_line(x, y):
    stamp = now_utc().strftime("%Y-%m-%d %H:%M UTC")
    return f'<text class="ft" x="{x}" y="{y}" text-anchor="end">last refreshed {stamp}</text>'


def svg(w, h, label, css, body, title, bar=32):
    """Opaque dark terminal card. The animation default is the final state; keyframes only define `from`."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">
  <style>
    text {{ font-family: {MONO}; }}
    .t {{ font-size: 14px; fill: {DIM}; }}
    .ft {{ font-size: 14px; fill: {DIM}; }}
    @keyframes in {{ from {{ opacity: 0; transform: translateY(12px); }} }}
    {css}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
  </style>
  <rect width="{w}" height="{h}" rx="12" fill="{BG}"/>
  <path d="M0 {bar}V12a12 12 0 0 1 12-12h{w - 24}a12 12 0 0 1 12 12V{bar}z" fill="#111821"/>
  <circle cx="20" cy="{bar / 2}" r="5" fill="{RED}" fill-opacity=".85"/><circle cx="38" cy="{bar / 2}" r="5" fill="#fbbf24" fill-opacity=".85"/><circle cx="56" cy="{bar / 2}" r="5" fill="{EME}" fill-opacity=".85"/>
  <text class="t" x="{w / 2}" y="{bar / 2 + 5}" text-anchor="middle">{esc(title)}</text>
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12" fill="none" stroke="#fff" stroke-opacity=".08"/>
  {body}
</svg>
"""


def session():
    s = requests.Session()
    s.headers["User-Agent"] = "profile-readme-refresh"
    s.headers["Accept"] = "application/vnd.github+json"
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        s.headers["Authorization"] = f"Bearer {tok}"
    return s


def parse_time(iso):
    return dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))


def ago(then):
    s = int((now_utc() - then).total_seconds())
    for unit, n in (("d", 86400), ("h", 3600), ("m", 60)):
        if s >= n:
            return f"{s // n}{unit} ago"
    return "just now"
