"""Live strip: site status dots plus what's being built. Never raises because a site is down."""
import datetime as dt

import requests

from common import EME, RED, SKY, TXT, USER, ago, esc, now_utc, parse_time, refreshed_line, session, svg

SITES = [("Byline", "byline-res.vercel.app"), ("Codec Git", "codecgit.vercel.app"), ("Prepwise", "prepwise-mocha.vercel.app"), ("portfolio", "suyashvjain.web.app")]
# Event portals and this profile repo (the refresh bot's own commits would always win) never count as "building".
EXCLUDE = {"shortfilm_hult", "brandlab", "buildscape", "exit-denied", USER.lower()}
FALLBACK = ["byline", "codecgit", "Roll_Call", "inboxiq"]
FRESH_DAYS = 14


def site_up(host):
    try:
        return requests.get(f"https://{host}", timeout=8, headers={"User-Agent": "profile-readme-status"}).status_code < 500
    except requests.RequestException:
        return False


def building():
    """Return ('building'|'last commit', repo, relative time) or None if nothing can be determined."""
    s = session()
    try:
        r = s.get(f"https://api.github.com/users/{USER}/repos", params={"sort": "pushed", "per_page": 30, "type": "owner"}, timeout=20)
        r.raise_for_status()
        cutoff = now_utc() - dt.timedelta(days=FRESH_DAYS)
        for x in r.json():
            if x["fork"] or x["private"] or x["size"] == 0 or x["name"].lower() in EXCLUDE:
                continue
            when = parse_time(x["pushed_at"])
            if when >= cutoff:
                return "building", x["name"], ago(when)
            break  # sorted by push time: nothing newer is left
    except Exception as exc:  # noqa: BLE001
        print(f"live: repo list unavailable: {exc}")
    latest = None
    for name in FALLBACK:
        try:
            c = s.get(f"https://api.github.com/repos/{USER}/{name}/commits", params={"per_page": 1}, timeout=20)
            c.raise_for_status()
            when = parse_time(c.json()[0]["commit"]["committer"]["date"])
            if latest is None or when > latest[0]:
                latest = (when, name)
        except Exception as exc:  # noqa: BLE001
            print(f"live: {name} commit unavailable: {exc}")
    return ("last commit", latest[1], ago(latest[0])) if latest else None


def build():
    """Return (wide_svg, mobile_svg)."""
    status = [(n, site_up(h)) for n, h in SITES]
    info = building()
    css = ".v { font-size: 15px; } .row { animation: in .5s ease-out both; }"
    up = sum(ok for _, ok in status)
    label = f"Live: {up} of {len(status)} sites up" + (f". {info[0]}: {info[1]}, {info[2]}" if info else "")

    def line(info):
        k, repo, t = info
        return (f'<tspan fill="{SKY}">{k}:</tspan> <tspan fill="{TXT}">{esc(repo)}</tspan> <tspan fill="{EME}">· {esc(t)}</tspan>')

    # wide: one row of dots, one row for building
    dots = "".join(
        f'<g class="row" style="animation-delay:{0.2 + i * 0.15:.2f}s"><circle cx="{32 + i * 205}" cy="56" r="6" fill="{EME if ok else RED}"/>'
        f'<text class="v" x="{46 + i * 205}" y="61" fill="{TXT}">{esc(n)}</text></g>'
        for i, (n, ok) in enumerate(status)
    )
    bl = f'<g class="row" style="animation-delay:.9s"><text class="v" x="32" y="92">{line(info)}</text></g>' if info else ""
    hw = 124 if info else 96
    wide = svg(860, hw, label, css, f"{dots}{bl}{refreshed_line(836, hw - 10)}", "suyash@github: ~/live")

    # mobile: 2x2 dots, building line wrapped to the card width
    dots = "".join(
        f'<g class="row" style="animation-delay:{0.2 + i * 0.15:.2f}s"><circle cx="{24 + (i % 2) * 180}" cy="{56 + (i // 2) * 28}" r="6" fill="{EME if ok else RED}"/>'
        f'<text class="v" x="{38 + (i % 2) * 180}" y="{61 + (i // 2) * 28}" fill="{TXT}">{esc(n)}</text></g>'
        for i, (n, ok) in enumerate(status)
    )
    bl = f'<g class="row" style="animation-delay:.9s"><text class="v" x="24" y="132">{line(info)}</text></g>' if info else ""
    hm = 168 if info else 130
    mobile = svg(400, hm, label, css, f"{dots}{bl}{refreshed_line(376, hm - 12)}", "suyash@github: ~/live")
    return wide, mobile
