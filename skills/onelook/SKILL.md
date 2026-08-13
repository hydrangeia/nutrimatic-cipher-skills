---
name: onelook
description: >-
  Build OneLook (onelook.com) queries and the ready-to-open search URL for finding words by
  MEANING, by spelling shape, or both at once — the semantic counterpart to the `nutrimatic`
  skill. Use this whenever a puzzle needs a word/phrase identified from its definition or
  concept rather than only its shape: crossword and cryptic clues ("a 6-letter word meaning
  reluctant"), reverse-dictionary lookups ("what's the word for the fear of X"), synonyms /
  related concepts, "a word that means Y and starts with BL", rhymes, or acrostics /
  first-letter phrases. Trigger this even when the user doesn't say "onelook" — any request
  combining a MEANING with a letter pattern, or asking "what word means…", should use it.
  Reach for `nutrimatic` instead when the task is pure shape/anagram/phrase-frequency with no
  meaning involved. Produces a OneLook query plus the https://www.onelook.com/?w=... URL.
---

# OneLook query builder

OneLook searches ~805 dictionaries plus a semantic engine. Its superpower — which
`nutrimatic` lacks — is finding words by **meaning**, and combining meaning with a spelling
pattern in one query. Use it for the "I know what it means and roughly its shape" half of
word puzzles; use `nutrimatic` for the "I only know the shape / it's an anagram / I want the
most natural phrase from a big corpus" half. They are complementary — good solvers reach for
both.

## How to use this skill

1. Translate the solver's need into a OneLook query (syntax below). The key move is deciding
   whether it's **meaning** (`:concept`), **shape** (`pattern`), or **both** (`pattern:concept`).
2. Emit the query **and** a clickable URL: `https://www.onelook.com/?w=<url-encoded query>`.
3. If the user wants results inline, fetch that URL and report the top words (note: OneLook
   is JS-rendered, so a plain fetch may return little — prefer giving the URL, or use a
   browser tool).
4. Explain what OneLook can't pin down (it won't rank by phrase frequency like Nutrimatic,
   and its pattern language is simpler), and when to cross over to the `nutrimatic` skill.

For the full spec and worked examples, read [references/syntax.md](references/syntax.md).

## Cheat sheet — query syntax

| Token | Means |
|-------|-------|
| `?` | any one letter |
| `*` | any number of letters (incl. zero) |
| `#` | a consonant |
| `@` | a vowel |
| `-abcd` | disallow these letters |
| `+abcd` | restrict to only these letters |
| `//abcd//` | unscramble / anagram of these letters |
| `:meaning` | words **related to a concept/meaning** (reverse dictionary / thesaurus) |
| `pattern:meaning` | words matching the spelling `pattern` **and** related to `meaning` |
| `**word**` | phrases that **contain** `word` |
| `expand:nasa` | phrases that spell out the acrostic n.a.s.a. |
| `,` | separate multiple constraints, all must hold (AND) |

## Recipe patterns (need → query)

- **Word meaning X, N letters**: `?????:reluctant` (5-letter word meaning reluctant).
- **Meaning X, starts with BL**: `bl*:snow`.
- **Pure reverse dictionary** ("what's the word for…"): `:the fear of heights`.
- **Known letters + meaning**: `c##v?:persuade` (c, two consonants, a vowel, any, meaning persuade).
- **Anagram of some letters, and a meaning**: `//listen//` (anagram) — combine with a concept
  if helpful: `//listen//:hear` (rarely needed, but valid).
- **Synonyms / related words** for wordplay substitution: `:happy`.
- **Phrases containing a word**: `**winter**`.
- **Acrostic / first letters spell something**: `expand:hint`.
- **Two constraints at once**: `?????,*y*:color` (5 letters, contains a y, meaning color).

## URL construction

- Base: `https://www.onelook.com/?w=`
- Append the **URL-encoded** query. Notably encode: `*`→`%2A`, `:`→`%3A`, `#`→`%23`,
  `@`→`%40`, `+`→`%2B`, `//`→`%2F%2F`, `,`→`%2C`, space→`%20`.
- Example: query `bl*:snow` → `https://www.onelook.com/?w=bl%2A%3Asnow`

## When to use OneLook vs Nutrimatic

- **OneLook** (this skill): the word's **meaning** matters — clues, definitions, synonyms,
  reverse lookup, meaning+shape combos, acrostics.
- **`nutrimatic`**: pure shape, complex/nested anagrams (`<>`, `&`), or "the most natural
  multi-word phrase from a Wikipedia-sized corpus, ranked by frequency."

Decoded/clued fragments often bounce between the two — hand shapes to `nutrimatic`, meanings
to OneLook.

## Advanced (optional)

OneLook's word engine is powered by the free **Datamuse API** (`api.datamuse.com`, no key,
CORS-enabled) — e.g. `sp=` spelled-like, `ml=` means-like, `sl=` sounds-like, `rel_rhy=`
rhymes, `rel_syn=` synonyms. Mention it only if the user wants programmatic/bulk queries;
this skill itself stays URL-based and dependency-free.
