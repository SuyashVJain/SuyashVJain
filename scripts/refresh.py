"""Generate every live SVG into assets/. One failing card never blocks the others (its old file is kept)."""
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(__file__))
import building  # noqa: E402
import heatmap  # noqa: E402
import stats  # noqa: E402
import status  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")


def write(name, make):
    try:
        content = make()
    except Exception:  # noqa: BLE001
        print(f"[fail] {name}", file=sys.stderr)
        traceback.print_exc()
        return
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"[ok] {name}")


days = None
try:
    days = heatmap.fetch_days()
except Exception:  # noqa: BLE001
    print("[fail] contributions fetch", file=sys.stderr)
    traceback.print_exc()

if days:
    write("heatmap.svg", lambda: heatmap.build(days))
write("building.svg", building.build)
write("status.svg", status.build)
write("stats.svg", lambda: stats.build(days))
