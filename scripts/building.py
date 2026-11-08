"""'Currently building': most recently pushed public, non-fork, non-empty repo and its latest commit."""
import datetime as dt

from common import DIM, EME, IND, SKY, TXT, USER, ago, esc, refreshed_line, session, svg


def build():
    s = session()
    r = s.get(f"https://api.github.com/users/{USER}/repos", params={"sort": "pushed", "per_page": 30, "type": "owner"}, timeout=20)
    r.raise_for_status()
    # Skip forks, private, empty, and this profile repo (the refresh bot's own commits would always win).
    repos = [x for x in r.json() if not x["fork"] and not x["private"] and x["size"] > 0 and x["name"].lower() != USER.lower()]
    if not repos:
        raise RuntimeError("no eligible repo")
    repo = repos[0]
    c = s.get(f"https://api.github.com/repos/{USER}/{repo['name']}/commits", params={"per_page": 1}, timeout=20)
    c.raise_for_status()
    commit = c.json()[0]
    msg = commit["commit"]["message"].splitlines()[0]
    msg = msg if len(msg) <= 46 else msg[:45] + "…"
    when = dt.datetime.fromisoformat(repo["pushed_at"].replace("Z", "+00:00"))
    h = 232
    body = f"""<text class="p" x="32" y="76"><tspan fill="{IND}">$</tspan> git -C {esc(repo['name'])} log -1</text>
  <g class="row" style="animation-delay:.3s"><text class="k" x="32" y="118">repo</text><text class="v" x="150" y="118" fill="{SKY}">{esc(USER)}/{esc(repo['name'])}</text></g>
  <g class="row" style="animation-delay:.5s"><text class="k" x="32" y="150">commit</text><text class="v" x="150" y="150" fill="{TXT}">{esc(msg)}</text></g>
  <g class="row" style="animation-delay:.7s"><text class="k" x="32" y="182">pushed</text><text class="v" x="150" y="182" fill="{EME}">{ago(when)}</text></g>
  {refreshed_line(216, h)}"""
    css = """.p { font-size: 22px; fill: #c9d1d9; } .k { font-size: 20px; font-weight: 700; fill: #38bdf8; } .v { font-size: 20px; }
    .row { animation: in .5s ease-out both; }"""
    return svg(h, f"Currently building {repo['name']}: {msg}, pushed {ago(when)}", css, body, "suyash@github: ~/building")
