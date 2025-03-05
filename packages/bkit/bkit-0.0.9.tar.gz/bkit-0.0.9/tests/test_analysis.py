import os
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bkit


class TestAnalysis:
    @pytest.mark.parametrize(
        "text, expected_result",
        [
            ("হ্যালো বিশ্ব! এটি একটি পরীক্ষা।", 5),
            (["হ্যালো বিশ্ব!", "এটি একটি পরীক্ষা।"], 5),
        ],
    )
    def test_count_words(self, text, expected_result):
        result = bkit.analysis.count_words(text)
        assert result == expected_result
