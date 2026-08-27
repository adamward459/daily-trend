# Daily Trend

Weekly briefs on AI and web development, filtered for the MERN / React Native stack.

Generated automatically by a scheduled Claude task every **Monday at ~7am**.

## Layout

```
index.html                  generated archive page — links to every brief
articles/YYYY-MM-DD.html    one brief per week
assets/style.css            shared styles for every page
templates/article-template.html   structure a new brief copies
build_index.py              regenerates index.html from articles/
make_artifact.py            converts a brief into an artifact-ready fragment
```

## What each run does

1. Researches the past week across HN, Reddit, GitHub trending, engineering
   blogs, X discussion (via search, not scraping), tech press and arXiv.
2. Writes `articles/YYYY-MM-DD.html` from the template.
3. Runs `python3 build_index.py` to refresh the archive listing.
4. Commits everything to git.

## Rebuilding by hand

```bash
python3 build_index.py
```

Open `index.html` in a browser to read the archive locally.

## Hosting

Set up for GitHub Pages: `index.html` sits at the repo root, so enabling Pages
on the `main` branch (root folder) serves the archive directly.
