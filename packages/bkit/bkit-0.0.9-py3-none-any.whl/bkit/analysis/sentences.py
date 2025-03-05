from collections import Counter
from typing import List, Tuple

import bkit


def count_sentences(
    text: Tuple[str, List[str]], return_dict: bool = False, ordered: bool = False
) -> int:
    """
    Counts the number of sentences in the given text or list of texts.

    Args:
        text (Tuple[str, List[str]]): The text or list of texts to count sentences from.
        return_dict (bool, optional): Whether to return the result as a dictionary. Defaults to False.
        ordered (bool, optional): Whether to order the result in descending order.
            Only applicable if return_dict is True. Defaults to False.

    Returns:
        int or dict: The count of sentences. If return_dict is True, returns a dictionary with sentences as keys
        and their counts as values. If return_dict is False, returns the total count of sentences.

    Raises:
        AssertionError: If ordered is True but return_dict is False.
    """
    if ordered:
        assert return_dict, "return_dict must be True for ordered result."

    count = Counter()

    if isinstance(text, str):
        sentences = bkit.tokenizer.tokenize_sentence(text)
        count.update(sentences)
    else:
        for t in text:
            sentences = bkit.tokenizer.tokenize_sentence(t)
            count.update(sentences)

    if return_dict:
        if ordered:
            result = dict(sorted(count.items(), key=lambda x: x[1], reverse=True))
        else:
            result = dict(count)
    else:
        result = sum(count.values())

    return result
