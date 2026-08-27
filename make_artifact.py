#!/usr/bin/env python3
"""Turn an article page into an artifact-ready fragment.

The Artifact publisher supplies its own <!doctype>/<html>/<head>/<body> wrapper
and blocks external stylesheets, so this script:

  1. strips the wrapper tags,
  2. inlines assets/style.css,
  3. rewrites "../index.html" links (they do not resolve inside an artifact),
  4. keeps the <title> so the artifact is named correctly.

Usage:
    python3 make_artifact.py articles/2026-08-31.html /path/to/output.html
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STYLE = ROOT / "assets" / "style.css"


COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def convert(article: Path) -> str:
    # Strip comments first so a commented-out example tag cannot match
    # ahead of the real one.
    text = COMMENT.sub("", article.read_text(encoding="utf-8"))

    title_match = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    title = title_match.group(1).strip() if title_match else article.stem

    body_match = re.search(r"<body[^>]*>(.*)</body>", text, re.I | re.S)
    if not body_match:
        raise SystemExit(f"No <body> found in {article}")
    body = body_match.group(1)

    # The back-link has nowhere to go inside an artifact; drop the anchor,
    # keeping its label as plain text.
    body = re.sub(
        r'<a class="site-name"[^>]*>(.*?)</a>',
        r'<span class="site-name">\1</span>',
        body,
        flags=re.I | re.S,
    )
    body = re.sub(
        r'<a href="\.\./index\.html"[^>]*>.*?</a>',
        "Published from the daily-trend archive.",
        body,
        flags=re.I | re.S,
    )

    css = STYLE.read_text(encoding="utf-8") if STYLE.exists() else ""

    return f"<title>{title}</title>\n<style>\n{css}\n</style>\n{body.strip()}\n"


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 1
    source, dest = Path(argv[1]), Path(argv[2])
    if not source.is_absolute():
        source = ROOT / source
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(convert(source), encoding="utf-8")
    print(f"Wrote artifact-ready file: {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
