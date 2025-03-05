import numpy as np
import torch
import torch.nn as nn

from bkit.shallow.utils import from_numpy

from .encoder import LayerNormalization


class CharacterLSTM(nn.Module):
    """
    A class representing a Character-level LSTM module.

    This module takes character embeddings as input and processes them using
    an LSTM layer. It can optionally apply layer normalization to the output.

    :param num_embeddings: Number of unique characters in the character vocabulary.
    :param d_embedding: Size of the character embeddings.
    :param d_out: Size of the output after LSTM processing.
    :param char_dropout: Dropout probability for character embeddings.
    :param normalize: Flag indicating whether to apply layer normalization.
    :param **kwargs: Additional keyword arguments for character embeddings.
    """

    def __init__(
        self,
        num_embeddings,
        d_embedding,
        d_out,
        char_dropout=0.0,
        normalize=False,
        **kwargs,
    ):
        super().__init__()

        self.d_embedding = d_embedding
        self.d_out = d_out

        self.lstm = nn.LSTM(
            self.d_embedding, self.d_out // 2, num_layers=1, bidirectional=True
        )

        self.emb = nn.Embedding(num_embeddings, self.d_embedding, **kwargs)
        self.char_dropout = nn.Dropout(char_dropout)

        if normalize:
            print("This experiment: layer-normalizing after character LSTM")
            self.layer_norm = LayerNormalization(self.d_out, affine=False)
        else:
            self.layer_norm = lambda x: x

    def forward(self, chars_padded_np, word_lens_np, batch_idxs):
        """
        Forward pass of the CharacterLSTM module.

        :param chars_padded_np: Padded character sequences as a NumPy array.
        :param word_lens_np: Array of word lengths for each sequence.
        :param batch_idxs: Indices of sequences in the batch.
        :return: Processed character embeddings after LSTM and normalization.
        """
        decreasing_idxs_np = np.argsort(word_lens_np)[::-1].copy()
        decreasing_idxs_torch = from_numpy(decreasing_idxs_np)

        chars_padded = from_numpy(chars_padded_np[decreasing_idxs_np])
        word_lens = from_numpy(word_lens_np[decreasing_idxs_np])

        inp_sorted = nn.utils.rnn.pack_padded_sequence(
            chars_padded, word_lens_np[decreasing_idxs_np], batch_first=True
        )
        inp_sorted_emb = nn.utils.rnn.PackedSequence(
            self.char_dropout(self.emb(inp_sorted.data)), inp_sorted.batch_sizes
        )
        _, (lstm_out, _) = self.lstm(inp_sorted_emb)

        lstm_out = torch.cat([lstm_out[0], lstm_out[1]], -1)

        # Undo sorting by decreasing word length
        res = torch.zeros_like(lstm_out)
        res.index_copy_(0, decreasing_idxs_torch, lstm_out)

        res = self.layer_norm(res)
        return res


def get_bert(bert_model, bert_do_lower_case, hpara=None):
    """
    Get a pre-trained BERT model and tokenizer.

    :param bert_model: Name or path of the BERT pre-trained model.
    :param bert_do_lower_case: Flag indicating whether to convert text to lowercase.
    :param hpara: Hyperparameters (optional).
    :return: BERT tokenizer and pre-trained BERT model.
    """

    # Avoid a hard dependency on BERT by only importing it if it's being used
    from transformers import BertModel, BertTokenizer

    if hpara is None:
        if bert_model.endswith(".tar.gz"):
            tokenizer = BertTokenizer.from_pretrained(
                bert_model, do_lower_case=bert_do_lower_case
            )
        else:
            tokenizer = BertTokenizer.from_pretrained(
                bert_model, do_lower_case=bert_do_lower_case
            )
        bert = BertModel.from_pretrained(bert_model)
    else:
        tokenizer = hpara["bert_tokenizer"]
        # print("hpara", hpara['config'])
        bert = BertModel(hpara["config"])
    return tokenizer, bert


def get_xlnet(xlnet_model, xlnet_do_lower_case, hpara=None):
    """
    Get a pre-trained XLNet model and tokenizer.

    :param xlnet_model: Name or path of the XLNet pre-trained model.
    :param xlnet_do_lower_case: Flag indicating whether to convert text to lowercase.
    :param hpara: Hyperparameters (optional).
    :return: XLNet tokenizer and pre-trained XLNet model.
    """

    # Avoid a hard dependency on BERT by only importing it if it's being used
    from transformers import XLNetModel, XLNetTokenizer

    if hpara is None:
        tokenizer = XLNetTokenizer.from_pretrained(
            xlnet_model, do_lower_case=xlnet_do_lower_case
        )
        xlnet = XLNetModel.from_pretrained(xlnet_model)
    else:
        tokenizer = hpara["xlnet_tokenizer"]
        xlnet = XLNetModel(hpara["config"])

    return tokenizer, xlnet
