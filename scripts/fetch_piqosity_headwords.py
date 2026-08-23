"""Fetch the public Piqosity ISEE headword lists without copying definitions."""

from __future__ import annotations

import html
import json
import re
import time
import urllib.request
from pathlib import Path


SITE_DIR = Path(__file__).resolve().parents[1]
OUTPUT = SITE_DIR / "data" / "piqosity-headwords.json"
USER_AGENT = "Mozilla/5.0 (compatible; Marco-ISEE-List-Builder/1.0)"

LISTS = {
    "Piqosity Middle": [
        f"https://www.piqosity.com/publications/isee-middle-level-vocabulary-list/group-{group}/"
        for group in range(1, 36)
    ],
}

HEADING_PATTERN = re.compile(
    r'<h2\b[^>]*class="[^"]*\bflip-box-heading\b[^"]*"[^>]*>([\s\S]*?)</h2>',
    re.IGNORECASE,
)
TAG_PATTERN = re.compile(r"<[^>]+>")


def clean_heading(value: str) -> str:
    value = TAG_PATTERN.sub(" ", value)
    value = html.unescape(value).replace("\u00a0", " ")
    return re.sub(r"\s+", " ", value).strip()


def fetch(url: str) -> tuple[str, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.geturl(), response.read().decode("utf-8", errors="replace")


records: list[dict[str, object]] = []
for source, urls in LISTS.items():
    for group, url in enumerate(urls, start=1):
        final_url, page = fetch(url)
        words = [clean_heading(match) for match in HEADING_PATTERN.findall(page)]
        words = [word for word in words if word]
        if not 15 <= len(words) <= 45:
            raise RuntimeError(
                f"Unexpected {source} group {group} count: {len(words)} ({final_url})"
            )
        records.extend(
            {
                "word": word,
                "source": source,
                "group": group,
                "url": final_url,
            }
            for word in words
        )
        print(f"{source} group {group}: {len(words)}")
        time.sleep(0.05)

OUTPUT.write_text(
    json.dumps(records, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
    newline="\n",
)

counts = {
    source: sum(1 for record in records if record["source"] == source)
    for source in LISTS
}
print(f"Wrote {len(records)} headword positions to {OUTPUT}")
print(json.dumps(counts, indent=2))
