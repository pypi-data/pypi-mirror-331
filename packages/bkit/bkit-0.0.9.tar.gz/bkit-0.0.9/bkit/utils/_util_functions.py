import bkit


def is_bangla(text: str) -> bool:
    """Checks if text contains only Bangla and space characters.
    Returns true if so, else return false

    Args:
        text (str): The text to check

    Returns:
        bool: True if text contains only Bangla and space characters,
        false otherwise.
    """
    for c in text:
        if c not in bkit.__allowed_chars:
            return False
    return True


def is_digit(text: str) -> bool:
    """Checks if the text contains only Bangla digits. Returns
    True if so, else return false.

    Args:
        text (str): The text to check.

    Returns:
        bool: True if text contains only digits. False otherwise.
    """
    for c in text:
        if not (c in bkit.digits or c == "."):
            return False
    return True


def contains_digit(text: str, check_english_digits: bool = False) -> bool:
    """Checks if text contains any digits. Returns true if so, else false.

    Args:
        text (str): The text to check.
        check_english_digits (bool, optional): Whether to check english digits too.
            Defaults to False.

    Returns:
        bool: True if text contains any digit, false otherwise.
    """
    for d in bkit.digits:
        if d in text:
            return True

    if check_english_digits:
        english_digits = [chr(ord("0") + i) for i in range(10)]
        for d in english_digits:
            if d in text:
                return True

    return False


def contains_bangla(text: str) -> bool:
    """Checks if text contains any Bangla character. Returns
    true if so, else return false

    Args:
        text (str): The text to check

    Returns:
        bool: True if text contains any Bangla character, false otherwise.
    """
    for c in text:
        if c in bkit.__bangla_chars:
            return True
    return False
