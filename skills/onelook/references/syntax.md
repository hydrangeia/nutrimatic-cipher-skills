# OneLook — full query reference

Source: onelook.com "How to search" (captured 2026). OneLook = OneLook Thesaurus and
Reverse Dictionary; scans ~16.9M entries across ~805 dictionaries plus a semantic engine.

## Search URL
`https://www.onelook.com/?w=<url-encoded query>`

## Pattern symbols

| Symbol | Meaning |
|--------|---------|
| `?` | any single letter |
| `*` | any number of letters (including zero) |
| `#` | a consonant |
| `@` | a vowel |
| `-abcd` | disallow the letters a, b, c, d |
| `+abcd` | restrict to only the letters a, b, c, d |
| `//abcd//` | unscramble (anagram) the letters between the slashes |
| `:meaning` | words related to the concept/meaning (reverse dictionary / thesaurus) |
| `pattern:meaning` | spelling `pattern` AND meaning-related to `meaning` |
| `**word**` | phrases that contain `word` |
| `expand:abc` | phrases whose words spell the acrostic a.b.c. |
| `,` | AND together multiple patterns |

## Worked examples (from OneLook's own help)

| Query | Finds |
|-------|-------|
| `bluebird` | definitions of bluebird |
| `blue*` | words starting with blue |
| `*bird` | words ending with bird |
| `bl????rd` | starts bl, ends rd, 4 letters between (9 total) |
| `//fuljyo//` | words that are an anagram of the letters f,u,l,j,y,o |
| `?????,*y*` | 5 letters AND contains a "y" |
| `bl*:snow` | starts with bl AND meaning related to snow |
| `:snow` | words related to snow |
| `:winter sport` | words related to the concept "winter sport" |
| `**winter**` | phrases that contain the word winter |
| `expand:nasa` | phrases that spell out n.a.s.a. |

## Puzzle-hunt usage notes

- **The meaning axis is the point.** For a clue like "___ (6), means 'stubborn'", use
  `??????:stubborn`. Nutrimatic can't do this — it doesn't know meanings.
- **Combine constraints with `,`** to layer shape rules: `??e?a,-s` = 5 letters, e in
  position 3, a in position 5, no letter s.
- **Reverse dictionary** for "what's that word…": `:a word that means fear of open spaces`.
  Natural-language concepts work, not just single words.
- **Synonyms as wordplay fuel**: `:begin` to get start/commence/initiate… for substitution
  in cryptics or transformation puzzles.
- **Acrostics**: `expand:` finds multiword phrases whose initials spell a target — handy for
  "the first letters spell…" metas.
- **Anagrams**: `//letters//` is simple and fast, but for anagram-with-extra-letters,
  nested chunks, or fixed partial order, prefer the `nutrimatic` skill's `<>` operator.

## Limitations vs Nutrimatic

- Pattern language is simpler (no full regex, no intersection of two arbitrary regexes, no
  complex/nested anagram grammar).
- Dictionary-based, so it lacks Nutrimatic's Wikipedia-scale proper nouns / catchphrases and
  its corpus-frequency ranking of "most natural" multi-word answers.
- Results depend on OneLook's semantic model; obscure or very specific concepts may be noisy.

Rule of thumb: **meaning → OneLook, shape/anagram/phrase-frequency → Nutrimatic.**
