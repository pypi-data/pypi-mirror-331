import bkit


def preprocess_text(text):
    if text is None:
        return text

    pipeline = [
        "normalize_characters",
        "normalize_punctuation_spaces",
        "normalize_zero_width_chars",
        "normalize_halant",
        "normalize_kar_ambiguity",
        "clean_non_bangla",
        "clean_multiple_spaces",
        "clean_urls",
        "clean_emojis",
        "clean_html",
        "clean_multiple_punctuations",
        "clean_special_characters",
    ]

    for processing_func in pipeline:
        text = eval(f"bkit.transform.{processing_func}(text)")

        if text is None:
            return text

    return text
