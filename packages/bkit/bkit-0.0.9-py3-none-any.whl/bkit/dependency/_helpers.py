import os
from pathlib import Path
from typing import Dict, List, Union, Optional
import numpy as np
import onnxruntime
from transformers import T5Tokenizer
import regex as re
import string

def format_input(text: str) -> str:
    tokens = re.findall(r'[০-৯]+\.[০-৯]*|[\p{L}\p{M}\p{N}]+(?:[-/–][\p{L}\p{M}\p{N}]+)*|[!?.,:;]+|[-/]|[^\s\p{L}\p{M}\p{N}/-]', text)
    output_tokens = "".join([f"{token}{i+1}<fun_spt>" for i, token in enumerate(tokens)])
    text_processed = " ".join(tokens)
    return output_tokens, text_processed

def parse_dependency_format(text: str, dependency_parse: str) -> Dict:
    results = []
    relations = dependency_parse.split("<fun_spt>")
    for relation in relations:
        if not relation.strip():
            continue
        
        parts = relation.split()
        token = parts[0]
        label_with_brackets = parts[-2]
        head = int(parts[-1]) - 1
        label = label_with_brackets.strip("[]")
        is_root = (label == "root")
        
        token_end = len(results)
        token_start = head
        
        # entry_id = f"{token_start}_{token_end}_{label}"
        results.append({
            'token_start': token_start,
            'token_end': token_end,
            'label': label,
        })
    return {
        "text": text,
        "predictions": results
    }



class Infer_Dependency_Parser:
 
    def __init__(self, model_path: Union[str, Path] = None) -> None:
        
        self.model_path = model_path
        self.t5_model_path = Path(self.model_path) / 'model.onnx'        
        try:
            self.tokenizer = T5Tokenizer.from_pretrained(self.model_path)
            self.session = onnxruntime.InferenceSession(self.t5_model_path)
            
        except Exception as e:
            raise Exception(f"Failed to load model from {model_path}: {str(e)}")
        
        # Set configuration parameters
        self.max_length = 512
        self.max_new_tokens =  512

    def _sequential_decode(self, input_ids: np.ndarray, attention_mask: np.ndarray) -> List[int]:
        decoder_input_ids = np.array([[self.tokenizer.pad_token_id]], dtype=np.int32)
        generated_tokens = []
        
        for _ in range(self.max_new_tokens):
            # Prepare inputs for current step
            ort_inputs = {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "decoder_input_ids": decoder_input_ids
            }
            
            # Get predictions
            outputs = self.session.run(None, ort_inputs)
            logits = outputs[0]
            
            # Get next token
            next_token = np.argmax(logits[0, -1])
            generated_tokens.append(next_token)
            
            # Break if end of sequence
            if next_token == self.tokenizer.eos_token_id:
                break
                
            # Update decoder input
            decoder_input_ids = np.concatenate([
                decoder_input_ids,
                np.array([[next_token]], dtype=np.int32)
            ], axis=1)
        
        return generated_tokens

    def _process_single(self, text: str) -> Dict:
        
        # Format input
        formatted_tokens,processed_text = format_input(text)
        
        # Tokenize
        encoder_inputs = self.tokenizer(
            formatted_tokens,
            return_tensors="pt",
            max_length=self.max_length,
            padding="max_length",
            truncation=True
        )
        
        # Convert to numpy
        input_ids = encoder_inputs['input_ids'].numpy().astype(np.int32)
        attention_mask = encoder_inputs['attention_mask'].numpy().astype(np.int32)
        
        # Generate tokens
        generated_tokens = self._sequential_decode(input_ids, attention_mask)
        
        # Decode prediction
        decoded_pred = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
        
        # Parse and return results
        return parse_dependency_format(processed_text, decoded_pred)

    def _split_into_sentences(self, text: str) -> List[str]:
       
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            if char == '।':
                if current_sentence.strip():
                    sentences.append(current_sentence.strip())
                current_sentence = ""
                
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
            
        return sentences

    def infer(self, text: str) -> List[Dict]:
        
        # Split text into sentences
        sentences = self._split_into_sentences(text)
        
        # Process each sentence
        results = [self._process_single(sent) for sent in sentences]
        
        return results
