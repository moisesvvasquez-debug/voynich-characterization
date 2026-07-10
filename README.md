# Signal Before Sense — an information-theoretic characterization of the Voynich Manuscript

**This is not a decipherment.** It is an honest attempt to answer two prior questions about
the Voynich Manuscript (Beinecke MS 408) *without reading a single word*:

1. Does the text carry information at all, or is it meaningless fabrication?
2. If it carries information, **what kind of machine produced it**?

The work reproduces several established results independently, with a single consistent
pipeline, and reports the analyses that **failed** as first-class results — because on a
problem this crowded with premature "solutions," knowing which footholds do *not* exist is
as valuable as any that might.

## Read it

- **Paper (English):** https://claude.ai/code/artifact/e67eb8a2-552a-43ff-adb1-281fc244770f
- **Paper (Español):** https://claude.ai/code/artifact/943d66b2-17e3-4c7b-ba78-7c830945fc44
- **Interactive — the three-dial generator:** [EN](https://claude.ai/code/artifact/fc785537-863f-4b6f-887b-328895c6a1ef) · [ES](https://claude.ai/code/artifact/5bbd2b47-eff3-4a61-b542-44a2f427c9cf)
- Companion pieces (self-contained HTML): `kill-the-dubs.html`, `cientifica.html`, `guia.html`, `mapa.html`, `volvelle.html`, `como-se-hizo.html`

## What survives the tests (headline findings)

- **Not random.** Zipfian frequencies, low type/token ratio — decisively unlike gibberish.
- **Anomalously low character-conditional entropy** (h₂ ≈ 2.26 bits, vs ~3.04 for Spanish and
  3.0–3.6 for 25 tested languages) — the manuscript is *more* predictable than any natural writing.
- **Vocabulary tracks illustrated subject matter at 165σ** above chance (Montemurro & Zanette's
  result, reproduced), surviving controls for the two Currier "languages."
- **Words are combinatorial, not lexical** — assembled from a small stock of prefix·core·suffix
  slots; the reused unit is *sub-word*, not the word.
- **Positional locking:** glyph↔position mutual information (0.72 bits) exceeds all nineteen
  Latin-alphabet languages tested; only syllabic/abjad scripts reach it.
- **Every word-hunting crib fails**, and a multilingual phonetic-match test shows the most
  seductive coincidences (`chedy`~*chaud*, `chor`~*psychros*) are statistically indistinguishable
  from random strings — the trap that has consumed a century of "solutions."

**The honest limit:** the surface statistics cannot decide whether the code carries meaning or
is a mechanical generator. That tie is unbreakable from the text alone.

## Method — "Kill the Dubs" (KTD)

A dub is a *dubious* claim wearing the costume of a fact. Each step finds one and kills it:
**(1)** contrast against chance (null models) · **(2)** try to break the hypothesis, not confirm it
· **(3)** verify at the source, never from memory · **(4)** ventilate the nulls and your own errors
· **(5)** kill the temptation to over-claim. What survives is asserted; what doesn't is declared.
See `kill-the-dubs.html`.

## Repository

- `paper.html` / `paper_es.html` — the paper (EN / ES), self-contained.
- `rueda-generador*.html` — the interactive three-dial generator (EN / ES).
- `*.py` — the analysis scripts (each reads `voy_lsi.txt` from the working directory).
- `voy_lsi.txt` — the EVA transliteration (Takahashi, Landini–Stolfi interlinear archive; code `H`).
- `REFERENCES.bib` — verified bibliography.

External comparison corpora (Spanish, Latin, Arabic, Aramaic, Sanskrit, UDHR set) and the
Beinecke page images are **not redistributed here**; scripts that use them expect them in the
working directory.

## License

- **Code** (`*.py`, interactive HTML generators) — **MIT** (`LICENSE`).
- **Papers, text, figures** — **CC BY 4.0** (`LICENSE-TEXT.md`).
- The Voynich EVA transliteration and external corpora keep their own terms (credited in the paper).

## Status & author

Working preprint · not peer-reviewed. Author: **Carlos Moisés Vásquez** ·
moises.vvasquez@gmail.com. Corrections and objections are genuinely welcome.
