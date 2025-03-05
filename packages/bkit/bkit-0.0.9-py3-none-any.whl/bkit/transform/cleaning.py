"""
This module holds methods that can be used to remove noise or clean text.
"""

import regex

import bkit

emoji_pattern = regex.compile(
    r"(?!\s)[\s"
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U00002500-\U00002BEF"  # chinese char
    "\U00002702-\U000027B0"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001f926-\U0001f937"
    "\U00010000-\U0010ffff"
    "\u2640-\u2642"
    "\u2600-\u2B55"
    "\u200d"
    "\u23cf"
    "\u23e9"
    "\u231a"
    "\u23e9-\u23f3\u23f8-\u23fa"
    "\ufe0f"  # dingbats
    "\u3030"
    r"]+(?<!\s)",
    flags=regex.UNICODE,
)


def clean_punctuations(text: str, replace_with: str = "") -> str:
    """Cleans or removes punctuations and replace those with the given string.

    Args:
        text (str): The text to clean.
        replace_with (str, optional): The string to replace with. Defaults to ''.

    Returns:
        str: The clean string

    Examples:
        >>> import bkit
        >>> text = 'আমরা মাঠে ফুটবল খেলতে পছন্দ করি!'
        >>> bkit.transform.clean_punctuations(text)
        'আমরা মাঠে ফুটবল খেলতে পছন্দ করি'
        >>> bkit.transform.clean_punctuations(text, replace_with=' PUNCT ')
        'আমরা মাঠে ফুটবল খেলতে পছন্দ করি PUNCT '
    """
    if replace_with == "":
        for punctuation in bkit.punctuations:
            text = text.replace(punctuation, replace_with)
    else:
        punctuations = regex.escape("".join(bkit.punctuations))
        punctuations = f"[{punctuations}]+"

        text = regex.sub(punctuations, replace_with, text)

    return text


def clean_digits(text: str, replace_with: str = " ") -> str:
    """Clean digits and replace each digits with the given string.

    Args:
        text (str): The text to clean
        replace_with (str, optional): The string to replace with.
            Defaults to ' '.

    Returns:
        str: The clean string
    """
    text = regex.sub(r"[০-৯]+\.?[০-৯]*", replace_with, text)

    return text


def clean_multiple_spaces(text: str, keep_new_line: bool = False) -> str:
    """Clean multiple consecutive whitespace characters including space,
    newlines, tabs, vertical tabs, etc. It also removes leading and
    tailing whitespace characters.

    Args:
        text (str): The text to clean
        keep_new_line (bool, optional): If True, keeps a single newline
            character for one or more consecutive newlines. Defaults to
            False.

    Returns:
        str: The clean text.
    """
    if keep_new_line:
        text = regex.sub(r"[\n\v]+", "\n", text)
        text = regex.sub(r"[\t\f\r ]+", " ", text)
        text = regex.sub(r"\n[\t\f\r ]+", "\n", text)
    else:
        text = " ".join(text.split())

    return text.strip()


def clean_urls(text: str, replace_with: str = " ") -> str:
    """Clean URLs from text and replace the URLs with any given string.

    Args:
        text (str): The text to clean
        replace_with (str, optional): Any string to replace the URLs.
            Defaults to ' '.

    Returns:
        str: The clean text.
    """
    text = regex.sub(r"(?:(?:https?:\/\/|ftp:\/\/|www\.))\S+", replace_with, text)
    return text


def clean_html(text: str, replace_with: str = "") -> str:
    """Clean HTML tags from text and replace the tags with given string.

    Args:
        text (str): The text to clean
        replace_with (str, optional): Any string to replace the HTML tags.
            Defaults to ''.

    Returns:
        str: The clean text.
    """
    text = regex.sub(
        r"<script.*?>[\S\s]*?</script>|<style.*?>[\S\s]*?</style>|<[\S\s]*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});",
        replace_with,
        text,
    )
    return text


def clean_emojis(text: str, replace_with: str = "") -> str:
    """Removes emojis and emoticons form text and replace with the
    given sting.

    Args:
        text (str): The text to clean.
        replace_with (str, optional): The string to replace. Defaults to ''.

    Returns:
        str: The clean text.
    """
    text = emoji_pattern.sub(replace_with, text)
    return text


def clean_multiple_punctuations(text: str) -> str:
    """Remove multiple consecutive punctuations and keep the first punctuation only.

    Args:
        text (str): The text to clean.

    Returns:
        str: The clean text.
    """
    punctuations = regex.escape("".join(bkit.punctuations))
    punctuations = f"[{punctuations}]"

    text = regex.sub(rf"({punctuations})(?:{punctuations}+)", r"\1", text)
    return text


def clean_special_characters(
    text: str, characters: list = None, replace_with: str = " "
) -> str:
    """Remove special characters like $, #, @, etc and replace them with the given string.

    Args:
        text (str): The text to clean.
        characters (list, optional): The characters to clean. If None is passed, `['$', '#',
            '&', '%', '@']` are removed by default.
        replace_with (str, optional): The string to replace the characters with. Defaults to ' '.

    Returns:
        str: The clean text.
    """
    if not characters:
        characters = bkit.transform._special_characters

    characters = regex.escape("".join(characters))
    characters = f"[{characters}]"

    text = regex.sub(rf"{characters}+", replace_with, text)
    return text


def clean_non_bangla(text: str, replace_with: str = " ") -> str:
    """Removes any non-bangla character in the text.

    Args:
        text (str): The text to clean.
        replace_with (str, optional): The string to replace. Defaults to ' '.

    Returns:
        str: The clean text.
    """
    bangla_chars = regex.escape("".join(bkit.__allowed_chars))
    non_bangla_chars = f"[^{bangla_chars}]+"

    text = regex.sub(non_bangla_chars, replace_with, text)

    return text


def clean_text(
    text: str,
    remove_digits: bool = True,
    remove_emojis: bool = True,
    remove_punctuations: bool = True,
    remove_non_bangla: bool = True,
) -> str:
    """Clean text using the following steps sequentially:
    1. Removes all HTML tags
    2. Removes all URLs
    3. Removes all emojis (optional)
    4. Removes all digits (optional)
    5. Removes all punctuations (optional)
    6. Removes all extra spaces

    Args:
        text (str): The text to clean
        remove_digits (bool, optional): Whether to remove digits. Defaults to True.
        remove_emojis (bool, optional): Whether to remove emojis. Defaults to True.
        remove_punctuations (bool, optional): Whether to remove punctuations. Defaults to True.

    Returns:
        str: The clean text.
    """
    text = clean_html(text, " ")
    text = clean_urls(text, " ")
    text = clean_emojis(text, " ") if remove_emojis else text
    text = clean_digits(text, " ") if remove_digits else text
    text = clean_punctuations(text, " ") if remove_punctuations else text
    text = clean_non_bangla(text) if remove_non_bangla else text
    text = clean_multiple_spaces(text)
    return text
