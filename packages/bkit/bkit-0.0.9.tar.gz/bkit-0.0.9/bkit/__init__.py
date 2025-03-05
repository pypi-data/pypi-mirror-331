"""
Bangla text processing kit with Normalization and Cleaning functions.
"""

import logging

from . import analysis, tokenizer, transform, utils

try:
    from . import lemmatizer, stemmer
except ImportError:
    pass

try:
    from . import ner, pos, shallow, coref, dependency
except ImportError:
    pass

# all basic chars for bangla

vowels = ["অ", "আ", "ই", "ঈ", "উ", "ঊ", "ঋ", "এ", "ঐ", "ও", "ঔ"]
consonants = [
    "ক",
    "খ",
    "গ",
    "ঘ",
    "ঙ",
    "চ",
    "ছ",
    "জ",
    "ঝ",
    "ঞ",
    "ট",
    "ঠ",
    "ড",
    "ঢ",
    "ণ",
    "ত",
    "থ",
    "দ",
    "ধ",
    "ন",
    "প",
    "ফ",
    "ব",
    "ভ",
    "ম",
    "য",
    "র",
    "ল",
    "শ",
    "ষ",
    "স",
    "হ",
    "ড়",
    "ঢ়",
    "য়",
    "ৎ",
    "ঁ",
    "ং",
    "ঃ",
]
digits = ["০", "১", "২", "৩", "৪", "৫", "৬", "৭", "৮", "৯"]

kars = ["া", "ি", "ী", "ু", "ূ", "ৃ", "ে", "ৈ", "ো", "ৌ"]

legacy = [
    "ঀ",
    "ঌ",
    "ঽ",
    "ৠ",
    "ৗ",
    "ৡ",
    "ৢ",
    "ৣ",
    "৲",
    "৴",
    "৵",
    "৶",
    "৷",
    "৸",
    "৹",
    "৺",
    "৻",
    "ৼ",
    "৽",
    "৾",
]
assamese = ["ৰ", "ৱ"]
joiners = ["\u200c", "\u200d"]

nukta = "়"
halant = "্"

bangla_chars = vowels + consonants + digits + kars + joiners + [nukta, halant]
punctuations = [
    "!",
    '"',
    "'",
    "(",
    ")",
    ",",
    "-",
    ".",
    ":",
    ":-",
    ";",
    "<",
    "=",
    ">",
    "?",
    "[",
    "]",
    "{",
    "}",
    "ʼ",
    "।",
    "॥",
    "–",
    "—",
    "‘",
    "’",
    "“",
    "”",
    "…",
    "′",
    "″",
    "√",
    "/",
    "_",
    "|",
]

__bangla_chars = set(bangla_chars)

__special_symbols = ["%", "#", "$", "৳", "+", "*", "&"]
__allowed_chars = set(
    bangla_chars + [" ", "\t", "\n", "\r"] + punctuations + __special_symbols
)

__space_chars = {" ", "\t", "\n", "\f", "\r", "\v"}
__allowed_control_chars = set(joiners).union(__space_chars)

# Model cache dir
import os

ROOT_DIR = os.path.dirname(__file__)
ML_MODELS_CACHE_DIR = os.path.join(ROOT_DIR, ".cache")
