"""
The `bkit.transform` module can be used to transform any given text. This module covers two broader
types of text transformations including text cleaning or noise removal (`bkit.transform.cleaning`)
and text normalization (`bkit.transform.normalizing`).

All functions and classes are accessible from the `bkit.transform` module, i.e. it is not needed to
access the cleaning functions from `bkit.transform.cleaning`. For more readability one can do it though.
"""

from .cleaning import (
    clean_digits,
    clean_emojis,
    clean_html,
    clean_multiple_punctuations,
    clean_multiple_spaces,
    clean_non_bangla,
    clean_punctuations,
    clean_special_characters,
    clean_text,
    clean_urls,
)
from .normalizing import (
    Normalizer,
    normalize_characters,
    normalize_consonant_diacritics,
    normalize_halant,
    normalize_kar_ambiguity,
    normalize_punctuation_spaces,
    normalize_zero_width_chars,
)

__all__ = [
    "Normalizer",
    "normalize_characters",
    "normalize_punctuation_spaces",
    "normalize_zero_width_chars",
    "normalize_halant",
    "normalize_kar_ambiguity",
    "normalize_consonant_diacritics",
    "clean_punctuations",
    "clean_digits",
    "clean_multiple_spaces",
    "clean_urls",
    "clean_emojis",
    "clean_html",
    "clean_multiple_punctuations",
    "clean_special_characters",
    "clean_text",
    "clean_non_bangla",
]

# ----- normalization rules -----
# The rules are defined as key value pairs in a dictionary.
# The key represents the condition, i.e. the substring we
# want to replace and the value represents the result, i.e.
# the corresponding strings we want to replace with. Example:
# rule = {
#     'ব়': 'র',
#     'য়': 'য়',
#     ...
# }

# nukta normalization
_nukta_normalization = {"ড়": "ড়", "ঢ়": "ঢ়", "ব়": "র", "য়": "য়", "়": ""}

# assamese normalization
# source: https://r12a.github.io/scripts/bengali/block.html#assamese
_assamese_normalization = {
    # according to source, these should be mapped as following
    # 'ৰ': 'র',
    # 'ৱ': 'ব'
    # but according to use, these are mapped as following
    "্ৰ": "্র",
    "ৰ": "ব",
    "ৱ": "র",
}

# kar normalization
_kar_normalization = {
    "অা": "আ",
    "াে": "ো",  # আ + এ
    "ো": "ো",  # এ + আ
    "ৗে": "ৌ",  # ৗ + আ
    "ৌ": "ৌ",  # আ +  ৗ
    "ৄ": "ৃ",
}

# punctuations normalization
_punctuations_normalization = {
    "ʼ": "'",
    "‘": "'",
    "ʻ": "'",
    "’": "'",
    "′": "'",
    "`": "'",
    "‛": "'",
    "❛": "'",
    "❜": "'",
    "´": "'",
    "“": '"',
    "”": '"',
    "″": '"',
    "‟": '"',
    "❝": '"',
    "❞": '"',
    "＂": '"',
    "«": '"',
    "»": '"',
    "〝": '"',
    "〞": '"',
    "〟": '"',
    "...": "…",
    "৷": "।",
    "\xad": "",  # \xad is soft hyphen
}

# legacy normalization
_legacy_normalization = {
    "ঀ": "৭",
    "ঌ": "৯",
    "ৡ": "৯",
    "৵": "৯",
    "৻": "ৎ",
    "ৠ": "ঋ",
    "ঽ": "হ",
    "ৢ": "",
    "ৣ": "",
}

############# REGEX patterns #############
urls = (
    # identify protocol
    r"(?:(?:https?:\/\/|ftp:\/\/|www\.))"
)

############# punctuation space #############
# punctuations that takes space before but not later
_punctuation_pre_space = {"(", "{", "["}

# punctuations that takes later before but not before
_punctuation_post_space = {"!", "?", ",", "।", "॥", ")", "}", "]"}

############# zero width chars #############
_zwj = "\u200d"
_zwnj = "\u200c"

############# halant #############
_valid_post_chars_to = {"ত", "থ", "ন", "ব", "ম", "য", "র"}

_valid_pre_chars = {
    "ক",
    "খ",
    "গ",
    "ঘ",
    "ঙ",
    "চ",
    "জ",
    "ঞ",
    "ট",
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
    "য়",
    "\u200d",
}
_valid_post_chars = {
    "ক",
    "খ",
    "গ",
    "ঘ",
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
    "\u09cd",
}
_valid_conjunct_pairs = {
    "ক": {"ট", "ম", "ত", "ক", "ব", "র", "ল", "ষ", "স", "য"},
    "খ": {"র", "য"},
    "গ": {"ম", "ণ", "ব", "র", "ধ", "ল", "ন", "য"},
    "ঘ": {"র", "য", "ন"},
    "ঙ": {"ম", "ক", "গ", "ঘ", "খ"},
    "চ": {"ব", "ছ", "চ", "ঞ", "য"},
    "ছ": {"ব"},
    "জ": {"জ", "ব", "র", "ঝ", "ঞ", "য"},
    "ঞ": {"জ", "চ", "ঝ", "ছ"},
    "ট": {"ট", "ম", "ব", "র", "য"},
    "ড": {"ড", "য", "র", "ব"},
    "ঢ": {"র", "য"},
    "ণ": {"ট", "ড", "ম", "ণ", "ব", "ঠ", "ঢ", "য"},
    "ত": {"ত", "ম", "ব", "র", "থ", "ন", "য"},
    "থ": {"র", "য", "ব"},
    "দ": {"ম", "দ", "ব", "ধ", "র", "ভ", "য"},
    "ধ": {"ম", "ব", "র", "ন", "য"},
    "ন": {"ট", "ড", "ত", "দ", "ম", "ব", "ঠ", "ধ", "থ", "ন", "য", "স"},
    "প": {"ট", "ত", "র", "ল", "ন", "স", "প", "য"},
    "ফ": {"ল", "র"},
    "ব": {"জ", "দ", "ব", "র", "ধ", "ল", "য"},
    "ভ": {"র", "য", "ব"},
    "ম": {"ম", "ব", "ফ", "র", "ল", "ন", "প", "ভ", "য"},
    "য": {"য"},
    "র": {
        "ক",
        "ঝ",
        "জ",
        "ট",
        "ছ",
        "ঘ",
        "থ",
        "খ",
        "শ",
        "ষ",
        "চ",
        "ঢ",
        "ভ",
        "স",
        "ত",
        "ড",
        "ণ",
        "গ",
        "ফ",
        "হ",
        "প",
        "ম",
        "দ",
        "ব",
        "ল",
        "ধ",
        "ন",
        "য",
        "র",
    },
    "ল": {"ট", "ড", "ম", "ক", "ব", "গ", "ল", "প", "য"},
    "শ": {"ম", "ব", "ছ", "র", "ল", "ন", "চ", "য"},
    "ষ": {"ট", "ম", "ণ", "ক", "ব", "ফ", "ঠ", "প", "য"},
    "স": {"ট", "ত", "ম", "ক", "ব", "ফ", "র", "ল", "থ", "খ", "ন", "প", "য"},
    "হ": {"ম", "ণ", "ব", "র", "ল", "ন", "য"},
}

############# special characters #############
_special_characters = ["$", "#", "&", "%", "@"]

############# special characters #############
_non_print_characters = {
    "\ufffc": "",
    "\ufe0f": "",
}
