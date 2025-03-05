import os
from pathlib import Path

import bkit
from bkit.utils import MODEL_URL_MAP, load_cached_file

from ._helpers import Infer_Noisy

import spacy
from spacy.tokens import Doc, Span
from spacy import displacy
import random



def generate_random_color():
    return f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"

def visualize(predictions):
    """
    Visualize NER predictions using spaCy's displacy and inline format.
    
    Args:
        predictions (list of tuples): A list of tuples with (token, label, confidence).
                                      Example: [('তুমি', 'O', 0.999), ('ঢাকা', 'B-GPE', 0.998)]
    """
    nlp = spacy.blank("bn")  # 'bn' for Bangla (you can use any language)

    # Extract tokens and entities
    tokens = [token for token, _, _ in predictions]
    entities = []
    start = 0
    current_entity = None

    # Process predictions to handle B- and I- labels
    for i, (token, label, _) in enumerate(predictions):
        if label.startswith("B-"):  # Start of a new entity
            if current_entity:  # Close previous entity if any
                entities.append((current_entity["start"], current_entity["end"], current_entity["label"]))
            current_entity = {"start": start, "end": start + 1, "label": label.split("-")[1]}
        elif label.startswith("I-") and current_entity and current_entity["label"] == label.split("-")[1]:
            # Extend the current entity
            current_entity["end"] += 1
        else:
            if current_entity:  # Close previous entity
                entities.append((current_entity["start"], current_entity["end"], current_entity["label"]))
                current_entity = None
        start += 1

    # Add the last entity if still open
    if current_entity:
        entities.append((current_entity["start"], current_entity["end"], current_entity["label"]))

    doc = Doc(nlp.vocab, words=tokens)

    spans = [Span(doc, start, end, label=label) for start, end, label in entities]
    doc.ents = spans  

    specific_colors = {
        "NUM": "#FFD700",  
        "UNIT": "#00BFFF",  
        "PER": "#FF4500",  
        "ORG": "#7CFC00",  
        "D&T": "#8A2BE2",  
        "GPE": "#FF69B4", 
        "LOC": "#00FA9A", 
        "EVENT": "#4B0082", 
        "T&T": "#DC143C", 
        "MISC": "#FF8C00"  
    }

    unique_labels = {label for _, _, label in entities}
    colors = {label: specific_colors.get(label, generate_random_color()) for label in unique_labels}
    options = {"colors": colors}

    displacy.render(doc, style="ent", jupyter=True, options=options)





class Infer:
    """
    Attributes:
        model_name (str): Name of the pre-trained NER model.
        infer_class (Infer_Noisy): Inference class for noisy label model or other NER models.
        model_cache_dir (Path): Path to the cached model files.

    Methods:
        __init__(self, model_name: str = None, pretrained_model_path: str = None, force_redownload: bool = False) -> None:
            Initializes the Infer class instance.

        infer(self, text: str = '...') -> dict:
            Perform NER inference on the input text.
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
            model_name (str): Name of the pre-trained NER model.
            pretrained_model_path (str): Path to a custom pre-trained model directory.
            force_redownload (bool): Flag to force redownload if the model is not cached.
        """
        self.model_name = model_name
        cache_dir = Path(bkit.ML_MODELS_CACHE_DIR)
        model_cache_dir = cache_dir / f"{model_name}"

        if self.model_name == "ner-noisy-label":
            self.infer_class = Infer_Noisy

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
        Perform NER inference on the input text.

        Args:
            text (str): Input text for NER inference.

        Returns:
            dict: Dictionary containing NER inference results.
        """
        result = self.infer_class.infer(text)
        return result
