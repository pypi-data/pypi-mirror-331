"""
Bangla text normalization related functions.
"""

import unicodedata

import regex

import bkit


def normalize_characters(text: str) -> str:
    """Normalize Bangla characters. The text is normalized based on the
    following steps sequentially:
        1. Nukta normalization: Normalizes the characters with nukta like ড়.
        2. Assamese normalization: Normalized the assamese characters.
        3. Kar normalization: Normalizes the 'ো' and 'ৌ' kars.
        4. Initial kar normalization
        5. Initial ঁ, ং, and ঃ normalization
        6. Legacy characters: Normalized the legacy characters like: ৡ, ঀ, etc.
        7. Punctuation normalization: Normalize punctuation like quotations.

    Args:
        text (str): The text to normalize.

    Returns:
        str: The normalized text.
    """
    # Nukta normalization
    for condition, result in bkit.transform._nukta_normalization.items():
        text = text.replace(condition, result)

    # Assamese normalization
    for condition, result in bkit.transform._assamese_normalization.items():
        text = text.replace(condition, result)

    # Kar normalization
    for condition, result in bkit.transform._kar_normalization.items():
        text = text.replace(condition, result)

    # Initial kar and ঁ, ং, and ঃ normalization normalization
    i = 0
    while i < len(text) and (text[i] in bkit.kars or text[i] in ["ঁ", "ং", "ঃ"]):
        i += 1
    text = text[i:] if i < len(text) else ""

    # Legacy character normalization
    for condition, result in bkit.transform._legacy_normalization.items():
        text = text.replace(condition, result)

    # Punctuation normalization
    for condition, result in bkit.transform._punctuations_normalization.items():
        text = text.replace(condition, result)

    # Non-printable normalization
    for condition, result in bkit.transform._non_print_characters.items():
        text = text.replace(condition, result)

    # Control character normalization
    text = "".join(
        [
            char
            for char in text
            if unicodedata.category(char)[0] != "C"
            or char in bkit.__allowed_control_chars
        ]
    )

    return text


def normalize_punctuation_spaces(text: str) -> str:
    """Normalizes spaces between punctuation marks and letters or
    digits. Like:
        1. (   কখগ) -> (কখগ)
        2. কখগ । -> কখগ।
        3. কখগ।ঘচছ -> কখগ। ঘচছ

    Args:
        text (str): The text to be normalized

    Returns:
        str: The normalized text
    """
    out_chars = []

    i = 0
    while i < len(text):
        char = text[i]
        if char in bkit.transform._punctuation_pre_space:
            while len(out_chars) > 1 and out_chars[-2] == " ":
                # remove multiple pre spaces
                out_chars.pop()

            if i - 1 >= 0 and text[i - 1] != " ":
                out_chars.append(" ")

            # remove post spaces e.g. (   কখগ) -> (কখগ)
            while i + 1 < len(text) and text[i + 1] == " ":
                i += 1

            out_chars.append(char)
        elif char in bkit.transform._punctuation_post_space:
            # remove the pre-spaces e.g. কখগ । -> কখগ।
            while out_chars and out_chars[-1] == " ":
                out_chars.pop()

            out_chars.append(char)
            if i + 1 < len(text) and text[i + 1] != " ":
                if (
                    i - 1 >= 0
                    and bkit.utils.is_digit(text[i - 1])
                    and bkit.utils.is_digit(text[i + 1])
                ):
                    pass
                else:
                    out_chars.append(" ")
            while i + 2 < len(text) and text[i + 2] == " " and bkit.utils.is_digit(text[i + 1]):
                # remove multiple post spaces
                i += 1
        else:
            out_chars.append(char)
        i += 1

    return "".join(out_chars)


def normalize_zero_width_chars(text: str) -> str:
    """Normalize zero width (ZW) characters. There are two zero-width characters - Zero
    Width Joiner (ZWJ) [`0x200D`] and Zero Width Non Joiner (ZWNJ) [`0x200C`]
    characters. Generally ZWNJ is not used with Bangla texts and ZWJ joiner is
    used with `র` only. Based on this intuition, all ZW characters are removed
    expect a ZWJ preceded by a `র`.

    Args:
        text (str): The text to be normalized.

    Returns:
        str: The normalized text.
    """
    out_chars = []

    for i in range(len(text)):
        if text[i] == bkit.transform._zwnj:
            if i - 1 >= 0 and text[i - 1] == "র":
                if i - 2 >= 0 and text[i - 2] == bkit.halant:
                    # remove this ZWNJ
                    pass
                elif (
                    i + 2 < len(text)
                    and text[i + 1] == bkit.halant
                    and text[i + 2] == "য"
                ):
                    # convert this ZWNJ to ZWJ
                    out_chars.append(bkit.transform._zwj)

            # remove all other ZWNJ
            continue

        if text[i] == bkit.transform._zwj:
            if i - 1 >= 0 and text[i - 1] == "র":
                if i - 2 >= 0 and text[i - 2] == bkit.halant:
                    # remove this ZWJ
                    pass
                elif (
                    i + 2 < len(text)
                    and text[i + 1] == bkit.halant
                    and text[i + 2] == "য"
                ):
                    # keep this ZWJ for zo-fola
                    out_chars.append(text[i])
        else:
            out_chars.append(text[i])

    return "".join(out_chars)


def normalize_halant(text: str) -> str:
    """Normalizes halant (হসন্ত) [`0x09CD`] in Bangla text. While using this function, it is
    recommended to normalize the zero width characters at first, e.g. using the
    `bkit.transform.normalize_zero_width_chars()` function.

    During the normalization it also handles the `ত্ -> ৎ` conversion. For a valid conjunct
    letter (যুক্তবর্ণ) where 'ত' is the former character, can take one of 'ত', 'থ', 'ন', 'ব', 'ম', 'য',
    and 'র' as the next character. The conversion is perform based on this intuition.

    During the halant normalization, the following cases are handled.
    - Remove any leaning and tailing halant of a word and/or text.
    - Replace two or more consecutive occurrence of halant by a single halant.
    - Remove halant between any characters that do not follow or precede a halant character.
    Like a halant that follows or precedes a vowel, kar, য়, etc will be removed.
    - Remove multiple fola (multiple ref, ro-fola and jo-fola)

    Args:
        text (str): The text to be normalized.

    Returns:
        str: The normalized text.
    """
    out_chars, i = [], 0
    ref, ro = False, False
    multi_ro_ref, multi_zo = False, False

    while i < len(text):
        if text[i] == bkit.halant:
            # check if halant is at the start of text or word
            if i == 0 or (i - 1 >= 0 and text[i - 1] in bkit.__space_chars):
                i += 1
                continue

            # check if halant is at the end of text or word
            if i == len(text) - 1 or (
                i + 1 < len(text) and text[i + 1] in bkit.__space_chars
            ):
                # handle ত -> ৎ first
                if text[i - 1] == "ত":
                    if i - 2 >= 0 and text[i - 2] == bkit.halant:
                        # consider ত as conjugate
                        pass
                    else:
                        out_chars.pop()  # remove already added ত
                        out_chars.append("ৎ")
                if text[i - 1] == "র":
                    # tailing ref
                    out_chars.pop()

                i += 1
                continue

            # handle multiple ref
            if not ro and text[i - 1] == "র":
                ref = True

                if multi_ro_ref:
                    out_chars.pop()
                    i += 1
                    continue

                multi_ro_ref = True

            # handle multiple ro-fola
            elif not ref and text[i + 1] == "র":
                ro = True

                if multi_ro_ref:
                    i += 2
                    continue

                multi_ro_ref = True
            else:
                ref, ro = False, False
                multi_ro_ref = False

            # handle multiple zo-fola
            if text[i + 1] == "য":
                if multi_zo:
                    i += 2
                    continue

                multi_zo = True

            # handle ত -> ৎ
            if (
                text[i - 1] == "ত"
                and text[i + 1] not in bkit.transform._valid_post_chars_to
            ):
                if i - 2 >= 0 and text[i - 2] == bkit.halant:
                    # consider ত as conjugate
                    pass
                else:
                    # replace by ৎ
                    out_chars.pop()  # remove already added ত
                    out_chars.append("ৎ")
            elif text[i + 1] == "য" and text[i - 1] != bkit.halant:
                # do not remove any zo-fola
                out_chars.append(text[i])
            elif text[i + 1] == "য়" and text[i - 1] in bkit.transform._valid_pre_chars:
                # make it zo-fola
                out_chars.append(text[i])
                out_chars.append("য")
                i += 1
            elif text[i - 1] in bkit.transform._valid_conjunct_pairs:
                j = i
                while i + 1 < len(text) and text[i + 1] == bkit.halant:
                    i += 1

                if (
                    i + 1 < len(text)
                    and text[i + 1] in bkit.transform._valid_conjunct_pairs[text[j - 1]]
                ):
                    out_chars.append(text[i])

        else:
            out_chars.append(text[i])
            if text[i] != "র":
                ref, ro = False, False
                multi_ro_ref = False
            if not (text[i] == "য" and i - 1 >= 0 and text[i - 1] == "্"):
                multi_zo = False

        i += 1

    while out_chars and out_chars[-1] == "্":
        out_chars.pop()

        if out_chars and out_chars[-1] == "র":
            # tailing ref
            out_chars.pop()

    return "".join(out_chars)


def normalize_kar_ambiguity(text: str) -> str:
    """Normalizes kar ambiguity with vowels, ঁ, ং, and ঃ. It removes any kar that is preceded
    by a vowel or consonant diacritics like: `আা` will be normalized to `আ`. In case of
    consecutive occurrence of kars like: `কাাাী`, only the first kar will be kept like: `কা`.

    Args:
        text (str): The text to be normalized.

    Returns:
        str: The normalized text.
    """
    # swap ঁ, ং, and ঃ with kars
    text = regex.sub(
        r"([\u0981-\u0983])([\u09be-\u09c3\u09c7\u09c8\u09cb\u09cc])", "\\2\\1", text
    )
    text = text.replace("অা", "আ")

    # swap fola and kar
    text = regex.sub(
        r"([\u09be-\u09c3\u09c7\u09c8\u09cb\u09cc])(্য|্র)", "\\2\\1", text
    )

    # remove redundancy
    text = regex.sub(
        r"([\u0981-\u0983\u0985-\u098b\u0989\u0990\u0993\u0994\u09be-\u09c3\u09c7\u09c8\u09cb\u09cc])(?:[\u09be-\u09c3\u09c7\u09c8\u09cb\u09cc]+)",
        r"\1",
        text,
    )

    return text


def normalize_consonant_diacritics(text: str) -> str:
    """Normalizes multiple consecutive occurrence of ঁ, ং, and ঃ

    Args:
        text (str): The text to normalize.

    Returns:
        str: The normalized text.
    """
    out_chars = [text[0]] if text else []

    i = 1
    while i < len(text):
        if text[i] in ["ঁ", "ং", "ঃ"] and text[i - 1] in ["ং", "ঃ"]:
            pass
        else:
            out_chars.append(text[i])
        i += 1

    return "".join(out_chars)


class Normalizer:
    """A pipeline class for normalizing the Bangla texts. It can perform the normalization
    in five steps. These are: 1. Character normalization, 2. Punctuation space normalization,
    3. Zero-width character normalization, 4. Halant normalization, 5. Vowel kar normalization,
    and 6. Consonant diacritics normalization.

    Examples:
        >>> import bkit
        >>> text = 'অাামাব় । '
        >>> list(text)
        ['অ', 'া', 'া', 'ম', 'া', 'ব', '়', ' ', '।', ' ']
        >>> normalizer = bkit.transform.Normalizer(
        ...     normalize_characters=True,
        ...     normalize_zw_characters=True,
        ...     normalize_halant=True,
        ...     normalize_vowel_kar=True,
        ...     normalize_punctuation_spaces=True
        ... )
        >>>  clean_text = normalizer(text)
        >>>  clean_text
        আমার।
        >>>  list(clean_text)
        ['আ', 'ম', 'া', 'র', '।']
    """

    def __init__(
        self,
        normalize_characters: bool = True,
        normalize_punctuation_spaces: bool = True,
        normalize_zw_characters: bool = True,
        normalize_halant: bool = True,
        normalize_vowel_kar: bool = True,
        normalize_multi_consonant_diacritics: bool = True,
    ) -> None:
        """
        Args:
            normalize_characters (bool, optional): whether to normalize characters. Defaults
                to True.
            normalize_punctuation_spaces (bool, optional): Whether to normalize punctuation
                spaces. Defaults to True.
            normalize_zw_characters (bool, optional): Whether to normalize zero width
                characters. Defaults to True.
            normalize_halant (bool, optional): Whether to normalize halant. Defaults to True.
            normalize_vowel_kar (bool, optional): Whether to normalize the vowel-kar ambiguity.
                Defaults to True.
        """
        __pdoc__ = {"__call__": True}

        self.pipeline = []

        if normalize_characters:
            self.pipeline.append(bkit.transform.normalize_characters)
        if normalize_zw_characters:
            self.pipeline.append(bkit.transform.normalize_zero_width_chars)
        if normalize_halant:
            self.pipeline.append(bkit.transform.normalize_halant)
        if normalize_vowel_kar:
            self.pipeline.append(bkit.transform.normalize_kar_ambiguity)
            self.pipeline.append(
                bkit.transform.normalize_halant
            )  # handle multiple fola
        if normalize_multi_consonant_diacritics:
            self.pipeline.append(bkit.transform.normalize_consonant_diacritics)
        if normalize_punctuation_spaces:
            self.pipeline.append(bkit.transform.normalize_punctuation_spaces)

        assert len(self.pipeline) > 0, "At least a normalization type must be chosen."

    def __call__(self, text: str) -> str:
        """
        Args:
            text (str): The text to normalize.

        Returns:
            str: The normalized text.
        """
        for function in self.pipeline:
            text = function(text)

        return text
