---
name: puzzle-ciphers
description: >-
  Identify and crack classic ciphers and encodings that show up in puzzle hunts, using a
  bundled standard-library Python toolkit (no installs). Use this whenever a puzzle
  presents a string that looks encoded and needs decoding — a run of dots and dashes,
  strings of A/B or 0/1, a block of nonsense letters, number sequences, "shift/rotate the
  alphabet", an anagram of the wrong shape, ROT13/Caesar/Atbash, Vigenere with or without a
  known key, Baconian, Morse, A1Z26, Polybius, tap code, rail fence, affine, base64/hex/
  binary, or phone-keypad text. Trigger this even when the user doesn't name the cipher —
  "what does this decode to", "can you crack this", "this is probably a substitution
  cipher", or just a pasted mystery string in a hunt context all qualify. Start by running
  scripts/identify.py to triage the string, then run the suggested scripts/ciphers.py
  command(s) and rank results by how English-like they read.
---

# Puzzle-hunt cipher toolkit

A batteries-included kit for the "crank-turning" decode steps of puzzle hunts. Two Python
scripts (standard library only — runnable with plain `python`, no packages, no venv):

- `scripts/identify.py` — triage a mystery string: reports its character set, length,
  index of coincidence, and letter frequencies, then suggests which ciphers to try.
- `scripts/ciphers.py` — the transforms and brute-forcers.

Paths are relative to this skill's directory. Invoke as, e.g.,
`python "<this-skill-dir>/scripts/ciphers.py" caesar --all "text"`.

## Workflow (identification flow)

Follow this order — it's fastest and avoids guessing:

1. **Triage.** Run `identify.py "<the string>"`. Read its character-set/IC report and its
   ranked suggestions. This narrows a huge space to 1–3 likely cipher families.
2. **Try the suggestions, cheapest first.** Caesar/Atbash/ROT and the numeric/symbolic
   decodes are instant and definitive — always try them before anything fancy.
3. **Rank by English-ness.** Brute-force commands print candidates ordered by chi-squared
   distance to English (lower = more English-like). The ranking is a heuristic — eyeball
   the top few, don't blindly take rank 1, especially on short strings (<40 letters) where
   letter statistics are noisy.
4. **Feed results forward.** A decoded string is often itself an instruction, an anagram,
   or a word-shape — hand it to the `nutrimatic` skill or decode again.
5. **Mind the human-only steps.** These tools do one transform; figuring out *which*
   transform and *what the answer means* is the solver's job.

## Command reference

Every command takes text as trailing args or via stdin. Full help: `ciphers.py <cmd> -h`,
or `ciphers.py list`.

### Monoalphabetic (letter → letter)
- `caesar --all "text"` — try all 26 shifts, ranked by English-ness. **The go-to first move
  for any letters-only string.** `caesar --shift N` applies a specific shift.
- `rot13 "text"` / `rot47 "text"` — fixed rotations (rot47 covers printable ASCII).
- `atbash "text"` — reverse the alphabet (a↔z).
- `affine --solve "text"` — brute-force all 312 affine keys, ranked. `affine --a A --b B`
  to apply/`--encrypt` a known key.
- `substitution --key <26 letters> "text"` — apply a full substitution alphabet
  (a→key[0] … z→key[25]).
- `freq "text"` — letter-frequency table + index of coincidence, for hand-solving a
  general substitution.

### Polyalphabetic
- `vigenere --key KEY "text"` (add `--encrypt` to encode).
- `vigenere --solve "text"` — estimate key length via index of coincidence, then recover
  the key column-by-column. **Wants ~150+ letters** to be reliable; on short text pass
  `--keylen N` (or a known key) instead, and read the printed key-length ranking.

### Symbolic / numeric encodings
- `morse ".... . .-.. .-.. ---"` — decode (`--encode` to encode). Word gap = `/` or `|`
  or double space.
- `bacon "AABBB AABAA ..."` — Baconian; prints **both** the 24-letter (classic, i=j/u=v)
  and 26-letter interpretations, since hunts use either. Accepts A/B or 0/1.
- `a1z26 "8 5 12 12 15"` — numbers 1–26 → letters (`--encode` to reverse).
- `fromdec "72 73"` — decimal ASCII codes → text.
- `frombin` / `fromhex` / `frombase64` / `frombase32` — base decodes to text.
- `t9 "44 33"` — phone multi-tap (press-count) → letters.

### Grid / digraph ciphers
- `polybius "23 15 ..."` — 5×5 Polybius (default alphabet drops J; `--square` for a custom
  25- or 36-cell alphabet). `--encode` to encode.
- `tap "23 15 ..."` — tap code (5×5 grid without K; K reads as C). Digits 1–5, any spacing.
- `playfair --key KEYWORD "text"` — Playfair digraph cipher (needs the keyword; `--encrypt`
  to encode). Decryption leaves the padding `x`/doubled-letter artifacts for you to clean up.

### Transposition
- `railfence --rails N "text"` — rail-fence decode (`--encode` to encode). Add `--strip`
  to ignore spaces.
- `columnar --key KEYWORD "text"` — columnar transposition (needs the keyword; `--encrypt`
  to encode, `--strip` to drop spaces first).
- `keyboard --shift N --direction left|right "text"` — shift each letter to its QWERTY
  row-neighbour (wraps within the row). Common "typed one key over" gimmick.

## Worked example

```
$ python scripts/identify.py "gttuatiksktz"
... index of coincidence ... Suggestions: 1. Monoalphabetic substitution ...
$ python scripts/ciphers.py caesar --all "gttuatiksktz"
shift  6 (chi2  22.9): announcement   <-- best
```

## When to reach for more

For deeper theory, cipher-identification tells, and ciphers not covered by a one-liner
(Playfair, columnar transposition, keyed alphabets, fractionation), read
[references/cipher-guide.md](references/cipher-guide.md). If a hunt needs a cipher this kit
lacks, add a subcommand to `ciphers.py` — it's plain stdlib and easy to extend.
