import os
from pathlib import Path
from typing import Dict, List
import bkit
from bkit.utils import MODEL_URL_MAP, load_cached_file

from ._helpers import Infer_Dependency_Parser

import regex as re
import spacy
from spacy import displacy
from spacy.tokens import Doc
import numpy as np
import string



def create_doc_from_predictions(text, predictions):
    nlp = spacy.blank("bn")  
    
    words = text.split()
    doc = Doc(nlp.vocab, words=words)
    
    heads = np.array([len(doc) - 1] * len(doc), dtype=np.int32)
    deps = [""] * len(doc)
    
    # Process predictions
    for pred in predictions:
        head_idx = pred['token_start']
        dep_idx = pred['token_end']
        dep_label = pred['label']
        
        # Set the head and dependency label
        if dep_idx < len(heads):
            heads[dep_idx] = head_idx
            deps[dep_idx] = dep_label
    
    # Set heads and deps
    for token, head, dep in zip(doc, heads, deps):
        token.head = doc[head]
        token.dep_ = dep
    
    return doc

def visualize(data):
    text = data[0]['text']
    predictions = data[0]['predictions']
    
    doc = create_doc_from_predictions(text, predictions)
    options = {
        "compact": False,
        "font": "Source Sans Pro",
        "collapse_punct": False,
        "distance": 120,
        "arrow_stroke": 2,
        "arrow_width": 8,
        "arrow_spacing": 12
    }
    # Generate visualization
    svg = displacy.render(doc, style="dep",jupyter=True,options=options)
    
    return svg




class Infer:
    def __init__(
        self,
        model_name: str = None,
        pretrained_model_path: str = None,
        force_redownload: bool = False,
    ) -> None:
        self.model_name = model_name
        cache_dir = Path(bkit.ML_MODELS_CACHE_DIR)
        model_cache_dir = cache_dir / f"{model_name}"

        if self.model_name == "dependency-parsing":
            self.infer_class = Infer_Dependency_Parser

        if pretrained_model_path and os.path.exists(pretrained_model_path):
            self.infer_class = self.infer_class(pretrained_model_path)
        else:
            if model_name not in MODEL_URL_MAP and not os.path.exists(model_cache_dir):
                raise Exception(
                    'model name not found in download map and no model cache directory found')

            # load the model files from cache directory or force download and save in cache
            self.model_cache_dir = load_cached_file(
                model_name, force_redownload=force_redownload)
            self.infer_class = self.infer_class(self.model_cache_dir)

    def __call__(self, text: str) -> List[Dict]:
       
        results = self.infer_class.infer(text)
        return results