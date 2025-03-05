import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bkit


class TestCleaning:
    def test_punctuation_cleaning(self):
        source_file = "test_data/punct_cleaning.tsv"
        source_file = open(source_file)

        for line in source_file:
            source, replace_with, target = line.split("\t")
            source, target = source.strip(), target.strip()

            cleaned = bkit.transform.clean_punctuations(
                source, replace_with=replace_with
            )
            assert (
                target == cleaned
            ), f"\ninput: {list(source)}\ntarget: {list(target)}\noutput: {list(cleaned)}"

    def test_multi_punctuation_cleaning(self):
        source_file = "test_data/multi_punct_cleaning.tsv"
        source_file = open(source_file)

        for line in source_file:
            source, target = line.split("\t")
            source, target = source.strip(), target.strip()

            cleaned = bkit.transform.clean_multiple_punctuations(source)
            assert (
                target == cleaned
            ), f"\ninput: {list(source)}\ntarget: {list(target)}\noutput: {list(cleaned)}"

    def test_digit_cleaning(self):
        source_file = "test_data/digit_cleaning.tsv"
        source_file = open(source_file)

        for line in source_file:
            source, replace_with, target = line.split("\t")
            source, target = source.strip(), target.strip()

            cleaned = bkit.transform.clean_digits(source, replace_with=replace_with)
            assert (
                target == cleaned
            ), f"\ninput: {list(source)}\ntarget: {list(target)}\noutput: {list(cleaned)}"

    def test_multi_space_cleaning(self):
        source_file = "test_data/multi_space_cleaning.tsv"
        source_file = open(source_file)

        for line in source_file:
            source, target = line.split("\t")
            source, target = source.strip(), target.strip()

            cleaned = bkit.transform.clean_multiple_spaces(source)
            assert (
                target == cleaned
            ), f"\ninput: {list(source)}\ntarget: {list(target)}\noutput: {list(cleaned)}"

    def test_url_cleaning(self):
        source_file = "test_data/url_cleaning.tsv"
        source_file = open(source_file)

        for line in source_file:
            source, replace_with, target = line.split("\t")
            source, target = source.strip(), target.strip()

            cleaned = bkit.transform.clean_urls(source, replace_with=replace_with)
            assert (
                target == cleaned
            ), f"\ninput: {list(source)}\ntarget: {list(target)}\noutput: {list(cleaned)}"

    def test_html_cleaning(self):
        source_file = "test_data/html_cleaning.tsv"
        source_file = open(source_file)

        for line in source_file:
            source, replace_with, target = line.split("\t")
            source, target = source.strip(), target.strip()

            cleaned = bkit.transform.clean_html(source, replace_with=replace_with)
            assert (
                target == cleaned
            ), f"\ninput: {list(source)}\ntarget: {list(target)}\noutput: {list(cleaned)}"

    def test_emoji_cleaning(self):
        source_file = "test_data/emoji_cleaning.tsv"
        source_file = open(source_file)

        for line in source_file:
            source, replace_with, target = line.split("\t")
            source, target = source.strip(), target.strip()

            cleaned = bkit.transform.clean_emojis(source, replace_with=replace_with)
            assert (
                target == cleaned
            ), f"\ninput: {list(source)}\ntarget: {list(target)}\noutput: {list(cleaned)}"

    def test_special_char_cleaning(self):
        source_file = "test_data/special_char_cleaning.tsv"
        source_file = open(source_file)

        for line in source_file:
            source, replace_with, target = line.split("\t")
            source, target = source.strip(), target.strip()

            cleaned = bkit.transform.clean_special_characters(
                source, replace_with=replace_with
            )
            assert (
                target == cleaned
            ), f"\ninput: {list(source)}\ntarget: {list(target)}\noutput: {list(cleaned)}"
