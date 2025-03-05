import os
import re
import shutil
from pathlib import Path
from typing import Union

import bkit
from bkit.utils import MODEL_URL_MAP
from ._download import download_file_from_google_drive


def load_cached_file(
    model_name: str,
    force_redownload: bool,
) -> Path:
    """
    Load cached model files or download and cache them.

    Args:
        model_name (str): Name of the pre-trained NER model.
        force_redownload (bool): Flag to force redownload if the model is not cached.

    Returns:
        Path: Path to the directory containing cached model files.
    """

    if not force_redownload and os.path.exists(bkit.ML_MODELS_CACHE_DIR):
        cache_dir = Path(bkit.ML_MODELS_CACHE_DIR)
        model_cache_dir = cache_dir / f"{model_name}"

        if os.path.exists(model_cache_dir):
            return detect_model_folder(model_cache_dir)

    return download_from_url(model_name)


def download_from_url(model_name: str) -> Path:
    """
    Download model files from a URL and cache them.

    Args:
        model_name (str): Name of the pre-trained NER model.

    Returns:
        Path: Path to the directory containing cached model files.
    """

    cache_dir = Path(bkit.ML_MODELS_CACHE_DIR)
    model_cache_dir = cache_dir / f"{model_name}"

    # build the cache directory if no cache directory is present
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    else:
        # purge cache directory from the saved model files before downloading
        if os.path.exists(model_cache_dir):
            shutil.rmtree(model_cache_dir, ignore_errors=False)

    file_link = MODEL_URL_MAP[model_name]
    file_path = str(model_cache_dir) + ".zip"

    download_file_from_google_drive(file_link, file_path)
    unzip_file(file_path, model_cache_dir)
    os.remove(file_path)

    return detect_model_folder(model_cache_dir)


def get_id_from_url(url: str):
    """
    Extracts the file ID from a public download url. Supppose, the donwload url
    is - https://drive.google.com/file/d/1bjHvSQrKLtIYdextXBBKrk2l5P_xWdE1/view?usp=share_link
    the function will return the file id  - 1bjHvSQrKLtIYdextXBBKrk2l5P_xWdE1
    Args:
        url (str): share link of the file (google drive link for now)
    """

    url = url.split("https://drive.google.com/file/d/")[1]
    url = re.split("/view\?usp=(sharing|share_link)", url)[0]
    return url


def unzip_file(file: Path, unzip_to: Path):
    """
    unpack and write out in CoNLL column-like format
    source: flair/file_utils.py
    """

    from zipfile import ZipFile

    with ZipFile(file, "r") as zipObj:
        # Extract all the contents of zip file in current directory
        zipObj.extractall(unzip_to)


def detect_model_folder(model_cache_dir: Union[str, Path]):
    """
    moke model_cache_dir the new folder that created inside
    after extracting the zip archive.
    Args:
    model_cache_dir (Union[str, Path]): Path to the potential model directory.

    Returns:
    Path: Path to the actual model directory.
    """
    if isinstance(model_cache_dir, str):
        model_cache_dir = Path(model_cache_dir)

    all_files = list(model_cache_dir.glob("*"))
    all_paths = [str(i.absolute()) for i in all_files]
    for path in all_paths:
        if os.path.isdir(path):
            model_cache_dir = path
            break

    if isinstance(model_cache_dir, str):
        model_cache_dir = Path(model_cache_dir)

    return model_cache_dir
