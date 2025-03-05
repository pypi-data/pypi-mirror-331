from typing import List

import regex


def tokenize_sentence(text: str) -> List[str]:
    """
    Tokenize the given text into sentences.

    Args:
        text (str): The text to tokenize into sentences.

    Returns:
        list: A list of sentences extracted from the text.

    Examples:
        >>> import bkit
        >>> text = 'তুমি কোথায় থাক? ঢাকা বাংলাদেশের রাজধানী। কি অবস্থা তার! ১২/০৩/২০২২ তারিখে সে ৪/ক ঠিকানায় গিয়ে ১২,৩৪৫ টাকা দিয়েছিল।'
        >>> bkit.tokenizer.tokenize_sentence(text)
        ['তুমি কোথায় থাক?', 'ঢাকা বাংলাদেশের রাজধানী।', 'কি অবস্থা তার!', '১২/০৩/২০২২ তারিখে সে ৪/ক ঠিকানায় গিয়ে ১২,৩৪৫ টাকা দিয়েছিল।']
    """
    sentences = regex.split(
        r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<![\u0981-\u09fe]\.)(?<=\.|\?|।|!|\n)\s+", text
    )
    return sentences
