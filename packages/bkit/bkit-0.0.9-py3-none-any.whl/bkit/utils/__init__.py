"""
This module contains some utility text checking functions. These functions are designed to
process Bangla text only.
"""

from ._models import MODEL_URL_MAP
from ._text import preprocess_text
from ._util_functions import contains_bangla, contains_digit, is_bangla, is_digit
from ._files_and_dirs import load_cached_file
from ._download import download_file_from_google_drive
try:
    from ._download import download_file_from_google_drive
    from ._files_and_dirs import *
except ImportError:
    pass

__all__ = ["is_bangla", "is_digit", "contains_digit", "contains_bangla"]
