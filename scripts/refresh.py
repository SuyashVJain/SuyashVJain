"""Generate the live strip into assets/. A failure keeps the previous files."""
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(__file__))
import live  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")

try:
    wide, mobile = live.build()
except Exception:  # noqa: BLE001
    print("[fail] live strip", file=sys.stderr)
    traceback.print_exc()
    sys.exit(0)  # never fail the workflow

for name, content in (("live.svg", wide), ("live-mobile.svg", mobile)):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"[ok] {name}")
