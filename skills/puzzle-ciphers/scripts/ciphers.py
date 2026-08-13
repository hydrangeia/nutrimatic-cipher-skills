#!/usr/bin/env python3
"""Classic-cipher toolkit for puzzle hunts. Standard library only.

Every command reads its text from the positional args (joined by spaces) or, if none
are given, from stdin. Output goes to stdout. Run `python ciphers.py <cmd> -h` for a
command's options, or `python ciphers.py list` for the full command list.

Design notes for the model driving this:
- Brute-force commands (caesar --all, affine --solve, vigenere --solve) rank candidates
  by chi-squared distance to English letter frequencies (lower = more English-like).
  Ranking is a heuristic; always eyeball the top few, don't blindly take rank 1.
- Transforms that lose non-letters (vigenere, affine, substitution) operate on letters
  only and return letters only. Caesar/atbash/rot preserve case and pass punctuation through.
"""
import argparse
import string
import sys
from collections import Counter

# ---------------------------------------------------------------------------
# English scoring
# ---------------------------------------------------------------------------
ENGLISH_FREQ = {
    'a': .0817, 'b': .0150, 'c': .0278, 'd': .0425, 'e': .1270, 'f': .0223,
    'g': .0202, 'h': .0609, 'i': .0697, 'j': .0015, 'k': .0077, 'l': .0403,
    'm': .0241, 'n': .0675, 'o': .0751, 'p': .0193, 'q': .0010, 'r': .0599,
    's': .0633, 't': .0906, 'u': .0276, 'v': .0098, 'w': .0236, 'x': .0015,
    'y': .0197, 'z': .0007,
}


def only_letters(s):
    return [c for c in s.lower() if c.isalpha() and c in ENGLISH_FREQ]


def chi2(s):
    """Chi-squared distance from English letter frequencies. Lower is more English."""
    letters = only_letters(s)
    n = len(letters)
    if n == 0:
        return float('inf')
    counts = Counter(letters)
    total = 0.0
    for c, freq in ENGLISH_FREQ.items():
        expected = freq * n
        observed = counts.get(c, 0)
        total += (observed - expected) ** 2 / expected
    return total


def index_of_coincidence(s):
    letters = only_letters(s)
    n = len(letters)
    if n < 2:
        return 0.0
    counts = Counter(letters)
    return sum(v * (v - 1) for v in counts.values()) / (n * (n - 1))


# ---------------------------------------------------------------------------
# Monoalphabetic shifts
# ---------------------------------------------------------------------------
def shift_text(text, k):
    """Shift each letter forward by k, preserving case and non-letters."""
    out = []
    for c in text:
        if c.isupper():
            out.append(chr((ord(c) - 65 + k) % 26 + 65))
        elif c.islower():
            out.append(chr((ord(c) - 97 + k) % 26 + 97))
        else:
            out.append(c)
    return ''.join(out)


def cmd_caesar(args):
    text = get_text(args)
    if args.all:
        cands = []
        for k in range(26):
            dec = shift_text(text, -k)  # decrypt: undo a +k Caesar
            cands.append((chi2(dec), k, dec))
        cands.sort(key=lambda t: t[0])
        for score, k, dec in cands:
            marker = '  <-- best' if (score, k, dec) == cands[0] else ''
            print(f"shift {k:2d} (chi2 {score:7.1f}): {dec}{marker}")
    else:
        print(shift_text(text, args.shift))


def cmd_rot13(args):
    print(shift_text(get_text(args), 13))


def cmd_rot47(args):
    text = get_text(args)
    out = []
    for c in text:
        o = ord(c)
        if 33 <= o <= 126:
            out.append(chr(33 + (o - 33 + 47) % 94))
        else:
            out.append(c)
    print(''.join(out))


def cmd_atbash(args):
    text = get_text(args)
    out = []
    for c in text:
        if c.isupper():
            out.append(chr(90 - (ord(c) - 65)))
        elif c.islower():
            out.append(chr(122 - (ord(c) - 97)))
        else:
            out.append(c)
    print(''.join(out))


# ---------------------------------------------------------------------------
# Affine
# ---------------------------------------------------------------------------
COPRIME_26 = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
INV_26 = {a: pow(a, -1, 26) for a in COPRIME_26}


def affine_decrypt(text, a, b):
    ainv = INV_26[a]
    out = []
    for c in only_letters(text):
        y = ord(c) - 97
        out.append(chr(ainv * (y - b) % 26 + 97))
    return ''.join(out)


def affine_encrypt(text, a, b):
    out = []
    for c in only_letters(text):
        x = ord(c) - 97
        out.append(chr((a * x + b) % 26 + 97))
    return ''.join(out)


def cmd_affine(args):
    text = get_text(args)
    if args.solve:
        cands = []
        for a in COPRIME_26:
            for b in range(26):
                dec = affine_decrypt(text, a, b)
                cands.append((chi2(dec), a, b, dec))
        cands.sort(key=lambda t: t[0])
        for score, a, b, dec in cands[:args.top]:
            print(f"a={a:2d} b={b:2d} (chi2 {score:7.1f}): {dec}")
    elif args.encrypt:
        print(affine_encrypt(text, args.a, args.b))
    else:
        print(affine_decrypt(text, args.a, args.b))


# ---------------------------------------------------------------------------
# Vigenere
# ---------------------------------------------------------------------------
def vigenere_decrypt(text, key):
    key = [ord(k) - 97 for k in key.lower() if k.isalpha()]
    if not key:
        return ''
    out, i = [], 0
    for c in only_letters(text):
        out.append(chr((ord(c) - 97 - key[i % len(key)]) % 26 + 97))
        i += 1
    return ''.join(out)


def vigenere_encrypt(text, key):
    key = [ord(k) - 97 for k in key.lower() if k.isalpha()]
    if not key:
        return ''
    out, i = [], 0
    for c in only_letters(text):
        out.append(chr((ord(c) - 97 + key[i % len(key)]) % 26 + 97))
        i += 1
    return ''.join(out)


def best_shift_for_column(col):
    """Return the shift (0-25) whose decryption of `col` best matches English."""
    best_k, best_score = 0, float('inf')
    for k in range(26):
        dec = ''.join(chr((ord(c) - 97 - k) % 26 + 97) for c in col)
        s = chi2(dec)
        if s < best_score:
            best_score, best_k = s, k
    return best_k


def cmd_vigenere(args):
    text = get_text(args)
    if args.solve:
        letters = only_letters(text)
        # Rank likely key lengths by average column IC (English mono ~0.066).
        ranked = []
        for L in range(1, args.maxlen + 1):
            cols = [letters[i::L] for i in range(L)]
            ics = [index_of_coincidence(''.join(col)) for col in cols if len(col) > 1]
            avg = sum(ics) / len(ics) if ics else 0.0
            ranked.append((avg, L))
        ranked.sort(key=lambda t: -t[0])
        print("Likely key lengths (by avg column IC, English mono ~0.066):")
        for avg, L in ranked[:8]:
            print(f"  len {L:2d}: IC {avg:.4f}")
        Ls = [L for _, L in ranked[:args.tries]] if args.tries else [ranked[0][1]]
        if args.keylen:
            Ls = [args.keylen]
        print()
        for L in Ls:
            cols = [letters[i::L] for i in range(L)]
            key = ''.join(chr(best_shift_for_column(col) + 97) for col in cols)
            dec = vigenere_decrypt(text, key)
            print(f"key len {L} -> key '{key}' (chi2 {chi2(dec):.1f}): {dec}")
    elif args.encrypt:
        print(vigenere_encrypt(text, args.key))
    else:
        print(vigenere_decrypt(text, args.key))


# ---------------------------------------------------------------------------
# Simple substitution helpers
# ---------------------------------------------------------------------------
def cmd_substitution(args):
    text = get_text(args)
    key = args.key.lower()
    if len(key) != 26:
        sys.exit("--key must be exactly 26 letters (the cipher alphabet a->key[0] ... z->key[25])")
    table = {chr(97 + i): key[i] for i in range(26)}
    out = []
    for c in text:
        low = c.lower()
        if low in table:
            m = table[low]
            out.append(m.upper() if c.isupper() else m)
        else:
            out.append(c)
    print(''.join(out))


def cmd_freq(args):
    text = get_text(args)
    letters = only_letters(text)
    n = len(letters)
    counts = Counter(letters)
    print(f"letters: {n}   unique: {len(counts)}   IC: {index_of_coincidence(text):.4f} "
          f"(English ~0.0667, random ~0.0385)")
    print("freq (most common first):")
    for c, v in counts.most_common():
        pct = 100 * v / n if n else 0
        bar = '#' * int(pct)
        print(f"  {c}: {v:4d}  {pct:5.1f}%  {bar}")


# ---------------------------------------------------------------------------
# Morse
# ---------------------------------------------------------------------------
MORSE = {
    'a': '.-', 'b': '-...', 'c': '-.-.', 'd': '-..', 'e': '.', 'f': '..-.',
    'g': '--.', 'h': '....', 'i': '..', 'j': '.---', 'k': '-.-', 'l': '.-..',
    'm': '--', 'n': '-.', 'o': '---', 'p': '.--.', 'q': '--.-', 'r': '.-.',
    's': '...', 't': '-', 'u': '..-', 'v': '...-', 'w': '.--', 'x': '-..-',
    'y': '-.--', 'z': '--..', '0': '-----', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.',
}
MORSE_REV = {v: k for k, v in MORSE.items()}


def cmd_morse(args):
    text = get_text(args)
    if args.encode:
        out = []
        for c in text.lower():
            if c in MORSE:
                out.append(MORSE[c])
            elif c == ' ':
                out.append('/')
        print(' '.join(out))
    else:
        # Decode. Word breaks: '/' or double-space or '|'. Letter breaks: single space.
        text = text.replace('|', '/').replace('  ', ' / ')
        words = []
        for word in text.split('/'):
            letters = [MORSE_REV.get(tok, '?') for tok in word.split() if tok]
            if letters:
                words.append(''.join(letters))
        print(' '.join(words))


# ---------------------------------------------------------------------------
# Baconian
# ---------------------------------------------------------------------------
def _bacon_24():
    table = {}
    letters = "abcdefghiklmnopqrstuvwxyz"  # classic: i=j, u=v collapsed
    order = ['abcdefgh', 'iklmnopq', 'rstuwxyz']  # not used; build directly below
    # Classic Bacon table (24 letters, i/j and u/v share a code):
    seq = "abcdefghi klmnopqrstu wxyz".replace(" ", "")
    codes = ['{:05b}'.format(i).replace('0', 'A').replace('1', 'B') for i in range(24)]
    for ch, code in zip(seq, codes):
        table[code] = ch
    # aliases
    table_out = dict(table)
    return table_out


def cmd_bacon(args):
    text = get_text(args)
    # Normalize to A/B: treat one of two symbol classes as A. Accept AB, ab, 01.
    raw = [c for c in text if not c.isspace()]
    ab = []
    for c in raw:
        if c in 'Aa0':
            ab.append('A')
        elif c in 'Bb1':
            ab.append('B')
        # ignore other chars
    bits = ''.join(ab)
    groups = [bits[i:i + 5] for i in range(0, len(bits) - len(bits) % 5, 5)]

    def decode(map26):
        return ''.join(map26.get(g, '?') for g in groups)

    map26 = {'{:05b}'.format(i).replace('0', 'A').replace('1', 'B'): chr(97 + i)
             for i in range(26)}
    map24 = _bacon_24()
    print(f"bits ({len(bits)}), {len(groups)} groups")
    print(f"26-letter (a=AAAAA..z): {decode(map26)}")
    print(f"24-letter (classic, i=j,u=v): {decode(map24)}")


# ---------------------------------------------------------------------------
# A1Z26 / letter-number
# ---------------------------------------------------------------------------
def cmd_a1z26(args):
    text = get_text(args)
    if args.encode:
        out = [str(ord(c) - 96) for c in text.lower() if c.isalpha()]
        print(' '.join(out))
    else:
        import re
        nums = re.findall(r'\d+', text)
        out = []
        for n in nums:
            v = int(n)
            out.append(chr(96 + v) if 1 <= v <= 26 else '?')
        print(''.join(out))


# ---------------------------------------------------------------------------
# Polybius square / tap code
# ---------------------------------------------------------------------------
def build_square(alphabet):
    size = int(round(len(alphabet) ** 0.5))
    pos = {}
    rev = {}
    for i, ch in enumerate(alphabet):
        r, c = divmod(i, size)
        pos[ch] = (r + 1, c + 1)
        rev[(r + 1, c + 1)] = ch
    return pos, rev, size


def cmd_polybius(args):
    text = get_text(args)
    alphabet = args.square.lower() if args.square else "abcdefghiklmnopqrstuvwxyz"  # no j
    pos, rev, size = build_square(alphabet)
    if args.encode:
        out = []
        for c in text.lower():
            cc = 'i' if (c == 'j' and 'j' not in pos) else c
            if cc in pos:
                r, col = pos[cc]
                out.append(f"{r}{col}")
        print(' '.join(out))
    else:
        import re
        digits = re.findall(r'[1-%d]' % size, text)
        pairs = [digits[i:i + 2] for i in range(0, len(digits) - len(digits) % 2, 2)]
        out = [rev.get((int(a), int(b)), '?') for a, b in pairs]
        print(''.join(out))


TAP_ALPHABET = "abcdefghijlmnopqrstuvwxyz"  # no k (k -> c)


def cmd_tap(args):
    text = get_text(args)
    import re
    pos, rev, size = build_square(TAP_ALPHABET)
    nums = re.findall(r'\d+', text)
    if args.encode:
        out = []
        for c in text.lower():
            cc = 'c' if c == 'k' else c
            if cc in pos:
                r, col = pos[cc]
                out.append('.' * r + ' ' + '.' * col)
        print('  '.join(out))
    else:
        # Tap values are always 1-5, so read individual digits and pair them. This
        # accepts both "2 3 1 5" (separate bursts) and "23 15" (glued pairs).
        vals = [int(d) for d in re.findall(r'[1-5]', text)]
        pairs = [vals[i:i + 2] for i in range(0, len(vals) - len(vals) % 2, 2)]
        out = [rev.get((a, b), '?') for a, b in pairs]
        print(''.join(out))


# ---------------------------------------------------------------------------
# Rail fence
# ---------------------------------------------------------------------------
def cmd_railfence(args):
    text = get_text(args)
    n = args.rails
    s = ''.join(text.split()) if args.strip else text
    if n < 2:
        print(s)
        return
    if args.encode:
        rows = [''] * n
        r, d = 0, 1
        for c in s:
            rows[r] += c
            if r == 0:
                d = 1
            elif r == n - 1:
                d = -1
            r += d
        print(''.join(rows))
    else:
        # Build the zigzag rail pattern, fill each rail from the ciphertext (which was
        # read rail-by-rail), then walk the zigzag popping from the matching rail.
        from collections import deque
        pattern = []
        r, d = 0, 1
        for _ in range(len(s)):
            pattern.append(r)
            if r == 0:
                d = 1
            elif r == n - 1:
                d = -1
            r += d
        counts = Counter(pattern)
        it = iter(s)
        rails = {row: deque(next(it) for _ in range(counts.get(row, 0))) for row in range(n)}
        out = [rails[row].popleft() for row in pattern]
        print(''.join(out))


# ---------------------------------------------------------------------------
# Bases / numeric
# ---------------------------------------------------------------------------
def cmd_frombin(args):
    text = get_text(args)
    import re
    chunks = re.findall(r'[01]+', text)
    if len(chunks) == 1 and len(chunks[0]) % 8 == 0:
        chunks = [chunks[0][i:i + 8] for i in range(0, len(chunks[0]), 8)]
    print(''.join(chr(int(b, 2)) for b in chunks if b))


def cmd_fromhex(args):
    text = get_text(args)
    import re
    hexstr = ''.join(re.findall(r'[0-9a-fA-F]', text))
    if len(hexstr) % 2:
        hexstr = hexstr[:-1]
    print(bytes.fromhex(hexstr).decode('latin-1'))


def cmd_frombase64(args):
    import base64
    text = ''.join(get_text(args).split())
    text += '=' * (-len(text) % 4)
    print(base64.b64decode(text).decode('latin-1', 'replace'))


def cmd_frombase32(args):
    import base64
    text = ''.join(get_text(args).split()).upper()
    text += '=' * (-len(text) % 8)
    print(base64.b32decode(text).decode('latin-1', 'replace'))


def cmd_fromdec(args):
    """Space/comma separated decimal numbers -> ASCII characters."""
    text = get_text(args)
    import re
    nums = [int(n) for n in re.findall(r'\d+', text)]
    print(''.join(chr(n) for n in nums if 0 < n < 0x110000))


# ---------------------------------------------------------------------------
# T9 / phone multi-tap
# ---------------------------------------------------------------------------
T9 = {'2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl', '6': 'mno',
      '7': 'pqrs', '8': 'tuv', '9': 'wxyz'}


def cmd_t9(args):
    """Decode phone multi-tap: groups of one repeated digit -> a letter. 0 or space = gap."""
    text = get_text(args)
    import re
    out = []
    for group in re.split(r'[ ,\-/]+', text.strip()):
        if not group:
            continue
        if set(group) == {'0'}:
            out.append(' ')
            continue
        d = group[0]
        if d in T9 and all(ch == d for ch in group):
            letters = T9[d]
            out.append(letters[(len(group) - 1) % len(letters)])
        else:
            out.append('?')
    print(''.join(out))


# ---------------------------------------------------------------------------
# dispatch
# ---------------------------------------------------------------------------
def get_text(args):
    if getattr(args, 'text', None):
        return ' '.join(args.text)
    data = sys.stdin.read()
    return data.rstrip('\n')


def cmd_list(args):
    print(__doc__)
    print("Commands: caesar, rot13, rot47, atbash, affine, vigenere, substitution, freq,")
    print("          morse, bacon, a1z26, polybius, tap, railfence, frombin, fromhex,")
    print("          frombase64, frombase32, fromdec, t9")


def build_parser():
    p = argparse.ArgumentParser(description="Classic-cipher toolkit for puzzle hunts.")
    sub = p.add_subparsers(dest='cmd', required=True)

    def add_text(sp):
        sp.add_argument('text', nargs='*', help="text (or pipe via stdin)")

    sp = sub.add_parser('list', help="show all commands"); sp.set_defaults(func=cmd_list)

    sp = sub.add_parser('caesar', help="Caesar shift; --all tries all 26 ranked by English-ness")
    sp.add_argument('--shift', type=int, default=0, help="shift letters forward by N")
    sp.add_argument('--all', action='store_true', help="try all 26 decrypt shifts, ranked")
    add_text(sp); sp.set_defaults(func=cmd_caesar)

    sp = sub.add_parser('rot13'); add_text(sp); sp.set_defaults(func=cmd_rot13)
    sp = sub.add_parser('rot47'); add_text(sp); sp.set_defaults(func=cmd_rot47)
    sp = sub.add_parser('atbash'); add_text(sp); sp.set_defaults(func=cmd_atbash)

    sp = sub.add_parser('affine', help="affine cipher; --solve brute-forces all keys")
    sp.add_argument('--a', type=int, default=1); sp.add_argument('--b', type=int, default=0)
    sp.add_argument('--encrypt', action='store_true')
    sp.add_argument('--solve', action='store_true')
    sp.add_argument('--top', type=int, default=5)
    add_text(sp); sp.set_defaults(func=cmd_affine)

    sp = sub.add_parser('vigenere', help="Vigenere; --solve estimates key via IC + chi2")
    sp.add_argument('--key', default='')
    sp.add_argument('--encrypt', action='store_true')
    sp.add_argument('--solve', action='store_true')
    sp.add_argument('--maxlen', type=int, default=20, help="max key length to test in --solve")
    sp.add_argument('--keylen', type=int, default=0, help="force a specific key length")
    sp.add_argument('--tries', type=int, default=3, help="how many top key-lengths to decrypt")
    add_text(sp); sp.set_defaults(func=cmd_vigenere)

    sp = sub.add_parser('substitution', help="apply a 26-letter substitution key a->key[0]..")
    sp.add_argument('--key', required=True)
    add_text(sp); sp.set_defaults(func=cmd_substitution)

    sp = sub.add_parser('freq', help="letter frequency + index of coincidence")
    add_text(sp); sp.set_defaults(func=cmd_freq)

    sp = sub.add_parser('morse', help="Morse; default decode, --encode to encode")
    sp.add_argument('--encode', action='store_true'); add_text(sp); sp.set_defaults(func=cmd_morse)

    sp = sub.add_parser('bacon', help="Baconian decode (prints both 24- and 26-letter)")
    add_text(sp); sp.set_defaults(func=cmd_bacon)

    sp = sub.add_parser('a1z26', help="1=a..26=z; default decode, --encode to encode")
    sp.add_argument('--encode', action='store_true'); add_text(sp); sp.set_defaults(func=cmd_a1z26)

    sp = sub.add_parser('polybius', help="Polybius square (default 5x5, i/j merged, no j)")
    sp.add_argument('--encode', action='store_true')
    sp.add_argument('--square', default='', help="custom alphabet (25 or 36 chars) filling the grid")
    add_text(sp); sp.set_defaults(func=cmd_polybius)

    sp = sub.add_parser('tap', help="Tap code (5x5, no k; k->c). Pairs of tap counts.")
    sp.add_argument('--encode', action='store_true'); add_text(sp); sp.set_defaults(func=cmd_tap)

    sp = sub.add_parser('railfence', help="Rail fence; default decode, --encode to encode")
    sp.add_argument('--rails', type=int, required=True)
    sp.add_argument('--encode', action='store_true')
    sp.add_argument('--strip', action='store_true', help="strip spaces before processing")
    add_text(sp); sp.set_defaults(func=cmd_railfence)

    sp = sub.add_parser('frombin', help="binary -> text"); add_text(sp); sp.set_defaults(func=cmd_frombin)
    sp = sub.add_parser('fromhex', help="hex -> text"); add_text(sp); sp.set_defaults(func=cmd_fromhex)
    sp = sub.add_parser('frombase64', help="base64 -> text"); add_text(sp); sp.set_defaults(func=cmd_frombase64)
    sp = sub.add_parser('frombase32', help="base32 -> text"); add_text(sp); sp.set_defaults(func=cmd_frombase32)
    sp = sub.add_parser('fromdec', help="decimal ASCII codes -> text"); add_text(sp); sp.set_defaults(func=cmd_fromdec)
    sp = sub.add_parser('t9', help="phone multi-tap decode"); add_text(sp); sp.set_defaults(func=cmd_t9)

    return p


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
