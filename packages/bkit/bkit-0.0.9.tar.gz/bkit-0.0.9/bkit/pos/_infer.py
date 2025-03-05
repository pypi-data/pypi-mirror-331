import os
from pathlib import Path

import bkit
from bkit.utils import MODEL_URL_MAP, load_cached_file

from ._helpers import Infer_Pos_Noisy

from spacy import displacy
import spacy



def visualize(pos_data):
    """
    Visualize POS tags using spaCy's displacy with custom colors
    
    Args:
        pos_data: List of tuples containing (word, pos_tag, confidence)
    """
    colors = {
        "PRO": "blueviolet",
        "VF": "lightpink",
        "NNC": "turquoise", 
        "ADJ": "lime",
        "NNP": "khaki",
        "ADV": "orange",
        "CONJ": "cornflowerblue",
        "DET": "forestgreen",
        "QF": "salmon",
        "VNF": "yellow",
        "PUNCT": "gray",
        "PP": "lightblue",
        "PART": "pink",
        "INTJ": "lightgreen"
    }

    text = " ".join([word for word, _, _ in pos_data])
    
    spans = []
    current_pos = 0
    for word, tag, _ in pos_data:
        start = current_pos
        end = start + len(word)
        spans.append((start, end, tag))
        current_pos = end + 1  # +1 for space

    # Create displacy document
    doc = {
        "text": text,
        "ents": [{"start": start, "end": end, "label": tag} 
                 for start, end, tag in spans]
    }

    # Visualization options
    options = {
        "ents": list(colors.keys()),
        "colors": colors
    }

    # Render
    displacy.render(doc, style="ent", options=options, manual=True)


class Infer:
    """
    Args:
        model_name (str): Name of the pre-trained POS model.
        pretrained_model_path (str): Path to a custom pre-trained model directory.
        force_redownload (bool): Flag to force redownload the cached model.

    Attributes:
        model_name (str): Name of the pre-trained POS model.
        infer_class (Infer_Noisy): Inference class for noisy label model or other POS models.
        model_cache_dir (Path): Path to the cached model files.

    Methods:
        __init__(self, model_name: str = None, pretrained_model_path: str = None, force_redownload: bool = False) -> None:
            Initializes the Infer class instance.

        infer(self, text: str = '...') -> dict:
            Perform POS inference on the input text.
    """

    def __init__(
        self,
        model_name: str = None,
        pretrained_model_path: str = None,
        force_redownload: bool = False,
    ) -> None:
        """
        Initializes the Infer class instance.

        Args:
            model_name (str): Name of the pre-trained POS model.
            pretrained_model_path (str): Path to a custom pre-trained model directory.
            force_redownload (bool): Flag to force redownload if the model is not cached.
        """
        self.model_name = model_name
        cache_dir = Path(bkit.ML_MODELS_CACHE_DIR)
        model_cache_dir = cache_dir / f"{model_name}"

        if self.model_name == "pos-noisy-label":
            self.infer_class = Infer_Pos_Noisy

        if pretrained_model_path and os.path.exists(pretrained_model_path):
            self.infer_class = self.infer_class(pretrained_model_path)
        else:
            if model_name not in MODEL_URL_MAP and not os.path.exists(model_cache_dir):
                raise Exception(
                    "model name not found in download map and no model cache directory found"
                )

            # load the model files from cache directory or force download and save in cache
            self.model_cache_dir = load_cached_file(
                model_name, force_redownload=force_redownload
            )
            self.infer_class = self.infer_class(self.model_cache_dir)

    def __call__(self, text: str) -> dict:
        """
        Perform POS inference on the input text.

        Args:
            text (str): Input text for POS inference.

        Returns:
            dict: Dictionary containing POS inference results.
        """
        result = self.infer_class.infer(text)
        return result
