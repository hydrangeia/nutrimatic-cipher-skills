# nutrimatic-cipher-skills

Puzzle-hunt "crank-turning" tools, packaged as two [Claude Code](https://docs.claude.com/en/docs/claude-code) skills — but the cipher toolkit also runs as a plain Python CLI with **zero dependencies**, so teammates who don't use Claude can still use it.



---

## What's inside / 里面有什么

### 1. `nutrimatic` — word/phrase shape search
Builds [Nutrimatic](https://nutrimatic.org) pattern queries and the ready-to-open
`nutrimatic.org/2024/?q=...` URL. For fill-in-the-blank, anagrams, letter banks,
consonant/vowel shapes, and letter-drop / tile-reorder wordplay.
把解题约束翻译成 Nutrimatic 查询式并拼好 URL：填空、变位词、字母库、辅音元音形状、拆字重组。

### 2. `puzzle-ciphers` — classic cipher toolkit
- `scripts/identify.py` — paste a mystery string; it reports character set, length,
  index of coincidence, letter frequencies, and **suggests which ciphers to try**.
- `scripts/ciphers.py` — the transforms and brute-forcers.
  丢一串密文进 `identify.py` 分诊 → 按建议跑 `ciphers.py` 解。

Covered: Caesar / ROT13 / ROT47 / Atbash / affine (brute-force) / **Vigenère (auto-solve)** /
simple substitution / Morse / Baconian / A1Z26 / Polybius / tap code / rail fence /
base64 / base32 / hex / binary / decimal-ASCII / phone T9.

---

## Install / 安装

### As Claude Code skills / 作为 Claude 技能
Copy the two skill folders into your project's (or user-level) `.claude/skills/`:

```bash
git clone https://github.com/hydrangeia/nutrimatic-cipher-skills.git
cp -r nutrimatic-cipher-skills/skills/* /path/to/your-project/.claude/skills/
```

Then launch Claude Code from that project root — the skills auto-trigger when a task
looks like a word-search or an encoded string. 从该项目根目录启动 Claude Code 即可自动触发。

### As a standalone CLI / 当命令行工具（无需 Claude）
The cipher scripts are standard-library Python 3 only — nothing to install:

```bash
python skills/puzzle-ciphers/scripts/identify.py "PBATENGHYNGVBAF"
python skills/puzzle-ciphers/scripts/ciphers.py caesar --all "PBATENGHYNGVBAF"
python skills/puzzle-ciphers/scripts/ciphers.py list   # all commands
```

---

## Quick examples / 速览

```bash
# 不知道是什么密码？先分诊 (run from skills/puzzle-ciphers/scripts/)
$ python identify.py "gttuatiksktz"
  -> suggests monoalphabetic; then:
$ python ciphers.py caesar --all "gttuatiksktz"
  shift  6: announcement   <-- best

# Vigenère，连密钥都不知道（需 ~150+ 字符）
$ python ciphers.py vigenere --solve "<long ciphertext>"
  key len 4 -> key 'hunt': in cryptography a cipher is ...

# 一串点划
$ python ciphers.py morse ".- -. .- --. .-. .- --"   ->  anagram

# 多层套娃：base64 → rot13
$ python ciphers.py frombase64 "enJyZ25nenZxYXZ0dWc=" | ...
```

Full command help: `python ciphers.py <command> -h`.

---

## Demo / 实战演示

Real transcripts (these exact outputs are what the tools produce):

```text
# 捡到乱码 → identify 分诊 → 按建议解
$ python identify.py "PBATENGHYNGVBAF LBH SBHAQ GUR XRL"
  index of coincidence: 0.0443 ... Suggestions: Caesar / ROT / Atbash ...
$ python ciphers.py caesar --all "PBATENGHYNGVBAF LBH SBHAQ GUR XRL"
  shift 13: CONGRATULATIONS YOU FOUND THE KEY   <-- best

# Vigenère，未知密钥（需 ~150+ 字符）
$ python ciphers.py vigenere --solve "<long ciphertext>"
  key len 4 -> key 'hunt': in cryptography a cipher is an algorithm ...

# Playfair（已知关键词）
$ python ciphers.py playfair --key "playfair example" --encrypt "hidethegoldinthetreestump"
  bmodzbxdnabekudmuixmmouvif

# 多层套娃：base64 外层，里面是 ROT13
$ python ciphers.py frombase64 "enJyZ25nenZxYXZ0dWc="   ->  zrrgngzvqavtug
$ python ciphers.py caesar --all "zrrgngzvqavtug"        ->  meetatmidnight
```

Decoded plaintext is often itself the next instruction (e.g. Morse `.- -. .- --. .-. .- --`
→ `anagram` → hand it to the `nutrimatic` skill). Chain freely.

---

## Notes & limits / 说明与边界
- Brute-force output is ranked by chi-squared distance to English — a **heuristic**.
  Eyeball the top few, especially on short strings (< ~40 letters). 结果按"像英语"排序，是启发式。
- `vigenere --solve` wants ~150+ letters; for short text pass `--keylen N` or a known key.
- General substitution (26! keys) can't be brute-forced — use `freq` + human word-fitting.
- Not built in (hand-solve, see `references/cipher-guide.md`): Playfair, columnar
  transposition, Bifid/Trifid/ADFGVX, book/running-key, keyboard shifts.
- Out of scope: modern crypto (AES/RSA), stego, pure-logic puzzles.

## Credits / 致谢
Nutrimatic is by **Dan Egnor** — the tool, corpus, and hosted service live at
[nutrimatic.org](https://nutrimatic.org) ([source](https://github.com/egnor/nutrimatic)).
This repo only documents its query syntax and helps build queries; it does not redistribute
Nutrimatic itself.

## License / 许可证
[MIT](LICENSE).
