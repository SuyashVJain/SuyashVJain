"""Write assets/live.svg and assets/live-mobile.svg. Never fails the workflow."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import live  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")

wide, mobile = live.build()  # check() swallows request errors, so a down site is just drawn red
for name, content in (("live.svg", wide), ("live-mobile.svg", mobile)):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"[ok] {name}")
