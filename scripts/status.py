"""Live site status. Never raises: a site that is down is simply drawn red."""
import time

import requests

from common import DIM, EME, IND, RED, TXT, esc, refreshed_line, svg

SITES = ["byline-res.vercel.app", "codecgit.vercel.app", "prepwise-mocha.vercel.app", "suyashvjain.web.app", "brandlab-ieee.vercel.app"]


def check(host):
    t = time.monotonic()
    try:
        r = requests.get(f"https://{host}", timeout=8, headers={"User-Agent": "profile-readme-status"})
        ms = round((time.monotonic() - t) * 1000)
        return (r.status_code < 500), f"HTTP {r.status_code}  {ms} ms"
    except requests.RequestException:
        return False, "no response"


def build():
    rows, y = "", 118
    results = []
    for i, host in enumerate(SITES):
        ok, text = check(host)
        results.append((host, ok))
        col = EME if ok else RED
        rows += (
            f'<g class="row" style="animation-delay:{0.3 + i * 0.2:.1f}s">'
            f'<circle cx="40" cy="{y - 7}" r="7" fill="{col}"/>'
            f'<text class="v" x="62" y="{y}" fill="{TXT}">{esc(host)}</text>'
            f'<text class="v" x="{860 - 32}" y="{y}" text-anchor="end" fill="{col}">{esc(text)}</text></g>'
        )
        y += 34
    h = y + 40
    up = sum(ok for _, ok in results)
    body = f"""<text class="p" x="32" y="76"><tspan fill="{IND}">$</tspan> ./status.sh</text>
  {rows}
  {refreshed_line(h - 18, h)}"""
    css = ".p { font-size: 22px; fill: #c9d1d9; } .v { font-size: 19px; } .row { animation: in .5s ease-out both; }"
    return svg(h, f"Site status: {up} of {len(SITES)} sites up", css, body, "suyash@github: ~/status")
