# Marco's Complete ISEE Vocabulary

A zero-build GitHub Pages study library built by expanding the original Zozeck Grade 8–9 website.

## Published collection

- 5,097 unique words and phrases
- all 1,920 original Zozeck entries and meanings preserved
- 1,009 unique Piqosity Middle-Level headwords
- 1,199 unique Piqosity Upper-Level headwords
- all 148 tested word families from Marco's four analyzed ISEE forms
- useful single-word vocabulary selected from Marco's Hard Practice and Word Mastery banks
- 130 additional high-yield Score 9 candidates
- search, source and study-band filters, sorting, and browser-saved checklist progress

Piqosity supplied the public headwords only. Definitions for newly added entries are generated independently from Princeton WordNet, with a small set of manually written corrections for terms WordNet does not cover. Piqosity definition text is not copied. The WordNet 3.0 notice is included at `data/WORDNET-LICENSE.txt`.

## Rebuild

The checked-in `words.json` is ready for GitHub Pages. To rebuild all data locally:

1. Install `nltk` and `wordfreq` into `.python`.
2. Download the NLTK `wordnet` corpus into `.python/nltk_data`.
3. Run `python scripts/fetch_piqosity_headwords.py` to refresh the public headwords.
4. Run `python scripts/build_source_headwords.py` when the sibling Marco practice repositories are available.
5. Run `python scripts/compile_word_list.py` to rebuild the preserved original list.
6. Run `python scripts/compile_expanded_word_list.py` to generate `words.json` and build statistics.

The source pages are:

- <https://www.piqosity.com/isee-middle-level-vocabulary-list/>
- <https://www.piqosity.com/isee-upper-level-vocabulary-list/>
