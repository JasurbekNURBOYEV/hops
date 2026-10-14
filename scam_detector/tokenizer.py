"""
tokenizer.py — text → features for the scam detector (copied from job_detector, keep the two in sync).

Scam messages hide from filters by mixing scripts ("ρaҕoτa" = "работа"), using
small caps / Coptic / math symbols as letters, letter O as zero ("2O 5OO"),
emoji-only layouts and zero-width padding. This module folds all of that back
to plain Cyrillic/Latin words and adds a few structural features.
"""
from __future__ import annotations

import re
import unicodedata

# ── Lookalike characters → Cyrillic ──────────────────────────────────────────
# Applied only to tokens that contain at least one Cyrillic-looking character,
# so plain English words are left alone.
_TO_CYR = {
    # Latin
    "a": "а", "b": "в", "c": "с", "e": "е", "h": "н", "k": "к", "m": "м", "n": "п",
    "o": "о", "p": "р", "r": "г", "t": "т", "u": "и", "x": "х", "y": "у",
    "ú": "й", "ù": "й", "é": "е", "ë": "ё",
    # Greek
    "α": "а", "β": "в", "δ": "б", "ε": "е", "η": "н", "ι": "і", "κ": "к",
    "λ": "л", "μ": "м", "ν": "у", "ο": "о", "π": "п", "ρ": "р", "σ": "о", "ς": "с",
    "τ": "т", "υ": "и", "φ": "ф", "χ": "х", "ω": "ш", "γ": "г",
    # Small caps / IPA / Coptic / misc letter-like symbols
    "ᴀ": "а", "ʙ": "в", "ᴄ": "с", "ᴅ": "д", "ᴇ": "е", "ɢ": "г", "ʜ": "н", "ɪ": "і",
    "ᴋ": "к", "ʟ": "л", "ᴍ": "м", "ɴ": "н", "ᴏ": "о", "ᴘ": "р", "ᴩ": "р", "ʀ": "я",
    "ᴛ": "т", "ᴜ": "и", "ᴡ": "ш", "ʏ": "у", "ᴢ": "з", "ᴦ": "г", "ᴨ": "п", "ᴧ": "л",
    "ᴫ": "л", "ᴎ": "и", "ʍ": "м", "ɑ": "а", "ϲ": "с", "ⲗ": "л", "ⲙ": "м", "ⲇ": "д",
    "ⲏ": "н", "ⲟ": "о", "ⲣ": "р", "ⲧ": "т", "ⲩ": "у", "ⲭ": "х",
    "ҕ": "б", "ү": "у", "ұ": "у", "қ": "к", "ӄ": "к", "ң": "н", "ө": "о", "һ": "н",
    "ⲁ": "а", "ʒ": "з", "ɯ": "ш", "պ": "щ", "á": "а", "à": "а", "ó": "о", "ò": "о",
    "ℂ": "с", "ℍ": "н", "ℕ": "п", "ℙ": "р",
}
# Math symbols used as letters — they are not word characters, so replace them up front.
_SYMBOL_LETTERS = str.maketrans({"∂": "д", "∏": "п", "∩": "п", "∆": "д"})
_CYR_HINTS = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюяі") | set(_TO_CYR) - set("abcehkmnoprtuxyúùéë")

_INVISIBLE = re.compile(r"[​-‏⁠-⁤﻿︀-️⃣­]")
_URL       = re.compile(r"(?:https?://)?(?:www\.)?((?:[a-z0-9-]+\.)+[a-z]{2,})(/[^\s]*)?", re.I)
_WORD      = re.compile(r"[^\W_]+")
_ZERO_O    = re.compile(r"(?<=\d)[oо]|[oо](?=\d)")


def _script(ch: str) -> str:
    if ch.isdigit():
        return "digit"
    name = unicodedata.name(ch, "")
    for s in ("LATIN", "CYRILLIC", "GREEK", "COPTIC"):
        if name.startswith(s):
            return s
    return "other"


def _is_emoji(ch: str) -> bool:
    return unicodedata.category(ch) == "So" or 0x1F000 <= ord(ch) <= 0x1FAFF


def _fold_word(word: str) -> str:
    if any(c in _CYR_HINTS for c in word):
        return "".join(_TO_CYR.get(c, c) for c in word)
    return word


def _url_features(text: str) -> tuple[str, list[str]]:
    feats = []
    def repl(m: re.Match) -> str:
        domain = m.group(1).lower()
        path = (m.group(2) or "").lower()
        feats.append("__url__")
        feats.append(f"__domain_{domain}__")
        if domain == "t.me" and path.startswith("/m/"):
            feats.append("__tme_m__")
        return " "
    return _URL.sub(repl, text), feats


def tokenize(text: str) -> list[str]:
    feats = ["__zero_width__"] if re.search(r"[\u200b-\u200f\u2060-\u2064\ufeff]", text) else []
    text = unicodedata.normalize("NFKC", _INVISIBLE.sub("", text))
    text, url_feats = _url_features(text)
    feats += url_feats
    text = text.lower().translate(_SYMBOL_LETTERS)

    emoji = [c for c in text if _is_emoji(c)]
    feats += [f"__emoji_{c}__" for c in set(emoji)]
    if len(set(emoji)) >= 3:
        feats.append("__many_emoji__")
    if len(emoji) >= 10 and len(emoji) > sum(c.isalpha() for c in text):
        feats.append("__emoji_art__")
    if re.search(r"18\s*\+|\+\s*18", text):
        feats.append("__18plus__")

    tokens: list[str] = []
    for raw in _WORD.findall(text):
        letters = {_script(c) for c in raw if not c.isdigit()}
        if len(letters & {"LATIN", "CYRILLIC", "GREEK", "COPTIC", "other"}) > 1:
            feats.append("__mixed_script__")
        word = _ZERO_O.sub("0", raw)
        if word.isdigit():
            tokens.append(word if len(word) <= 2 else f"__num{min(len(word), 6)}__")
            continue
        word = _fold_word(word)
        if len(word) > 1:
            tokens.append(word)
    return tokens + feats


def build_ngrams(tokens: list[str]) -> list[str]:
    words = [t for t in tokens if not t.startswith("__") or t.startswith("__num")]
    bigrams = [f"{words[i]}_{words[i + 1]}" for i in range(len(words) - 1)]
    return tokens + bigrams
