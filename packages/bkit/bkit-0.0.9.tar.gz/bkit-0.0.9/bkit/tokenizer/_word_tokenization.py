from typing import List

import regex

strs_with_comma_col = ["ড", "ডা", "মো", "মোসা", "মোছা", "রা", "সা", "আ", "রহ", "র"]
comma_col_start = "|".join(strs_with_comma_col)
comma_col_neg_behind = "".join([f"(?<!{s})" for s in strs_with_comma_col])

starting_patterns = [
    (regex.compile('([«“‘„"]|[`]+)', regex.U), r" \1 "),
    (regex.compile(f"((?:{comma_col_start})[.:])"), r" \1 "),
]

ending_patterns = [
    (regex.compile('([»”’"])', regex.U), r" \1 "),
    (regex.compile(r"''"), " '' "),
    (regex.compile(r"([^' ])('[র]|') "), r"\1 \2 "),
]

punctuation_patterns = [
    (regex.compile(r'([^\.])(\.)([\]\)}>"\'' "»”’ " r"]*)\s*$", regex.U), r"\1 \2 \3 "),
    # (regex.compile(f"{comma_col_neg_behind}([:,])([^\d])"), r" \1 \2"),
    (regex.compile(r"([:,])([^\d])"), r" \1 \2"),  # Separate commas not in numbers
    (regex.compile(r"([^\d]),([^\d])"), r"\1 , \2"),  # Ensure commas between words are separated
    (regex.compile(r"([:,])$"), r" \1 "),
    (
        regex.compile(r"\.{2,}", regex.U),
        r" \g<0> ",
    ),
    (regex.compile(r"[;@#$%&।]"), r" \g<0> "),
    (regex.compile(r"[?!]"), r" \g<0> "),
    (regex.compile(r"([^'])' "), r"\1 ' "),
    (
        regex.compile(r"[*]", regex.U),
        r" \g<0> ",
    ),
]

parentheses_pattern = (regex.compile(r"[\]\[\(\)\{\}\<\>]"), r" \g<0> ")

word_punct_patterns = [
    (regex.compile(r"(\d+\.?\d*)"), r" \1 "),
    (regex.compile(r"(\w+)"), r" \1 "),
    (regex.compile(r"([\u0980-\u09FF]+)"), r" \1 "),
    (regex.compile(r"([^\w\s]+)"), r" \1 "),
    (regex.compile(r"(\s+)"), r" \1 "),
]


def tokenize(text: str) -> List[str]:
    """
    Tokenize a given Bangla text into individual tokens. Each word and punctuations like
    comma, danda (।), question mark, etc. are considered as tokens.

    Args:
        text (str): The Bangla text to tokenize.

    Returns:
        list: A list of tokens extracted from the text.

    Examples:
        >>> import bkit
        >>> text = 'তুমি কোথায় থাক? ঢাকা বাংলাদেশের রাজধানী। কি অবস্থা তার! ১২/০৩/২০২২ তারিখে সে ৪/ক ঠিকানায় গিয়ে ১২,৩৪৫ টাকা দিয়েছিল।'
        >>> bkit.tokenizer.tokenize(text)
        ['তুমি', 'কোথায়', 'থাক', '?', 'ঢাকা', 'বাংলাদেশের', 'রাজধানী', '।', 'কি', 'অবস্থা', 'তার', '!', '১২/০৩/২০২২', 'তারিখে', 'সে', '৪/ক', 'ঠিকানায়', 'গিয়ে', '১২,৩৪৫', 'টাকা', 'দিয়েছিল', '।']
    """
    for exp, sub in starting_patterns:
        text = exp.sub(sub, text)

    for exp, sub in punctuation_patterns:
        text = exp.sub(sub, text)

    text = parentheses_pattern[0].sub(parentheses_pattern[1], text)
    text = f" {text} "

    for exp, sub in ending_patterns:
        text = exp.sub(sub, text)

    return text.split()


def tokenize_word_punctuation(text: str) -> List[str]:
    """
    Tokenize a given Bangla text into individual tokens. All words and punctuations like
    are considered as tokens.

    Args:
        text (str): The Bangla text to tokenize.

    Returns:
        list: A list of tokens extracted from the text.

    Examples:
        >>> import bkit
        >>> text = 'তুমি কোথায় থাক? ঢাকা বাংলাদেশের রাজধানী। কি অবস্থা তার! ১২/০৩/২০২২ তারিখে সে ৪/ক ঠিকানায় গিয়ে ১২,৩৪৫ টাকা দিয়েছিল।'
        >>> bkit.tokenizer.tokenize_word_punctuation(text)
        ['তুমি', 'কোথায়', 'থাক', '?', 'ঢাকা', 'বাংলাদেশের', 'রাজধানী', '।', 'কি', 'অবস্থা', 'তার', '!', '১২', '/', '০৩', '/', '২০২২', 'তারিখে', 'সে', '৪', '/', 'ক', 'ঠিকানায়', 'গিয়ে', '১২', ',', '৩৪৫', 'টাকা', 'দিয়েছিল', '।']
    """
    for exp, sub in word_punct_patterns:
        text = exp.sub(sub, text)

    return text.split()
