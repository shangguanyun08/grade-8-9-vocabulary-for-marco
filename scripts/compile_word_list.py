"""Compile the captured Zozeck Grade 8-9 lessons into one ranked list."""

from __future__ import annotations

import json
import re
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any

SITE_DIR = Path(__file__).resolve().parents[1]
WORD_FREQ_RUNTIME = SITE_DIR / ".python"
if WORD_FREQ_RUNTIME.exists():
    sys.path.insert(0, str(WORD_FREQ_RUNTIME))

try:
    from wordfreq import zipf_frequency  # type: ignore
except ImportError:  # Keep the checked-in frequency values usable offline.
    zipf_frequency = None

SOURCE = SITE_DIR / "data" / "zozeck-grade-8-9-raw.json"
OUTPUT = SITE_DIR / "words.json"


def clean_text(value: Any) -> str:
    text = str(value or "")
    text = text.replace("\u00a0", " ").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n+ *", " · ", text)
    return text.strip(" \n\t;")


def display_term(value: Any) -> str:
    term = clean_text(value)
    return term[:1].upper() + term[1:] if term else ""


def ranking_term(term: str) -> str:
    normalized = term.casefold().split(";", maxsplit=1)[0]
    normalized = normalized.replace("sth", "something").replace("sb", "somebody")
    normalized = re.sub(r"[()]", " ", normalized)
    normalized = re.sub(r"[^a-z0-9' -]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def meaning_from_solution(term: str, solution: Any) -> str:
    meaning = clean_text(solution)
    prefix = re.compile(rf"^\s*{re.escape(term)}\s*[:：-]\s*", re.IGNORECASE)
    meaning = prefix.sub("", meaning, count=1)
    if meaning == clean_text(solution) and ":" in meaning:
        before, after = meaning.split(":", maxsplit=1)
        if len(before) <= max(len(term) + 8, 40):
            meaning = after.strip()
    return meaning or clean_text(solution)


def definition_score(definition: str) -> tuple[int, int]:
    has_part_of_speech = int(bool(re.search(r"\b(adj|adv|noun|verb|n|v)\.?\b", definition, re.I)))
    return (has_part_of_speech, min(len(definition), 500))


raw: list[dict[str, Any]] = json.loads(SOURCE.read_text(encoding="utf-8"))
raw.sort(key=lambda item: int(item["sourceIndex"]))

previous_frequencies: dict[str, float] = {}
if OUTPUT.exists():
    previous_frequencies = {
        item["id"]: float(item["frequency"])
        for item in json.loads(OUTPUT.read_text(encoding="utf-8"))
    }

frequency_overrides = {
    "a word or two": 5.15,
    "distributing": 4.16,
    "multilingual": 3.42,
    "positive attitude": 4.35,
    "tension": 4.39,
    "with a single leap": 3.72,
}

records: OrderedDict[str, dict[str, Any]] = OrderedDict()
for item in raw:
    term = display_term(item.get("word"))
    if not term:
        continue
    meaning = meaning_from_solution(term, item.get("solution"))
    if not meaning:
        continue
    key = term.casefold()
    chapter = f"Chapter {int(item['chapter'])}"
    if key not in records:
        records[key] = {
            "id": key,
            "word": term,
            "meaning": meaning,
            "collection": "Grade 8-9",
            "sources": [],
            "firstSourceIndex": int(item["sourceIndex"]),
        }
    record = records[key]
    if definition_score(meaning) > definition_score(record["meaning"]):
        record["meaning"] = meaning
    if chapter not in record["sources"]:
        record["sources"].append(chapter)

ranked: list[dict[str, Any]] = []
for record in records.values():
    record["sources"].sort(key=lambda value: int(value.split()[-1]))
    if zipf_frequency is not None:
        frequency = zipf_frequency(ranking_term(record["word"]), "en")
    else:
        frequency = previous_frequencies.get(
            record["id"], frequency_overrides.get(record["id"], 0.0)
        )
    record["frequency"] = round(frequency, 3)
    ranked.append(record)

# Common English appears first. Word count, spelling length, alphabetical order,
# and original lesson position provide deterministic tie-breakers.
ranked.sort(
    key=lambda item: (
        -item["frequency"],
        len(item["word"].split()),
        len(item["word"]),
        item["word"].casefold(),
        item["firstSourceIndex"],
    )
)
for rank, record in enumerate(ranked, start=1):
    record["rank"] = rank
    record.pop("firstSourceIndex")

OUTPUT.write_text(
    json.dumps(ranked, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
    newline="\n",
)
print(f"Wrote {len(ranked)} unique entries from {len(raw)} Zozeck lesson positions.")

