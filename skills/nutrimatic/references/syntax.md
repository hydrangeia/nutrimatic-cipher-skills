# Nutrimatic — full syntax reference

Source: nutrimatic.org main page + usage guide (2024 edition). This is the authoritative
spec, condensed. Read the relevant section, then build the pattern.

## Table of contents
1. What it matches (normalization)
2. Character classes
3. Quoted phrases (word breaks)
4. `&` intersection
5. `<>` anagrams
6. Worked puzzle-hunt examples
7. Performance model & limits

---

## 1. What it matches (normalization)

Nutrimatic matches against every word/phrase occurring in Wikipedia ≥5 times
(~23.7M entries). The corpus text is normalized:

- Everything is lowercase **letters, digits, and spaces** — nothing else.
- Most punctuation becomes a space; **apostrophes are removed** (not spaced).
  - "Fleur-de-lis" → `fleur de lis`
  - "I'm Jack's total lack of surprise." → `im jacks total lack of surprise`
- It can stitch together multiple known words/phrases, so it finds multi-word answers
  **without being told the word boundaries** — e.g. `subject of blood and whiskey`.
- Results are ordered by corpus frequency: "reasonable" matches first, obscure ones later.

The query language is POSIX extended regular expressions (ERE) **without** POSIX
character classes, plus the extensions below. Standard operators work as usual:
`[]` `()` `{}` `|` `.` `?` `*` `+`.

## 2. Character classes

Uppercase letters and some punctuation are repurposed (they can't appear in the corpus):

| Token | Meaning | Equivalent |
|-------|---------|------------|
| `A` | any alphabetic character | `[a-z]` |
| `C` | any consonant (**including y**) | `[bcdfghjklmnpqrstvwxyz]` |
| `V` | any vowel (**excluding y**) | `[aeiou]` |
| `_` | any letter or number | `[a-z0-9]` |
| `#` | any digit | `[0-9]` |
| `-` | an optional space | `( ?)` |

`.` is still the regex "any character" (and matches a space too). The `-` and `_` tokens
are mostly useful **inside quoted phrases** — outside them, spaces are inserted freely so
they add little.

## 3. Quoted phrases — controlling word breaks

**By default Nutrimatic may insert a space anywhere in the pattern when matching.** So
`CVCVCVCVCV` matches `literature` (one word) but also `have become` and `was used as a`.

Wrap part or all of the pattern in `"…"` to forbid inserted spaces there:

- `"CVCVCVCVCV"` → only single 10-letter words.
- `"CVCVC VCVCV"` → only two explicit 5-letter words (space is literal).
- `"CVCVC-VCVCV"` → one 10-letter word **or** an evenly-split 5+5 pair (`-` = optional space).

Quote just the sub-expression you need to constrain; the rest can float.

## 4. `&` — intersection (AND)

`exprA&exprB` requires **both** to match. Parallel constraints:

`_*a_*&_*b_*&_*c_*&_{5,}` → a single run containing an `a`, a `b`, and a `c` (any order),
at least 5 characters long.

**Warning:** parsing cost can grow exponentially with many (10+) `&` clauses. Small
intersections are fine.

## 5. `<>` — anagrams

`<...>` matches any arrangement of the contents.

- `<act>` → `act`, `cat`, … (any order of a,c,t).
- Parts can be regexes in parentheses: `<(ag)(m)(ra)__>` → any 7-letter run containing
  `ag`, `m`, `ra`, plus two other letters.
- Anagrams can sit inside a bigger pattern with partial order info:
  `<aan>g<amr>` matches `anagram` but not `margana`.
- To keep an anagram within a single word, quote it: `"<act>"`.

**Warnings:**
- Large/complex anagrams (>10–15 letters, or several chunks that can match the same text,
  or deep nesting) are slow to parse and search.
- Known bug: with wildcard/multi-char anagram parts, results occasionally are **not** true
  anagrams of the input — verify fancy anagram output by hand.

## 6. Worked puzzle-hunt examples (from the usage guide)

**Fill a letter to make a word from a suffix + new letter + prefix**
Row `MOCHIT / HATORY`, ≥5 letters:
```
"(((((m?o)?c)?h)?i)?t)?_(h(a(t(o(ry?)?)?)?)?)?&_{5,}"
```
Each leading letter optional (a nested-optional "suffix" ladder), a wildcard `_` in the
middle, a nested-optional "prefix" ladder, intersected with a ≥5 length constraint.

**Reorder letter-triples into a clue, some left over** (pick 6 of 9, = 18 letters):
```
"<(-may)?(-sit)?(tit)?(ble)?(com)?(iks)?(ial)?(im b)?(-mon)?>"&(_{18})
```
Anagram of optional triples; `-`/spaces mark allowed word breaks; total pinned to 18.
→ `mayim bialiks sitcom`.

**Letter bank — phrase using each of a set of letters ≥ once** (bank `AEHIMNPRSW`):
```
[aehimnprsw]*&_*a_*&_*e_*&_*h_*&_*i_*&_*m_*&_*n_*&_*p_*&_*r_*&_*s_*&_*w_*
```
→ `new hampshire`.

**Drop one letter from each chunk, then concatenate** (CHARM/ELTON/CHEST/ONE):
```
(c?h?a?r?m?&_{4})(e?l?t?o?n?&_{4})(c?h?e?s?t?&_{4})(o?n?e?&_{2})
```
Every letter optional; each chunk length pinned to (original − 1). → `charlton heston`.

**Insert W,A,T,E,R in order into HEGM** ("add water"):
```
<waterhegm>&_*w_*a_*t_*e_*r_*
```
Anagram of all letters, with W<A<T<E<R order enforced. → `wheat germ`.

**Series of internally-scrambled 3-letter chunks, order fixed**:
```
<het><ral><seg><tan><rut><bla><oody><afl><ndi><cin><awe><ter>
```
→ `the largest natural body of land in ice water`.

## 7. Performance model & limits

- Internally a frequency-weighted trie (23,744,883 entries, 258MB index); best-first
  search over a priority queue ordered by corpus frequency.
- A query is cut off after ~**30 seconds** or ~**1,000,000 nodes** searched.
- Fast: single-word (quoted) patterns, bounded lengths.
- Slow / risky: long or nested anagrams, many `&` clauses, unbounded `*` over loose classes.
- If a query times out, tighten it: quote to a single word, bound lengths with `{n}` /
  `{n,m}`, or reduce anagram parts.
