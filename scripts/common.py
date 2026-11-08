"""Shared helpers: terminal-window SVG frame, GitHub API session, timestamps."""
import datetime as dt
import html
import os

import requests

USER = os.environ.get("GH_USER", "SuyashVJain")
W = 860
BAR = 40
MONO = 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace'
BG, SKY, IND, EME, TXT, DIM, RED = "#0b0f14", "#38bdf8", "#818cf8", "#34d399", "#c9d1d9", "#6b7785", "#f87171"

esc = html.escape


def now_utc():
    return dt.datetime.now(dt.timezone.utc)


def refreshed_line(y, h):
    stamp = now_utc().strftime("%Y-%m-%d %H:%M UTC")
    return f'<text class="ft" x="{W - 24}" y="{y}" text-anchor="end">last refreshed {stamp}</text>'


def svg(h, label, css, body, title):
    """Opaque dark terminal card. The animation default is the final state; keyframes only define `from`."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{esc(label)}">
  <style>
    text {{ font-family: {MONO}; }}
    .t {{ font-size: 16px; fill: {DIM}; }}
    .ft {{ font-size: 16px; fill: {DIM}; }}
    @keyframes in {{ from {{ opacity: 0; transform: translateY(14px); }} }}
    {css}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
  </style>
  <rect width="{W}" height="{h}" rx="12" fill="{BG}"/>
  <path d="M0 {BAR}V12a12 12 0 0 1 12-12h{W - 24}a12 12 0 0 1 12 12V{BAR}z" fill="#111821"/>
  <circle cx="24" cy="20" r="6" fill="{RED}" fill-opacity=".85"/><circle cx="46" cy="20" r="6" fill="#fbbf24" fill-opacity=".85"/><circle cx="68" cy="20" r="6" fill="{EME}" fill-opacity=".85"/>
  <text class="t" x="{W / 2}" y="26" text-anchor="middle">{esc(title)}</text>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="12" fill="none" stroke="#fff" stroke-opacity=".08"/>
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


def ago(then):
    s = int((now_utc() - then).total_seconds())
    for unit, n in (("d", 86400), ("h", 3600), ("m", 60)):
        if s >= n:
            return f"{s // n}{unit} ago"
    return "just now"
