"""Merge the original list with ISEE-specific sources into the published list."""

from __future__ import annotations

import json
import re
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any


SITE_DIR = Path(__file__).resolve().parents[1]
PYTHON_RUNTIME = SITE_DIR / ".python"
if PYTHON_RUNTIME.exists():
    sys.path.insert(0, str(PYTHON_RUNTIME))

try:
    import nltk  # type: ignore

    nltk.data.path.insert(0, str(PYTHON_RUNTIME / "nltk_data"))
    from nltk.corpus import wordnet as wn  # type: ignore
except ImportError as error:
    raise SystemExit("Install nltk into .python before compiling.") from error

try:
    from wordfreq import zipf_frequency  # type: ignore
except ImportError as error:
    raise SystemExit("Install wordfreq into .python before compiling.") from error


ORIGINAL = SITE_DIR / "data" / "zozeck-original-words.json"
PIQOSITY = SITE_DIR / "data" / "piqosity-headwords.json"
TEST_WORDS = SITE_DIR / "data" / "isee-test-headwords.json"
PRACTICE = SITE_DIR / "data" / "practice-headwords.json"
CURATED = SITE_DIR / "data" / "curated-score-9-headwords.json"
OUTPUT = SITE_DIR / "words.json"
STATS_OUTPUT = SITE_DIR / "data" / "build-stats.json"

SOURCE_ORDER = [
    "ISEE Test Samples",
    "Piqosity Middle",
    "Piqosity Upper",
    "Marco Hard Practice",
    "Marco Word Mastery",
    "Curated Score 9",
    "Zozeck Grade 8–9",
]

POS_NAMES = {
    "n": "Noun",
    "v": "Verb",
    "a": "Adjective",
    "s": "Adjective",
    "r": "Adverb",
}

DEFINITION_OVERRIDES = {
    "amoral": "Adjective. Lacking moral principles or unconcerned with right and wrong.",
    "begrudgingly": "Adverb. Reluctantly and with resentment.",
    "blasé": "Adjective. Unimpressed because something has become overly familiar.",
    "churlishness": "Noun. Rudeness or a lack of civility.",
    "divisively": "Adverb. In a way that causes disagreement or hostility.",
    "euphoniously": "Adverb. In a pleasing or harmonious-sounding way.",
    "façade": "Noun. The front of a building, or a deceptive outward appearance.",
    "good-natured": "Adjective. Friendly, patient, and pleasant.",
    "hard-nosed": "Adjective. Tough, practical, and unsentimental.",
    "impeachable": "Adjective. Open to accusation or formal challenge for misconduct.",
    "intimidatingly": "Adverb. In a way that causes fear or discourages confidence.",
    "jocularly": "Adverb. In a humorous or playful manner.",
    "knowledgeably": "Adverb. In a well-informed or expert manner.",
    "laid-back": "Adjective. Relaxed and easygoing.",
    "nonvital": "Adjective. Not essential or necessary for life or success.",
    "pixelate": "Verb. To divide or display an image as visible pixels.",
    "scorchingly": "Adverb. With extreme heat or harsh intensity.",
    "self-effacing": "Adjective. Modest and reluctant to draw attention to oneself.",
    "snarky": "Adjective. Critical or mocking in an indirect, sarcastic way.",
    "well-defined": "Adjective. Clearly described, marked, or understood.",
    "well-mannered": "Adjective. Polite and showing good social behavior.",
}

SPELLING_CORRECTIONS = {
    "hardnosed": "hard-nosed",
    "plebian": "plebeian",
}


def normalize(value: Any) -> str:
    return (
        str(value or "")
        .strip()
        .casefold()
        .replace("\u2010", "-")
        .replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2019", "'")
    )


def display(value: str) -> str:
    value = normalize(value)
    return value[:1].upper() + value[1:]


def ranking_term(value: str) -> str:
    value = normalize(value).split(";", maxsplit=1)[0]
    value = value.replace("sth", "something").replace("sb", "somebody")
    value = re.sub(r"[()]", " ", value)
    value = re.sub(r"[^a-z0-9' -]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def wordnet_definition(value: str) -> str | None:
    key = normalize(value)
    if key in DEFINITION_OVERRIDES:
        return DEFINITION_OVERRIDES[key]
    lookup = key.replace("-", "_").replace(" ", "_")
    synsets = wn.synsets(lookup)
    if not synsets:
        return None
    synset = synsets[0]
    definition = synset.definition().strip()
    definition = definition[:1].upper() + definition[1:]
    if definition[-1:] not in ".!?":
        definition += "."
    return f"{POS_NAMES.get(synset.pos(), 'Word')}. {definition}"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


records: OrderedDict[str, dict[str, Any]] = OrderedDict()


def ensure_record(word: str, *, required: bool = False) -> dict[str, Any] | None:
    key = normalize(word)
    if not key:
        return None
    if key in records:
        return records[key]
    meaning = wordnet_definition(key)
    if meaning is None:
        if required:
            raise RuntimeError(f"No independent definition found for required headword: {word}")
        return None
    record = {
        "id": key,
        "word": display(key),
        "meaning": meaning,
        "aliases": [],
        "sources": [],
        "details": [],
    }
    records[key] = record
    return record


def add_source(record: dict[str, Any], source: str, detail: str | None = None) -> None:
    if source not in record["sources"]:
        record["sources"].append(source)
    if detail and detail not in record["details"]:
        record["details"].append(detail)


# Preserve every original entry and its original meaning.
for item in load(ORIGINAL):
    key = normalize(item["word"])
    records[key] = {
        "id": key,
        "word": item["word"],
        "meaning": item["meaning"],
        "aliases": [],
        "sources": ["Zozeck Grade 8–9"],
        "details": list(item.get("sources", [])),
    }


for item in load(PIQOSITY):
    source_word = normalize(item["word"])
    corrected_word = SPELLING_CORRECTIONS.get(source_word, source_word)
    record = ensure_record(corrected_word, required=True)
    assert record is not None
    if source_word != corrected_word and source_word not in record["aliases"]:
        record["aliases"].append(source_word)
    add_source(record, item["source"], f"{item['source']} · Group {item['group']}")


for item in load(TEST_WORDS):
    record = ensure_record(item["word"], required=True)
    assert record is not None
    add_source(record, "ISEE Test Samples")
    for test_name in item["tests"]:
        if test_name not in record["details"]:
            record["details"].append(test_name)
    for alias in item["aliases"]:
        alias = normalize(alias)
        if alias != record["id"] and alias not in record["aliases"]:
            record["aliases"].append(alias)


skipped_practice: list[str] = []
for item in load(PRACTICE):
    source_word = normalize(item["word"])
    corrected_word = SPELLING_CORRECTIONS.get(source_word, source_word)
    record = ensure_record(corrected_word)
    if record is None:
        skipped_practice.append(item["word"])
        continue
    if source_word != corrected_word and source_word not in record["aliases"]:
        record["aliases"].append(source_word)
    for source in item["sources"]:
        add_source(record, source)


skipped_curated: list[str] = []
for item in load(CURATED):
    record = ensure_record(item["word"])
    if record is None:
        skipped_curated.append(item["word"])
        continue
    add_source(record, item["source"])


def study_band(record: dict[str, Any]) -> str:
    sources = set(record["sources"])
    if "ISEE Test Samples" in sources:
        return "Tested"
    if "Piqosity Middle" in sources:
        return "Middle Core"
    if "Piqosity Upper" in sources:
        return "Upper Stretch"
    if sources & {"Marco Hard Practice", "Marco Word Mastery", "Curated Score 9"}:
        return "Score 9 Practice"
    return "Zozeck Foundation"


ranked: list[dict[str, Any]] = []
for record in records.values():
    record["sources"].sort(key=lambda value: SOURCE_ORDER.index(value))
    record["aliases"].sort()
    record["frequency"] = round(zipf_frequency(ranking_term(record["word"]), "en"), 3)
    record["studyBand"] = study_band(record)
    ranked.append(record)

ranked.sort(
    key=lambda item: (
        -item["frequency"],
        len(item["word"].split()),
        len(item["word"]),
        item["word"].casefold(),
    )
)
for rank, record in enumerate(ranked, start=1):
    record["rank"] = rank

OUTPUT.write_text(
    json.dumps(ranked, ensure_ascii=False, separators=(",", ":")) + "\n",
    encoding="utf-8",
    newline="\n",
)

source_counts = {
    source: sum(source in record["sources"] for record in ranked)
    for source in SOURCE_ORDER
}
band_counts = {
    band: sum(record["studyBand"] == band for record in ranked)
    for band in ["Tested", "Middle Core", "Upper Stretch", "Score 9 Practice", "Zozeck Foundation"]
}
stats = {
    "total": len(ranked),
    "original": len(load(ORIGINAL)),
    "sourceCounts": source_counts,
    "bandCounts": band_counts,
    "skippedPractice": sorted(skipped_practice),
    "skippedCurated": sorted(skipped_curated),
}
STATS_OUTPUT.write_text(
    json.dumps(stats, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
    newline="\n",
)

print(json.dumps(stats, ensure_ascii=False, indent=2))
