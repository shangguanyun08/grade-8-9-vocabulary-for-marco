"""Validate the published expanded vocabulary dataset."""

from __future__ import annotations

import json
from pathlib import Path


SITE_DIR = Path(__file__).resolve().parents[1]


def load(name: str):
    return json.loads((SITE_DIR / name).read_text(encoding="utf-8"))


words = load("words.json")
original = load("data/zozeck-original-words.json")
piqosity = load("data/piqosity-headwords.json")
tested = load("data/isee-test-headwords.json")

assert len(words) == len({item["id"] for item in words}), "Duplicate IDs"
assert [item["rank"] for item in words] == list(range(1, len(words) + 1)), "Broken ranks"
assert all(item["word"] and item["meaning"] for item in words), "Blank word or meaning"
assert all(item["sources"] and item["studyBand"] for item in words), "Missing source metadata"

by_id = {item["id"]: item for item in words}
for item in original:
    expanded = by_id[item["id"]]
    assert expanded["meaning"] == item["meaning"], f"Original meaning changed: {item['id']}"
    assert "Zozeck Grade 8–9" in expanded["sources"]

for item in piqosity:
    source_id = item["word"].casefold().replace("plebian", "plebeian")
    source_id = source_id.replace("‐", "-").replace("‑", "-").replace("–", "-").replace("—", "-")
    assert source_id in by_id, f"Missing Piqosity headword: {item['word']}"
    assert item["source"] in by_id[source_id]["sources"]

assert len(tested) == 148
for item in tested:
    assert item["word"] in by_id, f"Missing tested family: {item['word']}"
    assert "ISEE Test Samples" in by_id[item["word"]]["sources"]

print(f"Validated {len(words):,} unique entries.")
print(f"Preserved {len(original):,} original entries.")
print(f"Included {len(tested)} tested word families and all Piqosity headwords.")
