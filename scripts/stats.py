"""Stats strip. Items that cannot be computed are left out, never guessed."""
from collections import Counter

from common import EME, IND, SKY, TXT, USER, esc, refreshed_line, session, svg


def build(days=None):
    items = []  # (value, label)
    if days:
        from heatmap import longest_streak

        items.append((str(sum(c for _, _, c in days)), "contributions, last year"))
        best = longest_streak(days)
        if best >= 3:
            items.append((f"{best} days", "longest streak"))
    langs_item = None
    try:
        r = session().get(f"https://api.github.com/users/{USER}/repos", params={"per_page": 100, "type": "owner"}, timeout=20)
        r.raise_for_status()
        langs = Counter(x["language"] for x in r.json() if not x["fork"] and not x["private"] and x["language"])
        top = [name for name, _ in langs.most_common(3)]
        if top:
            langs_item = (" · ".join(top), "top languages by repo")
    except Exception as exc:  # noqa: BLE001
        print(f"stats: languages unavailable: {exc}")
    if not items and not langs_item:
        raise RuntimeError("nothing computable")

    cols = [SKY, IND, EME]
    cells = ""
    n = len(items)
    colw = (860 - 64) / max(n, 1)
    for i, (v, lab) in enumerate(items):
        x = 32 + i * colw
        cells += (
            f'<g class="row" style="animation-delay:{0.3 + i * 0.2:.1f}s">'
            f'<text class="big" x="{x:.0f}" y="116" fill="{cols[i % 3]}">{esc(v)}</text>'
            f'<text class="lab" x="{x:.0f}" y="144">{esc(lab)}</text></g>'
        )
    h = 174
    if langs_item:
        cells += (
            f'<g class="row" style="animation-delay:{0.3 + n * 0.2:.1f}s">'
            f'<text class="lab" x="32" y="182" fill="{TXT}">{esc(langs_item[1])}:</text>'
            f'<text class="lab" x="270" y="182" fill="{SKY}">{esc(langs_item[0])}</text></g>'
        )
        h = 236
    body = f"""<text class="p" x="32" y="76"><tspan fill="{IND}">$</tspan> ./stats.sh</text>
  {cells}
  {refreshed_line(h - 14, h)}"""
    css = """.p { font-size: 22px; fill: #c9d1d9; } .big { font-size: 34px; font-weight: 700; } .lab { font-size: 19px; fill: #8b98a5; }
    .row { animation: in .5s ease-out both; }"""
    return svg(h, "GitHub stats: " + ", ".join(f"{v} {lab}" for v, lab in items), css, body, "suyash@github: ~/stats")
