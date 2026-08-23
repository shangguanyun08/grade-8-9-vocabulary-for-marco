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
assert all(item["sources"] and item["difficulty"] for item in words), "Missing metadata"
assert all(item["difficultyTier"] in range(1, 6) for item in words), "Broken difficulty tier"

removed_sources = {"Piqosity Upper", "Marco Hard Practice", "Marco Word Mastery", "Zozeck Grade 8–9"}
assert not any(removed_sources & set(item["sources"]) for item in words), "Removed source remains"

by_id = {item["id"]: item for item in words}
for item in original:
    expanded = by_id[item["id"]]
    assert expanded["meaning"] == item["meaning"], f"Original meaning changed: {item['id']}"
    assert "Original Zozeck Entries" in expanded["sources"]

assert sum("Original Zozeck Entries" in item["sources"] for item in words) == 1920

for item in piqosity:
    assert item["source"] == "Piqosity Middle", "Non-Middle Piqosity entry remains"
    source_id = item["word"].casefold().replace("plebian", "plebeian")
    source_id = source_id.replace("‐", "-").replace("‑", "-").replace("–", "-").replace("—", "-")
    assert source_id in by_id, f"Missing Piqosity headword: {item['word']}"
    assert item["source"] in by_id[source_id]["sources"]

assert len(tested) == 148
for item in tested:
    assert item["word"] in by_id, f"Missing tested family: {item['word']}"
    assert "ISEE Test Samples" in by_id[item["word"]]["sources"]

for item in words:
    expected = (
        ("Familiar", 1) if item["frequency"] >= 4.5 else
        ("Developing", 2) if item["frequency"] >= 3.5 else
        ("Challenging", 3) if item["frequency"] >= 2.8 else
        ("Advanced", 4) if item["frequency"] >= 2.0 else
        ("Rarest", 5)
    )
    assert (item["difficulty"], item["difficultyTier"]) == expected, f"Wrong difficulty: {item['id']}"

print(f"Validated {len(words):,} unique entries.")
print(f"Preserved {len(original):,} original entries.")
print(f"Included {len(tested)} tested word families and all Piqosity Middle headwords.")
