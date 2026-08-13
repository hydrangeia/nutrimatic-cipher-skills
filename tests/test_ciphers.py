"""Self-tests for ciphers.py — run via `python -m unittest` from the repo root.

These drive the real command-line interface via subprocess, so they verify exactly what a
user (or the skill) invokes. Known-answer vectors are from standard references.
"""
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "skills", "puzzle-ciphers", "scripts", "ciphers.py")


def run(*args, stdin=None):
    out = subprocess.run(
        [sys.executable, SCRIPT, *args],
        input=stdin, capture_output=True, text=True,
    )
    assert out.returncode == 0, f"{args} failed:\n{out.stderr}"
    return out.stdout.strip()


class TestCiphers(unittest.TestCase):
    def test_caesar_all_ranks_english_first(self):
        self.assertIn("announcement", run("caesar", "--all", "gttuatiksktz").splitlines()[0])

    def test_atbash(self):
        self.assertEqual(run("atbash", "svool"), "hello")

    def test_rot13_roundtrip(self):
        self.assertEqual(run("rot13", run("rot13", "Hello, World!")), "Hello, World!")

    def test_vigenere_roundtrip(self):
        ct = run("vigenere", "--key", "lemon", "--encrypt", "attackatdawn")
        self.assertEqual(run("vigenere", "--key", "lemon", ct), "attackatdawn")

    def test_affine_solve(self):
        ct = run("affine", "--encrypt", "--a", "5", "--b", "8", "attackatdawnthisisalongertext")
        self.assertIn("attackatdawn", run("affine", "--solve", ct).splitlines()[0])

    def test_morse_decode(self):
        self.assertEqual(run("morse", ".... . .-.. .-.. ---"), "hello")

    def test_bacon_classic(self):
        # 24-letter (classic) line should decode to hello
        self.assertIn("hello", run("bacon", "AABBB AABAA ABABA ABABA ABBAB"))

    def test_a1z26(self):
        self.assertEqual(run("a1z26", "8 5 12 12 15"), "hello")

    def test_polybius_roundtrip(self):
        enc = run("polybius", "--encode", "hello")
        self.assertEqual(run("polybius", enc), "hello")

    def test_railfence_roundtrip(self):
        enc = run("railfence", "--rails", "3", "--encode", "--strip", "WEAREDISCOVEREDFLEEATONCE")
        self.assertEqual(run("railfence", "--rails", "3", enc), "WEAREDISCOVEREDFLEEATONCE")

    def test_playfair_known_vector(self):
        ct = run("playfair", "--key", "playfair example", "--encrypt", "hidethegoldinthetreestump")
        self.assertEqual(ct, "bmodzbxdnabekudmuixmmouvif")

    def test_columnar_known_vector(self):
        ct = run("columnar", "--key", "ZEBRAS", "--encrypt", "WEAREDISCOVEREDFLEEATONCE")
        self.assertEqual(ct, "EVLNACDTESEAROFODEECWIREE")
        self.assertEqual(run("columnar", "--key", "ZEBRAS", ct), "WEAREDISCOVEREDFLEEATONCE")

    def test_keyboard_roundtrip(self):
        enc = run("keyboard", "--shift", "1", "--direction", "right", "hello world")
        self.assertEqual(run("keyboard", "--shift", "1", "--direction", "left", enc), "hello world")

    def test_base_decodes(self):
        self.assertEqual(run("frombin", "01001000 01001001"), "HI")
        self.assertEqual(run("fromhex", "48 49"), "HI")
        self.assertEqual(run("frombase64", "aGVsbG8="), "hello")


if __name__ == "__main__":
    unittest.main()
