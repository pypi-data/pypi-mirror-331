from __future__ import absolute_import  # noqa
from __future__ import division  # noqa
from __future__ import print_function  # noqa

CUDA_LAUNCH_BLOCKING = "1"  # noqa

from pathlib import Path
from typing import List, Tuple, Union

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import transformers
import yaml
from torch.utils.data import DataLoader
from transformers import (
    AutoConfig,
    AutoModelForPreTraining,
    AutoTokenizer,
    PreTrainedTokenizer,
)

from bkit.utils import preprocess_text





LABEL_TO_ID = {
    "B-PER": 0,
    "I-PER": 1,
    "B-ORG": 2,
    "I-ORG": 3,
    "B-LOC": 4,
    "I-LOC": 5,
    "B-GPE": 6,
    "I-GPE": 7,
    "B-EVENT": 8,
    "I-EVENT": 9,
    "B-NUM": 10,
    "I-NUM": 11,
    "B-UNIT": 12,
    "I-UNIT": 13,
    "B-D&T": 14,
    "I-D&T": 15,
    "B-T&T": 16,
    "I-T&T": 17,
    "B-MISC": 18,
    "I-MISC": 19,
    "O": 20,
}
ID_TO_LABEL = {v: k for k, v in LABEL_TO_ID.items()}
VOCAB = list(LABEL_TO_ID.keys())


def collate_func(batch: List) -> dict:
    """
    Creates a batch of data by padding to the max sequence length of
    the batch.
    Args:
        batch (List): List of instances to be collated into a batch.

    Returns:
        dict: Dictionary containing collated batch data.
    """

    global LABEL_TO_ID
    n_models = batch[0]["n_models"]
    input_ids, attention_mask, labels = (
        [[]] * n_models,
        [[]] * n_models,
        [[]] * n_models,
    )

    for i in range(n_models):
        max_len = max([len(f["input_ids"][i]) for f in batch])
        input_ids[i] = [
            f[f"input_ids"][i] + [0] * (max_len - len(f[f"input_ids"][i]))
            for f in batch
        ]
        attention_mask[i] = [
            [1.0] * len(f["input_ids"][i]) + [0.0] * (max_len - len(f[f"input_ids"][i]))
            for f in batch
        ]
        input_ids[i] = torch.tensor(input_ids[i], dtype=torch.long)
        attention_mask[i] = torch.tensor(attention_mask[i], dtype=torch.float)

        if batch[0]["labels"][0]:
            labels[i] = [
                f["labels"][i] + [len(LABEL_TO_ID)] * (max_len - len(f["labels"][i]))
                for f in batch
            ]

        labels[i] = torch.tensor(labels[i], dtype=torch.long)

    if len(labels[0]) == 0:
        labels = None

    output = {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels,
        "words": [f["words"] for f in batch],
    }
    return output


def process_instance(
    words: List[List[str]],
    labels: List[List[str]],
    tokenizers: List[PreTrainedTokenizer],
    n_models: int,
    embedding_names: List[str],
    max_seq_length=512,
) -> dict:
    """
    Preprocess and tokenize a list of texts splitted into words

    Args:
        words (List[List[str]]): list of sentences to preprocess
        labels (List[List[str]]): NER labels for each sentence
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
            tokens[i][: max_seq_length - 2],
            token_labels[i][: max_seq_length - 2],
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


class CRF(nn.Module):
    """
    Conditional Random Field (CRF) implementation for sequence tagging.

    Methods:
        __init__(self, num_tags: int):
            Initializes the CRF instance.

        forward(self, feats: torch.Tensor) -> torch.Tensor:
            Performs the Viterbi algorithm to predict the best tag sequence.

        loss(self, feats: torch.Tensor, tags: torch.Tensor) -> torch.Tensor:
            Computes the negative log likelihood loss between features and tags.
    """

    def __init__(self, num_tags: int) -> None:
        """
        Initializes the CRF instance.

        Args:
            num_tags (int): Number of tags in the sequence.
        """

        super(CRF, self).__init__()

        self.num_tags = num_tags
        self.transitions = nn.Parameter(torch.Tensor(num_tags, num_tags))
        self.start_transitions = nn.Parameter(torch.randn(num_tags))
        self.stop_transitions = nn.Parameter(torch.randn(num_tags))

        nn.init.xavier_normal_(self.transitions)

    def forward(self, feats):
        # Shape checks
        if len(feats.shape) != 3:
            raise ValueError("feats must be 3-d got {}-d".format(feats.shape))

        return self._viterbi(feats)

    def loss(self, feats: torch.Tensor, tags: torch.Tensor) -> torch.Tensor:
        """
        Computes negative log likelihood between features and tags.
        Essentially difference between individual sequence scores and
        sum of all possible sequence scores (partition function)
        Args:
            feats: Input features [batch size, sequence length, number of tags]
            tags: Target tag indices [batch size, sequence length]. Should be between
                    0 and num_tags
        Returns:
            Negative log likelihood [a scalar]
        """
        # Shape checks
        if len(feats.shape) != 3:
            raise ValueError("feats must be 3-d got {}-d".format(feats.shape))

        if len(tags.shape) != 2:
            raise ValueError("tags must be 2-d but got {}-d".format(tags.shape))

        if feats.shape[:2] != tags.shape:
            raise ValueError("First two dimensions of feats and tags must match")

        sequence_score = self._sequence_score(feats, tags)
        partition_function = self._partition_function(feats)
        log_probability = sequence_score - partition_function

        # -ve of l()
        # Average across batch
        return -log_probability.mean()

    def _sequence_score(self, feats: torch.Tensor, tags: torch.Tensor) -> torch.Tensor:
        """
        Args:
            feats: Input features [batch size, sequence length, number of tags]
            tags: Target tag indices [batch size, sequence length]. Should be between
                    0 and num_tags
        Returns: Sequence score of shape [batch size]
        """

        batch_size = feats.shape[0]

        # Compute feature scores
        feat_score = feats.gather(2, tags.unsqueeze(-1)).squeeze(-1).sum(dim=-1)

        # Compute transition scores
        # Unfold to get [from, to] tag index pairs
        tags_pairs = tags.unfold(1, 2, 1)

        # Use advanced indexing to pull out required transition scores
        indices = tags_pairs.permute(2, 0, 1).chunk(2)
        trans_score = self.transitions[indices].squeeze(0).sum(dim=-1)

        # Compute start and stop scores
        start_score = self.start_transitions[tags[:, 0]]
        stop_score = self.stop_transitions[tags[:, -1]]

        return feat_score + start_score + trans_score + stop_score

    def _partition_function(self, feats: torch.Tensor) -> torch.Tensor:
        """
        Computes the partitition function for CRF using the forward algorithm.
        Basically calculate scores for all possible tag sequences for
        the given feature vector sequence
        Args:
            feats: Input features [batch size, sequence length, number of tags]
        Returns:
            Total scores of shape [batch size]
        """
        _, seq_size, num_tags = feats.shape

        if self.num_tags != num_tags:
            raise ValueError(
                "num_tags should be {} but got {}".format(self.num_tags, num_tags)
            )

        # [batch_size, num_tags]
        a = feats[:, 0] + self.start_transitions.unsqueeze(0)
        transitions = self.transitions.unsqueeze(
            0
        )  # [1, num_tags, num_tags] from -> to

        for i in range(1, seq_size):
            feat = feats[:, i].unsqueeze(1)  # [batch_size, 1, num_tags]
            # [batch_size, num_tags]
            a = self._log_sum_exp(a.unsqueeze(-1) + transitions + feat, 1)

        # [batch_size]
        return self._log_sum_exp(a + self.stop_transitions.unsqueeze(0), 1)

    def _viterbi(self, feats: torch.Tensor) -> torch.Tensor:
        """
        Uses Viterbi algorithm to predict the best sequence
        Args:
            feats: Input features [batch size, sequence length, number of tags]
        Returns: Best tag sequence [batch size, sequence length]
        """
        _, seq_size, num_tags = feats.shape

        if self.num_tags != num_tags:
            raise ValueError(
                "num_tags should be {} but got {}".format(self.num_tags, num_tags)
            )

        # [batch_size, num_tags]
        v = feats[:, 0] + self.start_transitions.unsqueeze(0)
        transitions = self.transitions.unsqueeze(
            0
        )  # [1, num_tags, num_tags] from -> to
        paths = []

        for i in range(1, seq_size):
            feat = feats[:, i]  # [batch_size, num_tags]
            # [batch_size, num_tags], [batch_size, num_tags]
            v, idx = (v.unsqueeze(-1) + transitions).max(1)

            paths.append(idx)
            v = v + feat  # [batch_size, num_tags]

        v, tag = (v + self.stop_transitions.unsqueeze(0)).max(1, True)

        # Backtrack
        tags = [tag]
        for idx in reversed(paths):
            tag = idx.gather(1, tag)
            tags.append(tag)

        tags.reverse()
        return torch.cat(tags, 1)

    def _log_sum_exp(self, logits: torch.Tensor, dim: int) -> torch.Tensor:
        """
        Computes log-sum-exp in a stable way.

        Args:
            logits (torch.Tensor): Logits to compute log-sum-exp on.
            dim (int): Dimension along which to perform the operation.

        Returns:
            torch.Tensor: Result of the log-sum-exp operation.
        """
        max_val, _ = logits.max(dim)
        return max_val + (logits - max_val.unsqueeze(dim)).exp().sum(dim).log()


class NERModel(nn.Module):
    """Base NER model used for NER classification."""

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

        config = AutoConfig.from_pretrained(model_name, output_hidden_states=True)
        self.dropout = nn.Dropout(model_config["dropout_prob"])
        if model_config["gtlms"]:
            if embedding_name == "bert":
                self.model = transformers.BertModel(config=config)

        elif embedding_name == "xlnet":
            config = AutoConfig.from_pretrained(
                model_name, bi_data=False, output_hidden_states=True
            )
            self.model = AutoModelForPreTraining.from_pretrained(
                model_name, config=config
            )
        elif embedding_name == "t5":
            self.model = transformers.T5EncoderModel.from_pretrained(
                model_name, config=config
            )
        else:
            self.model = AutoModelForPreTraining.from_pretrained(
                model_name, config=config
            )

        self.rnn = nn.LSTM(
            bidirectional=True,
            num_layers=4,
            dropout=0.5,
            input_size=config.hidden_size,
            hidden_size=config.hidden_size // 2,
            batch_first=True,
        )
        self.classifier = nn.Sequential(
            nn.Linear(config.hidden_size, 512),
            nn.Dropout(0.5),
            nn.Linear(512, num_class + 1),
        )

        # dummy weights provided to loss funciton - only used to avoid error when loading model checkpoint
        self.loss_fnt = nn.CrossEntropyLoss(
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


class NLLModel(nn.Module):
    """Noisy NER model for NER classification"""

    def __init__(
        self,
        model_config: dict,
        num_class: int,
    ) -> None:
        """
        Main model class for NER classification
        Args:
            model_config (dict): contains model related parameters
            num_class (int): number of classes to tag (B-PER,I-PER,etc.)
        """
        super().__init__()

        self.model_name_or_path = model_config["model_name_or_path"]
        self.embedding_names = model_config["embedding_name"]
        self.n_model = len(self.model_name_or_path)
        self.best_model_index = model_config["best_model_index"]
        self.models = nn.ModuleList()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.loss_fnt = nn.CrossEntropyLoss()

        for i in range(self.n_model):
            model = NERModel(
                model_config,
                num_class,
                self.model_name_or_path[i],
                self.embedding_names[i],
            )
            model.to(self.device)
            self.models.append(model)

    def forward(
        self, input_ids: List[torch.Tensor], attention_mask: List[torch.Tensor]
    ) -> Tuple[torch.Tensor]:
        b_idx = self.best_model_index
        return self.models[b_idx](
            input_ids=input_ids[b_idx].to(self.device),
            attention_mask=attention_mask[b_idx].to(self.device),
        )


class Infer_Noisy:
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
                    AutoTokenizer.from_pretrained(
                        model_name_or_path[i], keep_accents=True
                    )
                )
            else:
                self.tokenizers.append(
                    AutoTokenizer.from_pretrained(model_name_or_path[i])
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
            w_preproc = preprocess_text(word)
            if w_preproc is not None:
                if len(w_preproc) > 0:
                    words.append(w_preproc)
                else:
                    words.append(word)

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
