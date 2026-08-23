"""Build checked-in headword sources from Marco's tests and practice banks."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


SITE_DIR = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = SITE_DIR.parent

TESTS = {
    "ISEE MiddleTest WTE": [
        "reluctance", "solitary", "keen", "abruptness", "feebly", "unruly",
        "insight", "pacify", "agile", "conform", "episode", "presume", "intricate",
        "lofty", "endeavor", "plume", "torrid", "insolently", "endangering",
        "assembled", "optimistic", "pinnacle", "barren", "primary", "aspiration",
        "thriving", "persevere", "subside", "prone", "acknowledging", "obstinate",
        "supplement", "inundated", "noncommittal", "haphazard",
    ],
    "ISEE Mock 1": [
        "consent", "momentary", "perspective", "aggravate", "enhance", "moral",
        "aspiration", "fathom", "tenacious", "devious", "disposition", "coerce",
        "demeanor", "snarky", "poised", "unfounded", "lope", "pertinent", "aversion",
        "evade", "disrupting", "disregarding", "willful", "abrasive", "scathing",
        "validated", "ambiguous", "belligerent", "amended", "preconceived",
        "distinguished", "advocating", "delectable", "alleviate", "collaborative",
        "homogeneous", "revered", "callous", "cynical", "inundated",
    ],
    "ISEE Mock 2": [
        "motive", "bizarre", "remorseful", "deliberate", "sophisticated", "privileged",
        "arbitrary", "daunting", "mock", "amend", "notorious", "persevere", "impartial",
        "affiliation", "connotation", "avid", "defame", "candor", "heedful", "miserly",
        "muffled", "defensive", "mediate", "resourceful", "acclimated", "elusive",
        "indispensable", "renowned", "incessant", "adversity", "replenish", "sentimental",
        "devoted", "prevail", "feasible", "malleable", "bashful", "falter", "sinister",
        "grievances",
    ],
    "ISEE Mock 3": [
        "oblivious", "devastated", "procrastinate", "portray", "abrupt", "controversial",
        "ample", "impending", "condone", "apprehensive", "supplement", "lure", "allotted",
        "incompetent", "benign", "abdicate", "copious", "accentuate", "repeal", "blunder",
        "hesitant", "advising", "retain", "pristine", "notorious", "credible", "foreign",
        "origin", "fatigued", "undermined", "arid", "instigate", "eclectic", "relinquish",
        "acuity", "altruistic", "inherently", "intimidate", "boasts", "assertion",
    ],
}

EXPLICIT_VARIANTS = {
    "reluctance": ["reluctant"], "abruptness": ["abrupt"], "feebly": ["feeble"],
    "insolently": ["insolent"], "endangering": ["endanger"], "assembled": ["assemble"],
    "aspiration": ["aspire"], "thriving": ["thrive"], "acknowledging": ["acknowledge"],
    "inundated": ["inundate"], "poised": ["poise"], "disrupting": ["disrupt"],
    "disregarding": ["disregard"], "validated": ["validate"], "amended": ["amend"],
    "preconceived": ["preconceive", "preconception"], "distinguished": ["distinguish"],
    "advocating": ["advocate"], "collaborative": ["collaborate"], "revered": ["revere"],
    "privileged": ["privilege"], "daunting": ["daunt"], "affiliation": ["affiliate"],
    "connotation": ["connote"], "muffled": ["muffle"], "acclimated": ["acclimate"],
    "renowned": ["renown"], "devoted": ["devote"], "grievances": ["grievance"],
    "devastated": ["devastate"], "impending": ["impend"], "allotted": ["allot"],
    "hesitant": ["hesitate"], "advising": ["advise"], "origin": ["originate"],
    "fatigued": ["fatigue"], "undermined": ["undermine"], "acuity": ["acute"],
    "altruistic": ["altruism"], "inherently": ["inherent"], "boasts": ["boast"],
    "assertion": ["assert"],
}

CURATED_SCORE_9 = """
aberrant abhor abjure abstemious acerbic acquiescent adroit aesthetic affable alacrity
ambivalent ameliorate anachronism anathema anomalous antithesis apathy appease arduous
articulate ascetic assiduous austere avarice bellicose benevolent bombastic brevity brusque
cajole capricious castigate caustic circumspect clandestine cogent complacent conciliatory
condescending conundrum cryptic deference delineate deride despondent didactic diffident
diligent discern disdain disinterested dogmatic dubious eloquent enigmatic ephemeral equanimity
equivocal erudite esoteric euphemism exacerbate exemplary exonerate expedient fastidious
fervent fortuitous frugal futile garrulous hackneyed haughty hypothetical iconoclast idyllic
imminent immutable impetuous implicit incredulous indignant indolent ineffable ingenuous
inhibit innocuous insipid intrepid irascible laconic lethargic magnanimous meticulous mitigate
morose mundane nebulous nonchalant obdurate obsequious ostentatious paradox parsimonious
pedantic perfunctory pervasive pragmatic precarious prodigal prolific prudent quixotic rancor
reticent sagacious salient scrutinize spurious stoic superfluous surreptitious taciturn transient
ubiquitous vacillate venerate vindicate wary zealous
""".split()


def normalize(value: str) -> str:
    return (
        value.strip()
        .casefold()
        .replace("\u2010", "-")
        .replace("\u2011", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2019", "'")
    )


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


test_records: dict[str, dict[str, object]] = {}
for test_name, terms in TESTS.items():
    for surface in terms:
        surface = normalize(surface)
        variants = [normalize(item) for item in EXPLICIT_VARIANTS.get(surface, [])]
        canonical = variants[0] if variants else surface
        record = test_records.setdefault(
            canonical,
            {"word": canonical, "aliases": [], "tests": []},
        )
        for alias in [surface, *variants[1:]]:
            if alias != canonical and alias not in record["aliases"]:
                record["aliases"].append(alias)
        if test_name not in record["tests"]:
            record["tests"].append(test_name)

write_json(
    SITE_DIR / "data" / "isee-test-headwords.json",
    sorted(test_records.values(), key=lambda item: str(item["word"])),
)

practice_sources = {
    "Marco Hard Practice": WORKSPACE_DIR / "marco-isee-hard-practice" / "data" / "questions.js",
    "Marco Word Mastery": WORKSPACE_DIR / "isee-word-mastery" / "data" / "questions.js",
}
practice_words: dict[str, set[str]] = defaultdict(set)
single_word = re.compile(r"^[A-Za-z][A-Za-z'\u2019\u2010-\u2015-]*$")

for source, path in practice_sources.items():
    script = path.read_text(encoding="utf-8")
    script = re.sub(r"^\s*export\s+const\s+questionBank\s*=\s*", "", script)
    script = re.sub(r";\s*$", "", script)
    bank = json.loads(script)
    for question in bank["questions"]:
        values = [choice["text"] for choice in question["choices"]]
        if question["type"] == "synonym":
            values.append(question["prompt"])
        for value in values:
            value = normalize(value)
            if single_word.fullmatch(value) and len(value) >= 3:
                practice_words[value].add(source)

practice_records = [
    {"word": word, "sources": sorted(sources)}
    for word, sources in sorted(practice_words.items())
]
write_json(SITE_DIR / "data" / "practice-headwords.json", practice_records)
write_json(
    SITE_DIR / "data" / "curated-score-9-headwords.json",
    [{"word": normalize(word), "source": "Curated Score 9"} for word in CURATED_SCORE_9],
)

print(f"Wrote {len(test_records)} tested word families.")
print(f"Wrote {len(practice_records)} practice-bank headwords.")
print(f"Wrote {len(CURATED_SCORE_9)} curated Score 9 candidates.")
