"""Live strip: one dot per deployed site with response time. A site that is down is drawn red, never an error."""
import time

import requests

from common import GREEN, RED, card, esc, now_utc

SITES = [("Byline", "byline-res.vercel.app"), ("Codec Git", "codecgit.vercel.app"), ("Prepwise", "prepwise-mocha.vercel.app"), ("Portfolio", "suyashvjain.web.app")]


def check(host):
    """Return (up, text). Up means it answered with anything below 500."""
    t = time.monotonic()
    try:
        r = requests.get(f"https://{host}", timeout=8, headers={"User-Agent": "profile-readme-status"})
        ms = round((time.monotonic() - t) * 1000)
        return r.status_code < 500, f"{ms} ms" if r.status_code < 500 else f"HTTP {r.status_code}"
    except requests.RequestException:
        return False, "down"


def build():
    """Return (wide_svg, mobile_svg)."""
    res = [(n, *check(h)) for n, h in SITES]
    stamp = now_utc().strftime("%Y-%m-%d %H:%M UTC")
    label = "Live status: " + ", ".join(f"{n} {'up, ' + t if ok else t}" for n, ok, t in res) + f". Last refreshed {stamp}."

    def item(x, y, n, ok, t):
        return (f'<circle cx="{x}" cy="{y - 5}" r="6" fill="{GREEN if ok else RED}"/>'
                f'<text x="{x + 16}" y="{y}">{esc(n)} <tspan class="d">· {esc(t)}</tspan></text>')

    def foot(x, y):
        return f'<text class="d" x="{x}" y="{y}" text-anchor="end">last refreshed {stamp}</text>'

    wide = card(860, 84, label, "".join(item(28 + i * 208, 34, *r) for i, r in enumerate(res)) + foot(832, 64))
    mobile = card(400, 132, label, "".join(item(24 + (i % 2) * 190, 36 + (i // 2) * 30, *r) for i, r in enumerate(res)) + foot(376, 108))
    return wide, mobile
