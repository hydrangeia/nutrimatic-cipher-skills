#!/usr/bin/env python3
"""Identify what a mystery string probably is, and suggest which ciphers.py command to try.

Usage:
    python identify.py "the ciphertext"      # or pipe via stdin

It reports the character set, length, index of coincidence, and letter frequencies, then
prints ranked suggestions. This is a heuristic triage aid, not a decision: it narrows the
search space so you try the most likely transforms first. Follow its suggestions with the
matching `ciphers.py` command.
"""
import re
import sys
from collections import Counter

ENGLISH_FREQ = {
    'a': .0817, 'b': .0150, 'c': .0278, 'd': .0425, 'e': .1270, 'f': .0223,
    'g': .0202, 'h': .0609, 'i': .0697, 'j': .0015, 'k': .0077, 'l': .0403,
    'm': .0241, 'n': .0675, 'o': .0751, 'p': .0193, 'q': .0010, 'r': .0599,
    's': .0633, 't': .0906, 'u': .0276, 'v': .0098, 'w': .0236, 'x': .0015,
    'y': .0197, 'z': .0007,
}


def ic(letters):
    n = len(letters)
    if n < 2:
        return 0.0
    counts = Counter(letters)
    return sum(v * (v - 1) for v in counts.values()) / (n * (n - 1))


def main():
    text = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else sys.stdin.read()
    text = text.strip()
    raw = text
    lower = text.lower()
    letters = [c for c in lower if c.isalpha()]
    digits = [c for c in text if c.isdigit()]
    uniq = set(c for c in raw if not c.isspace())
    uniq_letters = set(letters)

    print("=" * 60)
    print(f"length: {len(raw)} chars   letters: {len(letters)}   digits: {len(digits)}")
    print(f"unique non-space symbols: {len(uniq)} -> {''.join(sorted(uniq))[:60]}")
    coincidence = ic(letters)
    print(f"index of coincidence: {coincidence:.4f}  "
          f"(English ~0.0667 | polyalphabetic/random ~0.0385)")
    if letters:
        counts = Counter(letters)
        top = '  '.join(f"{c}:{v}" for c, v in counts.most_common(8))
        print(f"top letters: {top}")
    print("=" * 60)

    suggestions = []

    # Binary
    if uniq <= set('01') and len(digits) >= 8:
        suggestions.append(("Binary (bits)", "ciphers.py frombin", 5))
    # Baconian: exactly two distinct letters/symbols, length multiple-ish of 5
    if len(uniq_letters) == 2 and len(letters) >= 10:
        suggestions.append(("Baconian (2-symbol, 5-bit groups)", "ciphers.py bacon", 5))
    if uniq <= set('AB') and len(raw.replace(' ', '')) % 5 == 0:
        suggestions.append(("Baconian A/B", "ciphers.py bacon", 5))
    # Morse
    if uniq <= set('.-/|_ ') and ('.' in uniq or '-' in uniq):
        suggestions.append(("Morse code", "ciphers.py morse", 5))
    # Hex
    if uniq_letters <= set('abcdef') and digits and len(uniq) > 2:
        suggestions.append(("Hexadecimal", "ciphers.py fromhex", 4))
    # Pure numbers
    if digits and not letters:
        maxnum = max((int(n) for n in re.findall(r'\d+', text)), default=0)
        if all(int(n) <= 26 for n in re.findall(r'\d+', text)) and re.findall(r'\d+', text):
            suggestions.append(("A1Z26 (1-26 -> letters)", "ciphers.py a1z26", 4))
        if set(''.join(digits)) <= set('12345'):
            suggestions.append(("Polybius / Tap code (digits 1-5)", "ciphers.py polybius  OR  tap", 4))
        if 32 <= maxnum <= 126:
            suggestions.append(("Decimal ASCII codes", "ciphers.py fromdec", 3))
        if set(''.join(re.findall(r'\d+', text))) <= set('234567890') and any(len(g) > 1 for g in re.findall(r'(\d)\1*', ''.join(digits))):
            suggestions.append(("Phone multi-tap / T9 (2-9)", "ciphers.py t9", 2))
    # Base64-ish
    if re.fullmatch(r'[A-Za-z0-9+/=\s]+', raw) and len(uniq_letters) > 6 and any(c.isupper() for c in raw) and any(c.islower() for c in raw):
        suggestions.append(("Base64 (mixed case + digits)", "ciphers.py frombase64", 2))

    # Letters-only. Caesar/atbash cost nothing, so always try them first regardless of
    # IC — IC is unreliable on short or atypical text (a pangram Caesar looks low-IC).
    if letters and len(uniq_letters) > 2:
        suggestions.append(
            ("Caesar / ROT / Atbash — cheap, always worth trying first",
             "ciphers.py caesar --all   then atbash", 4))
        short = len(letters) < 80
        if coincidence >= 0.055:
            suggestions.append(
                ("Monoalphabetic substitution (IC near English) — frequency analysis",
                 "ciphers.py freq   then affine --solve / substitution --key ...", 5))
        if coincidence <= 0.052:
            suggestions.append(
                ("Polyalphabetic / Vigenere (low IC) — auto-solve wants 150+ chars",
                 "ciphers.py vigenere --solve   (or --keylen N if short)", 5))
        if 0.052 < coincidence < 0.055 or short:
            suggestions.append(
                ("IC inconclusive (or text short) — try BOTH mono and poly",
                 "ciphers.py caesar --all   AND   vigenere --solve", 3))

    suggestions.sort(key=lambda t: -t[2])
    if not suggestions:
        print("No strong signal. Try: caesar --all, atbash, vigenere --solve, and inspect freq.")
        return
    print("Suggestions (most likely first):")
    for i, (what, how, _score) in enumerate(suggestions, 1):
        print(f"  {i}. {what}")
        print(f"       -> python ciphers.py {how.split('ciphers.py ',1)[-1]}"
              if how.startswith('ciphers.py') else f"       -> {how}")


if __name__ == '__main__':
    main()
