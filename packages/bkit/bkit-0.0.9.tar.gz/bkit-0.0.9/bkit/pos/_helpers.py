from pathlib import Path
from typing import List, Tuple, Union

import numpy as np
import torch
import torch.nn.functional as F
import transformers
import yaml
from torch.utils.data import DataLoader

from bkit.ner._helpers import CRF, NLLModel, collate_func
from bkit.utils import preprocess_text





LABEL_TO_ID = {
    "ADJ": 0,
    "ADV": 1,
    "CONJ": 2,
    "DET": 3,
    "INTJ": 4,
    "NNC": 5,
    "NNP": 6,
    "OTH": 7,
    "PART": 8,
    "PP": 9,
    "PRO": 10,
    "PUNCT": 11,
    "QF": 12,
    "VF": 13,
    "VNF": 14,
}
VOCAB = list(LABEL_TO_ID.keys())
ID_TO_LABEL = {v: k for k, v in LABEL_TO_ID.items()}


def process_instance(
    words: List[List[str]],
    labels: List[List[str]],
    tokenizers: List[transformers.PreTrainedTokenizer],
    n_models: int,
    embedding_names: List[str],
    max_seq_length=512,
) -> dict:
    """
    Preprocess and tokenize a list of texts splitted into words
    Args:
        words (List[List[str]]): list of sentences to preprocess
        labels (List[List[str]]): POS labels for each sentence
        tokenizers (List[PreTrainedTokenizer]): list of tokenizers for each model
        n_models (int): number of models
        embedding_names (List[str]): model names of each model
        max_seq_length (int, optional): max length for each sequence. Defaults to 512.

    Returns:
        A dictionary containing input ids, labels, words and
    """
    global VOCAB, LABEL_TO_ID, ID_TO_LABEL

    tokens, token_labels, input_ids = [[]] * n_models, [[]] * n_models, [[]] * n_models

    for i in range(n_models):
        for word, label in zip(words, labels):
            tokenized = tokenizers[i].tokenize(word)

            token_label = [LABEL_TO_ID[label]] + [len(LABEL_TO_ID)] * (
                len(tokenized) - 1
            )
            if len(tokenized) == 0:
                tokens[i] = tokens[i] + [word]
            else:
                tokens[i] = tokens[i] + tokenized
            token_labels[i] = token_labels[i] + token_label

        tokens[i], token_labels[i] = (
            tokens[i][: max_seq_length - 3],
            token_labels[i][: max_seq_length - 3],
        )
        input_ids[i] = tokenizers[i].convert_tokens_to_ids(tokens[i])
        input_ids[i] = tokenizers[i].build_inputs_with_special_tokens(input_ids[i])

        # check whether there are special ids appended to beginning or end of the sequence
        if input_ids[i][0] in tokenizers[i].all_special_ids:
            token_labels[i] = [len(LABEL_TO_ID)] + token_labels[i]
        if input_ids[i][-1] in tokenizers[i].all_special_ids:
            if embedding_names[i] == "xlnet":
                token_labels[i] = token_labels[i] + [len(LABEL_TO_ID)] * 2
            else:
                token_labels[i] = token_labels[i] + [len(LABEL_TO_ID)]

        assert len(token_labels[i]) == len(input_ids[i]), print(
            "token_labels",
            token_labels[i],
            len(token_labels[i]),
            "\n",
            "input_ids",
            input_ids[i],
            len(input_ids[i]),
        )

    return {
        "input_ids": input_ids,
        "labels": token_labels,
        "words": words,
        "n_models": n_models,
    }


class POSModel(torch.nn.Module):
    """Base PoS model used for PoS classification."""

    def __init__(
        self,
        model_config: dict,
        num_class: int,
        model_name: Union[str, Path] = None,
        embedding_name: str = None,
    ) -> None:
        """
        Args:
            model_config (dict): contains model related parameters
            num_class (int): _description_
            model_name (Path/str, optional): pretrained language model path containing model config and weights. Defaults to None.
            embedding_name (str, optional): language model type (bert,electra,gpt2,t5,xlnet,etc.). Defaults to None.
        """
        super().__init__()

        config = transformers.AutoConfig.from_pretrained(
            model_name, output_hidden_states=True
        )
        self.dropout = torch.nn.Dropout(model_config["dropout_prob"])
        if model_config["gtlms"]:
            if embedding_name == "bert":
                self.model = transformers.BertModel(config=config)

        elif embedding_name == "xlnet":
            config = transformers.AutoConfig.from_pretrained(
                model_name, bi_data=False, output_hidden_states=True
            )
            self.model = transformers.AutoModelForPreTraining.from_pretrained(
                model_name, config=config
            )
        elif embedding_name == "t5":
            self.model = transformers.T5EncoderModel.from_pretrained(
                model_name, config=config
            )
        else:
            self.model = transformers.AutoModelForPreTraining.from_pretrained(
                model_name, config=config
            )

        self.rnn = torch.nn.LSTM(
            bidirectional=True,
            num_layers=4,
            dropout=0.5,
            input_size=config.hidden_size,
            hidden_size=config.hidden_size // 2,
            batch_first=True,
        )
        self.classifier = torch.nn.Sequential(
            torch.nn.Linear(config.hidden_size, 512),
            torch.nn.Dropout(0.5),
            torch.nn.Linear(512, num_class + 1),
        )

        # dummy weights provided to loss funciton - only used to avoid error when loading model checkpoint
        self.loss_fnt = torch.nn.CrossEntropyLoss(
            weight=torch.FloatTensor(torch.ones(num_class + 1))
        )
        self.crf = CRF(num_class + 1)
        self.finetuning = True
        self.num_class = num_class

    def forward(
        self, input_ids: List[torch.Tensor], attention_mask: List[torch.Tensor]
    ) -> Tuple[torch.Tensor]:
        self.model.eval()
        with torch.no_grad():
            enc = self.model(input_ids, attention_mask).hidden_states[-1]

        h, _ = self.rnn(enc)
        logits_focal = self.classifier(h)
        y_hat = self.crf.forward(logits_focal)
        return logits_focal, y_hat


class Infer_Pos_Noisy:
    """
    Class for making noisy label inference using a pre-trained NLL model.

    Attributes:
        config (dict): Model configuration loaded from `config.yaml`.
        device (torch.device): Device used for inference.
        n_model (int): Number of models for inference.
        tokenizers (list): List of tokenizers for each model.
        model (NLLModel): Pre-trained NLL model for inference.

    Methods:
        __init__(self, model_path: Union[str,Path] = None) -> None:
            Initializes the Infer_Noisy class instance.

        infer(self, text: str) -> dict:
            Perform noisy label inference on input text.

    """

    def __init__(self, model_path: Union[str, Path] = None) -> None:
        """
        Initializes the Infer_Noisy class instance.

        Args:
            model_path (Union[str, Path]): Path to the directory containing model files.
        """
        global VOCAB, LABEL_TO_ID, ID_TO_LABEL

        self.config = yaml.safe_load(open(f"{str(model_path)}/config.yaml", "r"))

        if isinstance(model_path, str):
            model_path = Path(model_path)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model_name_or_path = self.config["model_name_or_path"]
        model_name_or_path = [model_path / p for p in model_name_or_path]

        self.n_model = len(model_name_or_path)
        self.tokenizers = []
        for i in range(self.n_model):
            if self.config["embedding_name"][i] == "xlnet":
                self.tokenizers.append(
                    transformers.AutoTokenizer.from_pretrained(
                        model_name_or_path[i], keep_accents=True
                    )
                )
            else:
                self.tokenizers.append(
                    transformers.AutoTokenizer.from_pretrained(model_name_or_path[i])
                )

        self.config["model_name_or_path"] = model_name_or_path
        self.model = NLLModel(self.config, len(LABEL_TO_ID))

        self.model.load_state_dict(
            torch.load(model_path / self.config["model_file"], map_location=self.device)
        )

    def infer(self, text: str) -> dict:
        """
        Perform noisy label inference on input text.

        Args:
            text (str): Input text for inference.

        Returns:
            dict: Dictionary containing inference results.
        """
        # words = text.split()
        words = []
        for word in text.split():
            w_preporc = preprocess_text(word)
            if len(w_preporc) > 0:
                words.append(w_preporc)

        words_list = [words]
        labels_list = [[VOCAB[-1]] * len(text.split())]
        train_features = []

        for words, labels in zip(words_list, labels_list):
            train_features.append(
                process_instance(
                    words,
                    labels,
                    tokenizers=self.tokenizers,
                    n_models=self.n_model,
                    embedding_names=self.config["embedding_name"],
                )
            )

        batch_size = self.config["batch_size"]
        dataloader = DataLoader(
            train_features,
            batch_size=batch_size,
            shuffle=False,
            collate_fn=collate_func,
            drop_last=False,
        )

        inference_result = {}
        preds, probs, all_sen = [], [], []

        for batch in dataloader:
            self.model.eval()

            with torch.no_grad():
                logits, y_hat = self.model(
                    input_ids=batch["input_ids"], attention_mask=batch["attention_mask"]
                )
                # remove the last label prediction logit while inference
                batch_probs = (
                    F.softmax(logits[:, :, :-1], dim=-1).detach().cpu().numpy()
                )

                msk = batch["labels"][0] != len(LABEL_TO_ID)
                msk = msk.cpu().numpy()

                # select the tokens which are not subtoken
                batch_probs_masked = [
                    batch_probs[i, msk[i]] for i in range(len(batch_probs))
                ]

                probs_masked = [
                    np.amax(batch_probs_masked[i], axis=-1)
                    for i in range(len(batch_probs_masked))
                ]
                batch_probs_preds = [
                    np.argmax(batch_probs_masked[i], axis=-1)
                    for i in range(len(batch_probs_masked))
                ]
                y_hat = y_hat.cpu().numpy()
                pred_masked = [y_hat[i, msk[i]] for i in range(len(y_hat))]

                for i in range(len(pred_masked)):
                    invalid_idxs = np.argwhere(pred_masked[i] == len(LABEL_TO_ID))
                    invalid_idxs = invalid_idxs.flatten()
                    # replace crf invalid predictions with the predictions from linear layer
                    # crf can sometimes predict pad tokens
                    pred_masked[i][invalid_idxs] = batch_probs_preds[i][invalid_idxs]

                pred_masked = [
                    map(lambda x: ID_TO_LABEL[x], prediction)
                    for prediction in pred_masked
                ]

            preds.extend(pred_masked)
            probs.extend(probs_masked)
            all_sen.extend(batch["words"])

        for i, s in enumerate(all_sen):
            pred_sen = []
            for word, pred, prob in zip(s, preds[i], probs[i]):
                pred_sen.append((word, pred, prob))
            inference_result[f"prediction_sen_{i}"] = pred_sen

        return inference_result["prediction_sen_0"]
