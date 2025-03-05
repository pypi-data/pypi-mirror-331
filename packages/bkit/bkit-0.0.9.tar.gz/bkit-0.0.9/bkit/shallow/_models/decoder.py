import numpy as np
import pyximport
import torch
import torch.nn as nn

pyximport.install(setup_args={"include_dirs": np.get_include()})

from bkit.shallow.dataloaders import trees
from bkit.shallow.utils import from_numpy, nkutil, token, use_cuda

from . import chart_helper
from .embeddings import CharacterLSTM, get_bert, get_xlnet
from .encoder import Encoder, LayerNormalization, MultiLevelEmbedding
from .span_attentions import SpanNgramAttentions


class BatchIndices:
    """
    Batch indices container class (used to implement packed batches)
    """

    def __init__(self, batch_idxs_np):
        self.batch_idxs_np = batch_idxs_np
        # Note that the torch copy will be on GPU if use_cuda is set
        self.batch_idxs_torch = from_numpy(batch_idxs_np)

        self.batch_size = int(1 + np.max(batch_idxs_np))

        batch_idxs_np_extra = np.concatenate([[-1], batch_idxs_np, [-1]])
        self.boundaries_np = np.nonzero(
            batch_idxs_np_extra[1:] != batch_idxs_np_extra[:-1]
        )[0]
        self.seq_lens_np = self.boundaries_np[1:] - self.boundaries_np[:-1]
        assert len(self.seq_lens_np) == self.batch_size
        self.max_len = int(np.max(self.boundaries_np[1:] - self.boundaries_np[:-1]))


class ChartParser(nn.Module):
    """
    ChartParser neural network model for sequence parsing.

    This class defines a neural network architecture for sequence parsing tasks.

    :param tag_vocab: PoS tag vocabulary.
    :param word_vocab: Word vocabulary.
    :param label_vocab: Label vocabulary.
    :param char_vocab: Character vocabulary for character embeddings.
    :param ngram_vocab: N-gram vocabulary for n-gram embeddings.
    :param hparams: Hyperparameters for configuring the model.
    :param restore: Flag indicating whether to restore model weights.
    """

    def __init__(
        self,
        tag_vocab,
        word_vocab,
        label_vocab,
        char_vocab,
        ngram_vocab,
        hparams,
        restore=False,
    ):
        super().__init__()

        # Store function arguments as a specification
        self.spec = locals()
        self.spec.pop("self")
        self.spec.pop("__class__")
        self.spec["hparams"] = hparams.to_dict()
        self.ngram_channels = hparams.ngram

        # Store provided vocabularies
        self.tag_vocab = tag_vocab
        self.word_vocab = word_vocab
        self.label_vocab = label_vocab
        self.char_vocab = char_vocab
        self.ngram_vocab = ngram_vocab

        # Extract model multi head parameters?
        self.d_model = hparams.d_model
        self.partitioned = hparams.partitioned
        self.d_content = (self.d_model // 2) if self.partitioned else self.d_model
        self.d_positional = (hparams.d_model // 2) if self.partitioned else None

        # Maps the number of embeddings and dropout rates for each embedding type
        num_embeddings_map = {
            "tags": tag_vocab.size,
            "words": word_vocab.size,
            "chars": char_vocab.size,
            "ngrams": ngram_vocab.size,
        }
        emb_dropouts_map = {
            "tags": hparams.tag_emb_dropout,
            "words": hparams.word_emb_dropout,
        }

        # Determine which types of embeddings are used
        self.emb_types = []
        if hparams.use_tags:
            self.emb_types.append("tags")
        if hparams.use_words:
            self.emb_types.append("words")

        self.use_tags = hparams.use_tags

        # Set dropout for morphological embeddings
        self.morpho_emb_dropout = None
        if (
            hparams.use_chars_lstm
            or hparams.use_bert
            or hparams.use_bert_only
            or hparams.use_xlnet
            or hparams.use_xlnet_only
        ):
            self.morpho_emb_dropout = hparams.morpho_emb_dropout
        else:
            assert (
                self.emb_types
            ), "Need at least one of: use_chars_lstm, use_bert, use_xlnet"

        # Initialize encoders and tokenizers for different models
        self.char_encoder = None
        self.bert = None
        self.xlnet = None
        use_encoder = False
        if hparams.use_chars_lstm:
            # Initialize CharacterLSTM if using character embeddings
            assert (
                not hparams.use_bert
            ), "use_chars_lstm and use_bert are mutually exclusive"
            assert (
                not hparams.use_bert_only
            ), "use_chars_lstm and use_bert_only are mutually exclusive"
            self.char_encoder = CharacterLSTM(
                num_embeddings_map["chars"],
                hparams.d_char_emb,
                self.d_content,
                char_dropout=hparams.char_lstm_input_dropout,
            )
        elif hparams.use_xlnet or hparams.use_xlnet_only:
            # Initialize XLNet model and tokenizer if using XLNet embeddings
            if restore:
                self.xlnet_tokenizer, self.xlnet = get_xlnet(
                    None, None, hpara=self.spec["hparams"]
                )
            else:
                self.xlnet_tokenizer, self.xlnet = get_xlnet(
                    hparams.xlnet_model, hparams.xlnet_do_lower_case
                )
                self.spec["hparams"]["xlnet_tokenizer"] = self.xlnet_tokenizer
                self.spec["hparams"]["config"] = self.xlnet.config
            if hparams.bert_transliterate:
                from bkit.shallow.utils.transliterate import TRANSLITERATIONS

                self.bert_transliterate = TRANSLITERATIONS[hparams.bert_transliterate]
            else:
                self.bert_transliterate = None

            d_xlnet_annotations = self.xlnet.d_model
            self.xlnet_max_len = 512

            if hparams.use_xlnet_only:
                self.project_xlnet = nn.Linear(
                    d_xlnet_annotations, hparams.d_model, bias=False
                )
            else:
                self.project_xlnet = nn.Linear(
                    d_xlnet_annotations, self.d_content, bias=False
                )

            if not hparams.use_xlnet_only:
                use_encoder = True

        elif hparams.use_bert or hparams.use_bert_only:
            # Initialize BERT model and tokenizer if using BERT embeddings
            if restore:
                self.bert_tokenizer, self.bert = get_bert(
                    None, None, hpara=self.spec["hparams"]
                )
            else:
                self.bert_tokenizer, self.bert = get_bert(
                    hparams.bert_model, hparams.bert_do_lower_case
                )
                self.spec["hparams"]["bert_tokenizer"] = self.bert_tokenizer
                self.spec["hparams"]["config"] = self.bert.config
            if hparams.bert_transliterate:
                from utils.transliterate import TRANSLITERATIONS

                self.bert_transliterate = TRANSLITERATIONS[hparams.bert_transliterate]
            else:
                self.bert_transliterate = None

            d_bert_annotations = self.bert.pooler.dense.in_features
            self.bert_max_len = self.bert.embeddings.position_embeddings.num_embeddings

            if hparams.use_bert_only:
                self.project_bert = nn.Linear(
                    d_bert_annotations, hparams.d_model, bias=False
                )
            else:
                self.project_bert = nn.Linear(
                    d_bert_annotations, self.d_content, bias=False
                )

            if not hparams.use_bert_only:
                use_encoder = True

        # Create embedding and encoder layers
        if use_encoder:
            # Initialize MultiLevelEmbedding and Encoder if an encoder is used
            self.embedding = MultiLevelEmbedding(
                [num_embeddings_map[emb_type] for emb_type in self.emb_types],
                hparams.d_model,
                d_positional=self.d_positional,
                dropout=hparams.embedding_dropout,
                timing_dropout=hparams.timing_dropout,
                emb_dropouts_list=[
                    emb_dropouts_map[emb_type] for emb_type in self.emb_types
                ],
                extra_content_dropout=self.morpho_emb_dropout,
                max_len=hparams.sentence_max_len,
            )

            self.encoder = Encoder(
                self.embedding,
                num_layers=hparams.num_layers,
                num_heads=hparams.num_heads,
                d_kv=hparams.d_kv,
                d_ff=hparams.d_ff,
                d_positional=self.d_positional,
                num_layers_position_only=hparams.num_layers_position_only,
                relu_dropout=hparams.relu_dropout,
                residual_dropout=hparams.residual_dropout,
                attention_dropout=hparams.attention_dropout,
            )
        else:
            self.embedding = None
            self.encoder = None

        # Initialize other model components
        self.span_nagram_attentions = SpanNgramAttentions(
            ngram_size=self.ngram_vocab.size,
            d_emb=hparams.d_model,
            n_channels=self.ngram_channels,
        )
        self.channel_ids = from_numpy(np.array([i for i in range(self.ngram_channels)]))

        # Define the final linear layers for label prediction
        self.f_label = nn.Sequential(
            nn.Linear(
                hparams.d_model * (self.ngram_channels + 1), hparams.d_label_hidden
            ),
            LayerNormalization(hparams.d_label_hidden),
            nn.ReLU(),
            nn.Linear(hparams.d_label_hidden, label_vocab.size - 1),
        )

        # Move the model to GPU if available
        if use_cuda:
            self.cuda()

    @classmethod
    def from_spec(cls, spec, model):
        """
        Create an instance of the class from a specification and model weights.

        :param spec: Model specification.
        :param model: Pre-trained model weights.
        :return: An instance of the ChartParser class with loaded weights.
        """

        spec = spec.copy()
        hparams = spec["hparams"]
        if "use_chars_concat" in hparams and hparams["use_chars_concat"]:
            raise NotImplementedError("Support for use_chars_concat has been removed")

        # Handle missing hparams
        if "sentence_max_len" not in hparams:
            hparams["sentence_max_len"] = 300
        if "use_bert" not in hparams:
            hparams["use_bert"] = False
        if "use_bert_only" not in hparams:
            hparams["use_bert_only"] = False
        if "predict_tags" not in hparams:
            hparams["predict_tags"] = False
        if "bert_transliterate" not in hparams:
            hparams["bert_transliterate"] = ""

        spec["hparams"] = nkutil.HParams(**hparams)
        spec["restore"] = True

        # Create an instance of the class with the provided specification
        res = cls(**spec)

        # Load the provided model weights
        if use_cuda:
            res.cpu()

        res.load_state_dict(model)

        if use_cuda:
            res.cuda()
        return res

    def split_batch(self, sentences, golds, subbatch_max_tokens=3000):
        """
        Split input sentences and gold annotations into subbatches based on token count.

        Args:
            sentences (list): List of input sentences.
            golds (list): List of gold annotations corresponding to input sentences.
            subbatch_max_tokens (int): Maximum token count for each subbatch.

        Yields:
            tuple: Subbatches of sentences and their corresponding gold annotations.
        """
        if self.bert is not None:
            lens = [
                len(
                    self.bert_tokenizer.tokenize(
                        " ".join([word for (_, word) in sentence])
                    )
                )
                + 2
                for sentence in sentences
            ]
        else:
            lens = [len(sentence) + 2 for sentence in sentences]

        lens = np.asarray(lens, dtype=int)
        lens_argsort = np.argsort(lens).tolist()

        num_subbatches = 0
        subbatch_size = 1
        while lens_argsort:
            if (subbatch_size == len(lens_argsort)) or (
                subbatch_size * lens[lens_argsort[subbatch_size]] > subbatch_max_tokens
            ):
                yield [sentences[i] for i in lens_argsort[:subbatch_size]], [
                    golds[i] for i in lens_argsort[:subbatch_size]
                ]
                lens_argsort = lens_argsort[subbatch_size:]
                num_subbatches += 1
                subbatch_size = 1
            else:
                subbatch_size += 1

    def parse(self, sentence, gold=None):
        """
        Parse a single sentence and return the parse tree and loss.

        Args:
            sentence (list): Input sentence.
            gold (list): Gold annotation for the sentence (optional).

        Returns:
            tuple: Parse tree and loss value.
        """
        tree_list, loss_list = self.parse_batch(
            [sentence], [gold] if gold is not None else None
        )
        return tree_list[0], loss_list[0]

    def parse_batch(self, sentences, golds=None, return_label_scores_charts=False):
        """
        Parse a batch of sentences and return parse trees and losses.

        Args:
            sentences (list): List of input sentences.
            golds (list): List of gold annotations corresponding to input sentences (optional).
            return_label_scores_charts (bool): Whether to return label scores and charts.

        Returns:
            tuple: List of parse trees and list of loss values. If `return_label_scores_charts` is True, only label scores and charts are returned.
        """
        is_train = golds is not None  # True
        self.train(is_train)
        torch.set_grad_enabled(is_train)

        if golds is None:
            golds = [None] * len(sentences)

        packed_len = sum([(len(sentence) + 2) for sentence in sentences])

        i = 0
        tag_idxs = np.zeros(packed_len, dtype=int)
        word_idxs = np.zeros(packed_len, dtype=int)
        batch_idxs = np.zeros(packed_len, dtype=int)

        for snum, sentence in enumerate(sentences):
            for tag, word in (
                [(token.START, token.START)] + sentence + [(token.STOP, token.STOP)]
            ):
                tag_idxs[i] = (
                    0
                    if (not self.use_tags)
                    else self.tag_vocab.index_or_unk(tag, token.TAG_UNK)
                )
                if word not in (token.START, token.STOP):
                    count = self.word_vocab.count(word)
                    if not count or (is_train and np.random.rand() < 1 / (1 + count)):
                        word = token.UNK
                word_idxs[i] = self.word_vocab.index(word)
                batch_idxs[i] = snum
                i += 1
        assert i == packed_len

        batch_idxs = BatchIndices(batch_idxs)

        emb_idxs_map = {
            "tags": tag_idxs,
            "words": word_idxs,
        }
        emb_idxs = [from_numpy(emb_idxs_map[emb_type]) for emb_type in self.emb_types]

        if is_train:
            gold_tag_idxs = from_numpy(emb_idxs_map["tags"])

        extra_content_annotations = None

        if self.char_encoder is not None:
            assert isinstance(self.char_encoder, CharacterLSTM)
            max_word_len = max(
                [max([len(word) for tag, word in sentence]) for sentence in sentences]
            )
            # Add 2 for start/stop token
            max_word_len = max(max_word_len, 3) + 2
            char_idxs_encoder = np.zeros((packed_len, max_word_len), dtype=int)
            word_lens_encoder = np.zeros(packed_len, dtype=int)

            i = 0
            for snum, sentence in enumerate(sentences):
                for wordnum, (tag, word) in enumerate(
                    [(token.START, token.START)] + sentence + [(token.STOP, token.STOP)]
                ):
                    j = 0
                    char_idxs_encoder[i, j] = self.char_vocab.index(
                        token.CHAR_START_WORD
                    )
                    j += 1
                    if word in (token.START, token.STOP):
                        char_idxs_encoder[i, j : j + 3] = self.char_vocab.index(
                            token.CHAR_START_SENTENCE
                            if (word == token.START)
                            else token.CHAR_STOP_SENTENCE
                        )
                        j += 3
                    else:
                        for char in word:
                            char_idxs_encoder[i, j] = self.char_vocab.index_or_unk(
                                char, token.CHAR_UNK
                            )
                            j += 1
                    char_idxs_encoder[i, j] = self.char_vocab.index(
                        token.CHAR_STOP_WORD
                    )
                    word_lens_encoder[i] = j + 1
                    i += 1
            assert i == packed_len

            extra_content_annotations = self.char_encoder(
                char_idxs_encoder, word_lens_encoder, batch_idxs
            )

        elif self.xlnet is not None:
            all_input_ids = np.zeros((len(sentences), self.xlnet_max_len), dtype=int)
            all_input_mask = np.zeros((len(sentences), self.xlnet_max_len), dtype=int)
            all_word_start_mask = np.zeros(
                (len(sentences), self.xlnet_max_len), dtype=int
            )
            all_word_end_mask = np.zeros(
                (len(sentences), self.xlnet_max_len), dtype=int
            )

            subword_max_len = 0
            for snum, sentence in enumerate(sentences):
                tokens = []
                word_start_mask = []
                word_end_mask = []

                tokens.append(self.xlnet_tokenizer.cls_token)
                word_start_mask.append(1)
                word_end_mask.append(1)

                if self.bert_transliterate is None:
                    cleaned_words = []
                    for _, word in sentence:
                        word = token.BERT_TOKEN_MAPPING.get(word, word)
                        word = word.replace("\\/", "/").replace("\\*", "*")

                        word = word.replace("-LSB-", "[").replace("-RSB-", "]")
                        word = word.replace("-LRB-", "(").replace("-RRB-", ")")
                        if word == "n't" and cleaned_words:
                            cleaned_words[-1] = cleaned_words[-1] + "n"
                            word = "'t"
                        cleaned_words.append(word)
                else:
                    cleaned_words = [
                        self.bert_transliterate(word) for _, word in sentence
                    ]

                for word in cleaned_words:
                    word_tokens = self.xlnet_tokenizer.tokenize(word)  # word tokenized
                    if len(word_tokens) == 0:
                        word_tokens = [self.xlnet_tokenizer.unk_token]
                    for _ in range(len(word_tokens)):
                        word_start_mask.append(0)
                        word_end_mask.append(0)
                    word_start_mask[len(tokens)] = 1
                    word_end_mask[-1] = 1
                    tokens.extend(word_tokens)
                tokens.append(self.xlnet_tokenizer.sep_token)
                word_start_mask.append(1)
                word_end_mask.append(1)

                input_ids = self.xlnet_tokenizer.convert_tokens_to_ids(
                    tokens
                )  # input/token ids

                # The mask has 1 for real tokens and 0 for padding tokens. Only real tokens are attended to.
                input_mask = [1] * len(input_ids)

                subword_max_len = max(subword_max_len, len(input_ids))

                all_input_ids[snum, : len(input_ids)] = input_ids
                all_input_mask[snum, : len(input_mask)] = input_mask
                all_word_start_mask[snum, : len(word_start_mask)] = word_start_mask
                all_word_end_mask[snum, : len(word_end_mask)] = word_end_mask

            all_input_ids = from_numpy(
                np.ascontiguousarray(all_input_ids[:, :subword_max_len])
            )
            all_input_mask = from_numpy(
                np.ascontiguousarray(all_input_mask[:, :subword_max_len])
            )
            all_word_start_mask = from_numpy(
                np.ascontiguousarray(all_word_start_mask[:, :subword_max_len])
            )
            all_word_end_mask = from_numpy(
                np.ascontiguousarray(all_word_end_mask[:, :subword_max_len])
            )

            print(all_input_ids.shape)

            transformer_outputs = self.xlnet(
                all_input_ids, attention_mask=all_input_mask
            )  # xlnet_embeddings

            features = transformer_outputs[0]

            if self.encoder is not None:
                features_packed = features.masked_select(
                    all_word_end_mask.to(torch.bool).unsqueeze(-1)
                ).reshape(
                    -1, features.shape[-1]
                )  # embedding packed in a batch
                # For now, just project the features from the last word piece in each word
                extra_content_annotations = self.project_xlnet(
                    features_packed
                )  # projecting_to_desirable_encoder_shape

        elif self.bert is not None:
            all_input_ids = np.zeros((len(sentences), self.bert_max_len), dtype=int)
            all_input_mask = np.zeros((len(sentences), self.bert_max_len), dtype=int)
            all_word_start_mask = np.zeros(
                (len(sentences), self.bert_max_len), dtype=int
            )
            all_word_end_mask = np.zeros((len(sentences), self.bert_max_len), dtype=int)

            subword_max_len = 0
            for snum, sentence in enumerate(sentences):
                tokens = []
                word_start_mask = []
                word_end_mask = []

                tokens.append("[CLS]")
                word_start_mask.append(1)
                word_end_mask.append(1)

                if self.bert_transliterate is None:
                    cleaned_words = []
                    for _, word in sentence:
                        word = token.BERT_TOKEN_MAPPING.get(word, word)
                        word = word.replace("\\/", "/").replace("\\*", "*")

                        word = word.replace("-LSB-", "[").replace("-RSB-", "]")
                        word = word.replace("-LRB-", "(").replace("-RRB-", ")")
                        if word == "n't" and cleaned_words:
                            cleaned_words[-1] = cleaned_words[-1] + "n"
                            word = "'t"
                        cleaned_words.append(word)
                else:
                    cleaned_words = [
                        self.bert_transliterate(word) for _, word in sentence
                    ]

                for word in cleaned_words:
                    word_tokens = self.bert_tokenizer.tokenize(word)
                    if len(word_tokens) == 0:
                        word_tokens = ["[UNK]"]
                    for _ in range(len(word_tokens)):
                        word_start_mask.append(0)
                        word_end_mask.append(0)
                    word_start_mask[len(tokens)] = 1
                    word_end_mask[-1] = 1
                    tokens.extend(word_tokens)
                tokens.append("[SEP]")
                word_start_mask.append(1)
                word_end_mask.append(1)

                input_ids = self.bert_tokenizer.convert_tokens_to_ids(tokens)

                # The mask has 1 for real tokens and 0 for padding tokens. Only real tokens are attended to.
                input_mask = [1] * len(input_ids)

                subword_max_len = max(subword_max_len, len(input_ids))

                all_input_ids[snum, : len(input_ids)] = input_ids
                all_input_mask[snum, : len(input_mask)] = input_mask
                all_word_start_mask[snum, : len(word_start_mask)] = word_start_mask
                all_word_end_mask[snum, : len(word_end_mask)] = word_end_mask

            all_input_ids = from_numpy(
                np.ascontiguousarray(all_input_ids[:, :subword_max_len])
            )
            all_input_mask = from_numpy(
                np.ascontiguousarray(all_input_mask[:, :subword_max_len])
            )
            all_word_start_mask = from_numpy(
                np.ascontiguousarray(all_word_start_mask[:, :subword_max_len])
            )
            all_word_end_mask = from_numpy(
                np.ascontiguousarray(all_word_end_mask[:, :subword_max_len])
            )

            all_encoder_layers, _ = self.bert(
                all_input_ids, attention_mask=all_input_mask, return_dict=False
            )
            del _

            features = all_encoder_layers[-1]  # taking last layer

            if self.encoder is not None:
                features_packed = features.masked_select(
                    all_word_end_mask.to(torch.bool).unsqueeze(-1)
                ).reshape(-1, features.shape[-1])

                extra_content_annotations = self.project_bert(features_packed)

        if self.encoder is not None:
            annotations, _ = self.encoder(
                emb_idxs,
                batch_idxs,
                extra_content_annotations=extra_content_annotations,
            )  # xlnet_embedding_into_encoder

            if self.partitioned:
                # Rearrange the annotations to ensure that the transition to fenceposts captures an even split between position and content.

                annotations = torch.cat(
                    [  # embeddings_rearranged
                        annotations[:, 0::2],  # even_index_column
                        annotations[:, 1::2],  # even_odd_index_column
                    ],
                    1,
                )

            fencepost_annotations = torch.cat(
                [
                    # even_index_columns_without_last_row
                    annotations[:-1, : self.d_model // 2],
                    # odd_index_column_without_first_row
                    annotations[1:, self.d_model // 2 :],
                ],
                1,
            )

            fencepost_annotations_start = fencepost_annotations
            fencepost_annotations_end = fencepost_annotations

        # Note that the subtraction above creates fenceposts at sentence
        # boundaries, which are not used by our parser. Hence subtract 1
        # when creating fp_endpoints
        fp_startpoints = batch_idxs.boundaries_np[:-1]  # sentence_start_points
        fp_endpoints = batch_idxs.boundaries_np[1:] - 1  # sentence_end_points

        # Just return the charts, for ensembling
        if return_label_scores_charts:
            charts = []
            for i, (start, end) in enumerate(zip(fp_startpoints, fp_endpoints)):
                chart, att = self.label_scores_from_annotations(
                    fencepost_annotations_start[start:end, :],
                    fencepost_annotations_end[start:end, :],
                    sentences[i],
                )
                charts.append(chart.cpu().data.numpy())
            return charts

        if not is_train:
            trees = []
            scores = []

            for i, (start, end) in enumerate(zip(fp_startpoints, fp_endpoints)):
                sentence = sentences[i]

                sub_fencepost_annotations_start = fencepost_annotations_start[
                    start:end, :
                ]
                sub_fencepost_annotations_end = fencepost_annotations_end[start:end, :]

                (
                    label_scores_chart,
                    span_attentions,
                ) = self.label_scores_from_annotations(
                    sub_fencepost_annotations_start,
                    sub_fencepost_annotations_end,
                    sentence,
                )
                tree, score = self.parse_from_annotations(
                    label_scores_chart, sentence, golds[i]
                )
                trees.append(tree)
                scores.append(score)
            return trees, scores

        # During training time, the forward pass needs to be computed for every
        # cell of the chart, but the backward pass only needs to be computed for
        # cells in either the predicted or the gold parse tree. It's slightly
        # faster to duplicate the forward pass for a subset of the chart than it
        # is to perform a backward pass that doesn't take advantage of sparsity.
        # Since this code is not undergoing algorithmic changes, it makes sense
        # to include the optimization even though it may only be a 10% speedup.
        # Note that no dropout occurs in the label portion of the network
        pis = []
        pjs = []
        plabels = []
        paugment_total = 0.0
        num_p = 0
        gis = []
        gjs = []
        glabels = []
        patt = []
        gatt = []
        with torch.no_grad():
            for i, (start, end) in enumerate(zip(fp_startpoints, fp_endpoints)):
                sub_fencepost_annotations_start = fencepost_annotations_start[
                    start:end, :
                ]
                sub_fencepost_annotations_end = fencepost_annotations_end[start:end, :]
                sentence = sentences[i]
                gold = golds[i]

                (
                    label_scores_chart,
                    span_attentions,
                ) = self.label_scores_from_annotations(
                    sub_fencepost_annotations_start,
                    sub_fencepost_annotations_end,
                    sentence,
                )

                (
                    p_i,
                    p_j,
                    p_label,
                    p_augment,
                    g_i,
                    g_j,
                    g_label,
                ) = self.parse_from_annotations(label_scores_chart, sentence, gold)
                paugment_total += p_augment
                num_p += p_i.shape[0]
                pis.append(p_i + start)
                pjs.append(p_j + start)
                gis.append(g_i + start)
                gjs.append(g_j + start)
                plabels.append(p_label)
                glabels.append(g_label)
                span_attentions = span_attentions.cpu().data.numpy()
                patt.append(
                    [span_attentions[p_ii][p_jj] for p_ii, p_jj in zip(p_i, p_j)]
                )
                gatt.append(
                    [span_attentions[g_ii][g_jj] for g_ii, g_jj in zip(g_i, g_j)]
                )

        cells_i = from_numpy(np.concatenate(pis + gis))
        cells_j = from_numpy(np.concatenate(pjs + gjs))
        cells_label = from_numpy(np.concatenate(plabels + glabels))
        cells_att = from_numpy(np.concatenate(patt + gatt))

        span_vector = (
            fencepost_annotations_end[cells_j] - fencepost_annotations_start[cells_i]
        )
        span_vector = torch.cat([span_vector, cells_att], dim=1)

        cells_label_scores = self.f_label(span_vector)
        cells_label_scores = torch.cat(
            [
                cells_label_scores.new_zeros((cells_label_scores.size(0), 1)),
                cells_label_scores,
            ],
            1,
        )
        cells_scores = torch.gather(cells_label_scores, 1, cells_label[:, None])
        loss = cells_scores[:num_p].sum() - cells_scores[num_p:].sum() + paugment_total

        return None, loss

    def label_scores_from_annotations(
        self, fencepost_annotations_start, fencepost_annotations_end, sentence
    ):
        """
        Calculate label scores and span attentions from annotation features.

        Args:
            fencepost_annotations_start (Tensor): Annotations at sentence start positions.
            fencepost_annotations_end (Tensor): Annotations at sentence end positions.
            sentence (list): Input sentence.

        Returns:
            tuple: Label scores chart and span attentions.
        """

        # span_features[i][j] is fencepost_annotations_end[j] - fencepost_annotations_start[i]
        span_features = torch.unsqueeze(fencepost_annotations_end, 0) - torch.unsqueeze(
            fencepost_annotations_start, 1
        )

        # ---------- ngram ----------
        packed_ngrams = [[] for _ in range(self.ngram_channels)]
        packed_matching_positions = [[] for _ in range(self.ngram_channels)]

        for n in range(self.ngram_channels):
            n_len = n + 1
            for index in range(len(sentence) - n):
                ngram = tuple(
                    [
                        tag_word[1].lower()
                        for tag_word in sentence[index : index + n_len]
                    ]
                )  # all_combination_of words(ngram)
                if self.ngram_vocab.in_vocab(ngram):
                    if ngram in packed_ngrams[n]:
                        ngram_index = packed_ngrams[n].index(ngram)
                    else:
                        packed_ngrams[n].append(ngram)
                        ngram_index = len(packed_ngrams[n]) - 1
                    for i in range(index + 1):
                        for j in range(index + n_len, len(sentence) + 1):
                            packed_matching_positions[n].append((i, j, ngram_index))

        packed_ngram_len = max(
            max([len(packed_ngrams[n]) for n in range(self.ngram_channels)]), 1
        )
        ngram_idxs = np.zeros((self.ngram_channels, packed_ngram_len), dtype=int)
        span_ngram_matching_matrix = np.zeros(
            (
                len(sentence) + 1,
                len(sentence) + 1,
                self.ngram_channels,
                packed_ngram_len,
            ),
            dtype=np.float32,
        )
        for channel_index in range(self.ngram_channels):
            for i, ngram in enumerate(packed_ngrams[channel_index]):
                ngram_idxs[channel_index][i] = self.ngram_vocab.index(ngram)
            for position in packed_matching_positions[channel_index]:
                span_ngram_matching_matrix[position[0]][position[1]][channel_index][
                    position[2]
                ] = 1.0
                span_ngram_matching_matrix[position[1]][position[0]][channel_index][
                    position[2]
                ] = 1.0
        ngram_idxs = from_numpy(ngram_idxs)
        span_ngram_matching_matrix = from_numpy(span_ngram_matching_matrix)

        span_attentions = self.span_nagram_attentions(
            ngram_idxs, span_features, span_ngram_matching_matrix, self.channel_ids
        )

        # span_score and span_ngram_attention concatenated
        span_features = torch.cat([span_features, span_attentions], dim=2)

        # ---------- ngram ----------
        label_scores_chart = self.f_label(span_features)

        label_scores_chart = torch.cat(
            [  # added_null_label_opputunity
                label_scores_chart.new_zeros(
                    (label_scores_chart.size(0), label_scores_chart.size(1), 1)
                ),
                label_scores_chart,
            ],
            2,
        )

        return label_scores_chart, span_attentions

    def parse_from_annotations(self, label_scores_chart, sentence, gold=None):
        """
        Parse from label scores chart and return relevant information.

        Args:
            label_scores_chart (Tensor): Label scores chart.
            sentence (list): Input sentence.
            gold (list): Gold annotation for the sentence (optional).

        Returns:
            tuple: Information related to parsing.
        """
        is_train = gold is not None

        label_scores_chart_np = label_scores_chart.cpu().data.numpy()

        if is_train:
            decoder_args = dict(
                sentence_len=len(sentence),
                label_scores_chart=label_scores_chart_np,
                gold=gold,
                label_vocab=self.label_vocab,
                is_train=is_train,
            )

            p_score, p_i, p_j, p_label, p_augment = chart_helper.decode(
                False, **decoder_args
            )
            g_score, g_i, g_j, g_label, g_augment = chart_helper.decode(
                True, **decoder_args
            )
            return p_i, p_j, p_label, p_augment, g_i, g_j, g_label
        else:
            return self.decode_from_chart(sentence, label_scores_chart_np)

    def decode_from_chart_batch(self, sentences, charts_np, golds=None):
        """
        Decode parse trees from chart batch.

        Args:
            sentences (list): List of input sentences.
            charts_np (list): List of label scores charts.
            golds (list): List of gold annotations corresponding to input sentences (optional).

        Returns:
            tuple: List of parse trees and list of scores.
        """
        trees = []
        scores = []
        if golds is None:
            golds = [None] * len(sentences)
        for sentence, chart_np, gold in zip(sentences, charts_np, golds):
            tree, score = self.decode_from_chart(sentence, chart_np, gold)
            trees.append(tree)
            scores.append(score)
        return trees, scores

    def decode_from_chart(self, sentence, chart_np, gold=None):
        """
        Decode parse tree from label scores chart.

        Args:
            sentence (list): Input sentence.
            chart_np (Tensor): Label scores chart.
            gold (list): Gold annotation for the sentence (optional).

        Returns:
            tuple: Parse tree and score.
        """
        decoder_args = dict(
            sentence_len=len(sentence),
            label_scores_chart=chart_np,
            gold=gold,
            label_vocab=self.label_vocab,
            is_train=False,
        )

        force_gold = gold is not None

        # The optimized cython decoder implementation doesn't actually
        # generate trees, only scores and span indices. When converting to a
        # tree, we assume that the indices follow a preorder traversal.
        score, p_i, p_j, p_label, _ = chart_helper.decode(force_gold, **decoder_args)
        last_splits = []
        idx = -1

        def make_tree():
            nonlocal idx
            idx += 1
            i, j, label_idx = p_i[idx], p_j[idx], p_label[idx]
            label = self.label_vocab.value(label_idx)
            if (i + 1) >= j:
                tag, word = sentence[i]
                tree = trees.LeafParseNode(int(i), tag, word)
                if label:
                    tree = trees.InternalParseNode(label, [tree])
                return [tree]
            else:
                left_trees = make_tree()
                right_trees = make_tree()
                children = left_trees + right_trees
                if label:
                    return [trees.InternalParseNode(label, children)]
                else:
                    return children

        tree = make_tree()[0]
        return tree, score
