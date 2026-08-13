# Cipher identification & solving guide (puzzle hunts)

Companion to `puzzle-ciphers`. Use this to recognize what you're looking at and to handle
ciphers beyond the toolkit's one-liners.

## Identification tells (what the surface looks like)

| Surface signal | Likely cipher / encoding | First move |
|----------------|--------------------------|-----------|
| Only `.` `-` `/` | Morse | `morse` |
| Only two distinct symbols/letters (A/B, •/■), length ÷5 | Baconian | `bacon` |
| Only `0` `1`, length ÷8 | Binary ASCII | `frombin` |
| `0-9a-f` only, even length | Hex ASCII | `fromhex` |
| Numbers all 1–26 | A1Z26 | `a1z26` |
| Numbers all 1–5, even count | Polybius / Tap code | `polybius`, `tap` |
| Numbers ~32–126 | Decimal ASCII | `fromdec` |
| Digits 2–9, repeated runs | Phone multi-tap / T9 | `t9` |
| Mixed-case letters + digits + `+/=` | Base64 | `frombase64` |
| Letters only, IC ≈ 0.066 | Monoalphabetic (Caesar/Atbash/substitution/affine) | `caesar --all`, `freq` |
| Letters only, IC ≈ 0.038–0.045 | Polyalphabetic (Vigenere/Beaufort/running key) | `vigenere --solve` |
| Letters only, every letter of a word present but scrambled | Anagram / transposition | anagram (nutrimatic), `railfence` |
| Pairs of letters, no doubled pair, no J | Playfair | see below |

**Index of coincidence (IC)** is the key discriminator for letters-only text:
English ≈ 0.0667, monoalphabetic ciphers **preserve** it (they permute letters, not
statistics), polyalphabetic ciphers flatten it toward random ≈ 0.0385. Caveat: IC is
unreliable under ~80 letters and on statistically odd plaintext (pangrams, lists), so still
run `caesar --all` — it's free.

## Notes on the built-in ciphers

- **Caesar / ROT** — shift the alphabet by a constant. 26 possibilities; `caesar --all`
  settles it instantly. ROT13 is shift 13; ROT47 rotates printable ASCII (good for
  symbol-laden strings).
- **Atbash** — a↔z, b↔y, … Self-inverse. Ancient, common in hunts as a quick layer.
- **Affine** — `E(x) = a·x + b mod 26`, `a` coprime to 26. 312 keys; `affine --solve`
  brute-forces. Caesar is the special case a=1.
- **Vigenere** — repeating-key shift. Break by (1) find key length via IC / Kasiski, then
  (2) solve each column as a Caesar by frequency. `--solve` does both but needs length
  (~150+ chars). Beaufort and variant-Beaufort are close relatives (try if Vigenere key
  looks *almost* right). A running-key or one-time-pad Vigenere can't be broken this way.
- **Baconian** — each letter → 5 symbols from a 2-element set (often hidden as a typeface,
  case, or two shapes rather than literal A/B). Watch for the 24- vs 26-letter table; the
  toolkit prints both.
- **Morse** — needs clean letter/word separation; ambiguous if the spacing is lost
  (then it's a "Morse with no spaces" puzzle — a different beast, often solved by fitting).
- **Polybius / Tap code** — letters → coordinate pairs in a 5×5 grid. Polybius commonly
  drops J (into I); tap code drops K (into C). A keyed grid changes the alphabet order —
  pass it via `polybius --square <25 letters>`.
- **Rail fence** — write the text in a zigzag over N rails, read off row by row. Try a few
  small rail counts.

## Ciphers NOT covered by a one-liner (hand-solve or extend the script)

- **Simple substitution (general keyed alphabet)** — no formula; use `freq` for the letter
  distribution, seed with `e t a o` and common bigrams (`th`, `he`, `in`), pattern-match
  short words, and iterate. Feed candidate words to the `nutrimatic` skill.
- **Columnar transposition** — plaintext written in rows under a keyword, columns read in
  key order. **Built in when you know the keyword: `columnar --key KEYWORD`.** Without it,
  and if you know the width, try reading columns in different orders / anagram the column
  blocks. Doubling (double transposition) is harder.
- **Playfair** — digraph cipher on a 5×5 keyed square. Tells: even length, no doubled
  letters within a pair, no J. **Built in when you know the keyword: `playfair --key
  KEYWORD`** (hunts usually give it or make it guessable). Without the keyword you must
  reconstruct the square from cribs.
- **Fractionation (Bifid / Trifid / ADFGVX)** — coordinates split and recombined. Usually
  flagged by the puzzle's theme or a given square; solve by hand with the stated key.
- **Book / running-key** — key is a text (a given passage, page numbers). Look for the
  referenced source in the puzzle.
- **Keyboard shifts / substitutions** — QWERTY-neighbor shifts (built in:
  `keyboard --shift N --direction left|right`), phone keypad (`t9`), Dvorak. Try mapping
  against a keyboard layout if letters cluster oddly.

When a hunt leans on one of these repeatedly, add a subcommand to `scripts/ciphers.py` —
it's standard-library and structured for easy extension (one `cmd_*` function + one
`add_parser` block).

## General solving habits

- **Decoding rarely ends the puzzle.** The plaintext is often an instruction ("take the
  third letter of each"), an anagram, or a clue. Keep going.
- **Layers are common.** ROT13 → base64 → A1Z26 chains happen. Re-run `identify.py` on each
  intermediate result.
- **Preserve structure.** Note word lengths, punctuation, and counts before stripping —
  they're often the real signal (enumeration, indexing).
- **Corpus/word validation.** Use the `nutrimatic` skill to confirm a decoded fragment is a
  real word/phrase and to fill gaps.
