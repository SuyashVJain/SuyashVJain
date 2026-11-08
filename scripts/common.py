"""Shared helpers for the live strip."""
import datetime as dt
import html

esc = html.escape
SANS = '-apple-system, "Segoe UI", Helvetica, Arial, sans-serif'
BG, BORDER, TXT, DIM, GREEN, RED = "#0d1117", "#30363d", "#e6edf3", "#8b98a5", "#3fb950", "#f85149"


def now_utc():
    return dt.datetime.now(dt.timezone.utc)


def card(w, h, label, body):
    """Static dark card: opaque so it reads on both GitHub themes."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">
  <style>text {{ font-family: {SANS}; font-size: 15px; fill: {TXT}; }} .d {{ fill: {DIM}; }}</style>
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  {body}
</svg>
"""
