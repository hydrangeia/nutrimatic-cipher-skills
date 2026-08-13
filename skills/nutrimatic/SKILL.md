---
name: nutrimatic
description: >-
  Construct Nutrimatic pattern queries and build the ready-to-open search URL for
  word/phrase puzzle solving. Use this whenever a puzzle hunt task involves finding a
  word or phrase that fits a shape or set of constraints — fill-in-the-blank with known
  letters, "what N-letter word matches ___", anagrams and anagrams-with-extra-letters,
  consonant/vowel patterns, phrases mined from a corpus, letter-bank / letter-drop
  problems, or "add these letters in order" wordplay. Trigger this even when the user
  doesn't say "nutrimatic" by name — any request like "find a 7-letter word starting with
  KR ending in W", "anagram of TEAROSE plus one letter", or "what phrase can I make from
  these tiles" should use it. Produces a correct Nutrimatic pattern plus the
  https://nutrimatic.org/2024/?q=... URL.
---

# Nutrimatic query builder

Nutrimatic matches a regex-style pattern against ~24M words/phrases mined from Wikipedia,
returning the most **corpus-frequent** (most "natural") matches first. It is the go-to
crank-turning tool for word-shape and anagram sub-steps of puzzle hunt problems. It does
**not** solve puzzles end to end — it answers "what real words/phrases fit this shape?".

## How to use this skill

1. Translate the solver's constraint into a Nutrimatic pattern (rules below).
2. Emit the pattern **and** a clickable URL: `https://nutrimatic.org/2024/?q=<url-encoded pattern>`
   (use the `/2024/` edition — refreshed index; `/2016/` is the classic original).
3. If the user wants results inline, fetch that URL and report the top hits.
4. Explain any human-side constraints Nutrimatic can't enforce (e.g. "must be a common
   non-plural word", "each letter used once") so the user filters the output.

When a query is complex, ambiguous, or involves anagrams/intersections, read
[references/syntax.md](references/syntax.md) for the full spec, warnings, and worked
puzzle-hunt examples before committing to a pattern.

## Core rules (the ones you must not get wrong)

- **Text is normalized**: lowercase letters, digits, spaces only. Punctuation → space;
  apostrophes are *deleted* ("fleur-de-lis" → `fleur de lis`, "I'm" → `im`).
- **Spaces are inserted automatically by default.** `CVCVCVCVCV` matches single words
  *and* phrase fragments ("have become"). To pin word boundaries, use **quoted phrases**:
  - `"CVCVCVCVCV"` → single 10-letter words only.
  - `"CVCVC VCVCV"` → exactly two 5-letter words.
  - `"CVCVC-VCVCV"` → one word *or* an evenly-split pair (`-` = optional space).
- Literal `a-z`, `0-9`, space match themselves.
- `[]`, `()`, `{}`, `|`, `.`, `?`, `*`, `+` — standard POSIX-ERE regex meanings.

## Cheat sheet — special characters

| Token | Means | Equivalent |
|-------|-------|------------|
| `A` | any letter | `[a-z]` |
| `C` | consonant (incl. y) | `[bcdfghjklmnpqrstvwxyz]` |
| `V` | vowel (excl. y) | `[aeiou]` |
| `_` | any letter or digit | `[a-z0-9]` |
| `#` | any digit | `[0-9]` |
| `.` | any single char (incl. space) | regex `.` |
| `-` | optional space | `( ?)` |
| `"…"` | forbid auto word-breaks inside | — |
| `expr&expr` | **both** must match (intersection) | — |
| `<letters>` | anagram of the contents | — |

`_` and `-` are mainly useful **inside quotes** (outside, spaces float freely anyway).

## Recipe patterns (map the constraint → the query)

- **Known letters + blanks, one word**: `"kr...w"` (7-letter word `kr____w`), or use `A`
  for unknown letters: `"krAAAAw"`. Length via `{n}`: `"krA{3}w"`.
- **At least / exactly N letters**: `_{5,}` (≥5), `_{7}` (exactly 7). Add `&` to combine
  with another constraint.
- **Plain anagram**: `<tearose>` (single word: `"<tearose>"`).
- **Anagram + one (or k) extra letters**: `<tearoseA>` (one wildcard letter added).
- **Contains all of some letters, any order** (letter bank): `_*a_*&_*b_*&_*c_*` — one
  `_*x_*` clause per required letter, `&`-joined.
- **Letters must appear in a given order** (not necessarily adjacent): `_*w_*a_*t_*e_*r_*`.
  Combine with an anagram to constrain the whole: `<waterhegm>&_*w_*a_*t_*e_*r_*`.
- **Drop one letter from each of several chunks, then concatenate**:
  `(c?h?a?r?m?&_{4})(e?l?t?o?n?&_{4})...` — every letter optional, per-chunk length pinned.
- **Reorder given tiles/triples** (some optional/left over): quote it, make each tile a
  parenthesised optional inside an anagram, then pin total length:
  `"<(tit)?(ble)?(com)?(mon)?...>"&(_{18})`.

## URL construction

- Base: `https://nutrimatic.org/2024/?q=`
- Append the **URL-encoded** pattern. Characters that must be encoded: `"`→`%22`,
  `#`→`%23`, `&`→`%26`, `<`→`%3C`, `>`→`%3E`, `+`→`%2B`, space→`%20`.
- Example: pattern `"CVCVCVCVCV"` → `https://nutrimatic.org/2024/?q=%22CVCVCVCVCV%22`

## Performance / gotchas (warn the user when relevant)

- Queries are cut off after ~30s or 1,000,000 nodes. Single-word (quoted) queries are fast.
- **Anagrams** over ~10–15 parts, or with non-single-letter chunks, get slow and the parser
  can even return non-anagrams — double-check fancy anagram output.
- Large `&` intersections (10+ clauses) can blow up exponentially, though small ones are fine.
- Results include misspellings and obscure names (it's Wikipedia). Frequency order helps,
  but the human still picks the sensible answer.
