from collections import Counter, defaultdict
from typing import Dict, List, Tuple

import bkit


def count_words(
    text: Tuple[str, List[str]],
    clean_punctuation: bool = False,
    punct_replacement: str = "",
    return_dict: bool = False,
    ordered: bool = False,
) -> Tuple[int, Dict[str, int]]:
    """
    Counts the occurrences of words in the given text.

    Args:
        text (Tuple[str, List[str]]): The text to count words from. If a string is provided,
            it will be split into words. If a list of strings is provided, each string will
            be split into words and counted separately.
        clean_punctuation (bool, optional): Whether to clean punctuation from the words. Defaults to False.
        punct_replacement (str, optional): The replacement for the punctuation. Only applicable if
            clean_punctuation is True. Defaults to "".
        return_dict (bool, optional): Whether to return the word count as a dictionary.
            Defaults to False.
        ordered (bool, optional): Whether to return the word count in descending order. Only
            applicable if return_dict is True. Defaults to False.

    Returns:
        Tuple[int, Dict[str, int]]: If return_dict is True, returns a tuple containing the
            total word count and a dictionary where the keys are the words and the values
            are their respective counts. If return_dict is False, returns only the total
            word count as an integer.
    """

    if ordered:
        assert return_dict, "return_dict must be True for ordered result."

    count = Counter()

    if isinstance(text, str):
        count.update(text.split())
    else:
        for t in text:
            count.update(t.split())

    if clean_punctuation:
        clean_count = defaultdict(int)

        for k, v in count.items():
            k = bkit.transform.clean_punctuations(k, punct_replacement)

            for w in k.split():
                if w.strip():
                    clean_count[w] += v

        result = dict(clean_count)
    else:
        result = dict(count)

    if return_dict:
        if ordered:
            result = dict(sorted(result.items(), key=lambda x: x[1], reverse=True))
    else:
        result = sum(result.values())

    return result
