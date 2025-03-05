import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bkit


class TestNormalization:
    def test_character_normalization(self):
        source_file = "test_data/characters.tsv"
        source_file = open(source_file)

        for line in source_file:
            source, target = line.split("\t")
            source, target = source.strip(), target.strip()

            normalized = bkit.transform.normalize_characters(source)
            assert (
                target == normalized
            ), f"\ninput:  {list(source)}\ntarget: {list(target)}\noutput: {list(normalized)}"

    def test_punctuation_space_normalization(self):
        source_file = "test_data/punctuation_space.tsv"
        source_file = open(source_file)

        for line in source_file:
            source, target = line.split("\t")
            source, target = source.strip(), target.strip()

            normalized = bkit.transform.normalize_punctuation_spaces(source)
            assert (
                target == normalized
            ), f"\ninput:  {list(source)}\ntarget: {list(target)}\noutput: {list(normalized)}"

    def test_zw_normalization(self):
        source_file = "test_data/zero_width.tsv"
        source_file = open(source_file)

        for line in source_file:
            source, target = line.split("\t")
            source, target = source.strip(), target.strip()

            normalized = bkit.transform.normalize_zero_width_chars(source)
            assert (
                target == normalized
            ), f"\ninput:  {list(source)}\ntarget: {list(target)}\noutput: {list(normalized)}"

    def test_halant_normalization(self):
        source_file = "test_data/halant.tsv"
        source_file = open(source_file)

        for line in source_file:
            source, target = line.split("\t")
            source, target = source.strip(), target.strip()

            normalized = bkit.transform.normalize_halant(source)
            assert (
                target == normalized
            ), f"\ninput:  {list(source)}\ntarget: {list(target)}\noutput: {list(normalized)}"

    def test_vowel_kar_normalization(self):
        source_file = "test_data/vowel_kar.tsv"
        source_file = open(source_file)

        for line in source_file:
            source, target = line.split("\t")
            source, target = source.strip(), target.strip()

            normalized = bkit.transform.normalize_kar_ambiguity(source)
            assert (
                target == normalized
            ), f"\ninput:  {list(source)}\ntarget: {list(target)}\noutput: {list(normalized)}"

    def test_normalizer(self):
        source_file = "test_data/normalizer.tsv"
        source_file = open(source_file)

        normalizer = bkit.transform.Normalizer()

        for line in source_file:
            source, target = line.split("\t")
            source, target = source.strip("\n"), target.strip("\n")

            normalized = normalizer(source)
            assert (
                target == normalized
            ), f"\ninput:  {list(source)}\ntarget: {list(target)}\noutput: {list(normalized)}"
