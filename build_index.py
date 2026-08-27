#!/usr/bin/env python3
"""Regenerate index.html from the article pages in articles/.

Scans articles/*.html, reads each page's <title>, <meta name="description">
and <meta name="date">, and writes a listing page sorted newest first.

Usage:
    python3 build_index.py
"""

from __future__ import annotations

import html
import re
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARTICLES = ROOT / "articles"
INDEX = ROOT / "index.html"

SITE_NAME = "Daily Trend"
SITE_URL = "https://adamward459.github.io/daily-trend/"
TAGLINE = "Weekly briefs on AI and web development, filtered for the MERN / React Native stack."

FILENAME_DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def _tag(pattern: str, text: str) -> str | None:
    m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else None


def read_article(path: Path) -> dict:
    """Pull the listing metadata out of one article page."""
    # Comments are stripped first: a commented-out example tag would
    # otherwise match before the real one.
    text = COMMENT.sub("", path.read_text(encoding="utf-8", errors="replace"))

    title = _tag(r"<title[^>]*>(.*?)</title>", text)
    description = _tag(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', text
    )
    iso = _tag(r'<meta\s+name=["\']date["\']\s+content=["\'](.*?)["\']', text)

    if not iso:
        m = FILENAME_DATE.search(path.name)
        iso = m.group(1) if m else None

    try:
        parsed = datetime.strptime(iso, "%Y-%m-%d").date() if iso else None
    except ValueError:
        parsed = None

    if parsed is None:
        # Unparseable date: fall back to file mtime so the entry still lists.
        parsed = date.fromtimestamp(path.stat().st_mtime)

    return {
        "href": f"articles/{path.name}",
        "title": html.unescape(title) if title else path.stem,
        "description": html.unescape(description) if description else "",
        "date": parsed,
    }


def collect() -> list[dict]:
    if not ARTICLES.is_dir():
        return []
    entries = [
        read_article(p)
        for p in ARTICLES.glob("*.html")
        if not p.name.startswith((".", "_"))
    ]
    return sorted(entries, key=lambda e: (e["date"], e["href"]), reverse=True)


def render(entries: list[dict]) -> str:
    if entries:
        items = "\n".join(
            f"""      <li>
        <span class="entry-date">{e['date'].strftime('%B %-d, %Y')}</span>
        <a class="entry-title" href="{html.escape(e['href'])}">{html.escape(e['title'])}</a>
        <p class="entry-summary">{html.escape(e['description'])}</p>
      </li>"""
            for e in entries
        )
        listing = f'    <ul class="archive">\n{items}\n    </ul>'
        count = f"{len(entries)} brief{'s' if len(entries) != 1 else ''}"
    else:
        listing = '    <p class="empty">No briefs published yet.</p>'
        count = "No briefs yet"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(SITE_NAME)}</title>
<meta name="description" content="{html.escape(TAGLINE)}">
<link rel="canonical" href="{html.escape(SITE_URL)}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>\U0001f4e1</text></svg>">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="wrap">

  <header class="masthead">
    <span class="site-name">{html.escape(SITE_NAME)}</span>
    <h1>The archive</h1>
    <p class="dateline">{html.escape(TAGLINE)}</p>
  </header>

{listing}

  <footer class="foot">
    {count} &middot; generated {date.today().strftime('%B %-d, %Y')}
  </footer>

</div>
</body>
</html>
"""


def main() -> int:
    entries = collect()
    INDEX.write_text(render(entries), encoding="utf-8")
    print(f"Wrote {INDEX.relative_to(ROOT)} with {len(entries)} article(s).")
    for e in entries:
        print(f"  {e['date']}  {e['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
