import os
from pathlib import Path

import bkit
from bkit.utils import MODEL_URL_MAP, load_cached_file

from ._helpers import Infer_Coreference

import spacy
from spacy import displacy
from spacy.tokens import Doc, Span
from typing import Dict, List
import random

def visualize(coref_output: Dict) -> None:
 
    nlp = spacy.blank("bn")
    
    # Create a Doc object from the tokens
    words = coref_output['text']
    spaces = [True] * (len(words) - 1) + [False]
    doc = Doc(nlp.vocab, words=words, spaces=spaces)
    
    FIXED_COLORS = [
        "#E69F00",  # Orange
        "#56B4E9",  # Light blue
        "#009E73",  # Green
        "#CC79A7",  # Pink
        "#0072B2",  # Dark blue
        "#D55E00",  # Red
        "#F0E442",  # Yellow
        "#999999",  # Grey
        "#44AA99",  # Teal
        "#882255",  # Purple
    ]
    
    def get_random_color():
        """Generate a random color that's not too light (for visibility)"""
        hue = random.random()
        saturation = random.uniform(0.6, 0.9)
        value = random.uniform(0.5, 0.9)
        
        # Convert HSV to RGB
        h = hue * 6
        i = int(h)
        f = h - i
        p = value * (1 - saturation)
        q = value * (1 - f * saturation)
        t = value * (1 - (1 - f) * saturation)
        
        if i == 0:
            r, g, b = value, t, p
        elif i == 1:
            r, g, b = q, value, p
        elif i == 2:
            r, g, b = p, value, t
        elif i == 3:
            r, g, b = p, q, value
        elif i == 4:
            r, g, b = t, p, value
        else:
            r, g, b = value, p, q
        
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
    
    # Create entities for visualization
    ents = []
    colors = {}
    
    for cluster_id, mentions in coref_output['mention_indices'].items():
        if cluster_id < len(FIXED_COLORS):
            color = FIXED_COLORS[cluster_id]
        else:
            color = get_random_color()
        
        colors[f"COREF_{cluster_id}"] = color
        
        for mention in mentions:
            start_idx = mention['start_token']
            end_idx = mention['end_token'] + 1
            span = Span(doc, start_idx, end_idx, label=f"COREF_{cluster_id}")
            ents.append(span)
    
    doc.ents = ents
    
    options = {
        "ents": [f"COREF_{i}" for i in coref_output['mention_indices'].keys()],
        "colors": colors,
        "ent_spacing": 10
    }
    
    # Display the visualization
    displacy.render(doc, style="ent", options=options, jupyter=True)


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

        if self.model_name == "coref":
            self.infer_class = Infer_Coreference

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
