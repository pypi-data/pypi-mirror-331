import math

import torch
import torch.nn as nn
from torch.functional import F
from torch.utils.checkpoint import checkpoint
from transformers import AutoConfig, AutoModel, AutoTokenizer, T5EncoderModel
from torch import nn
import itertools
from pathlib import Path
from typing import Dict, Union
import numpy as np
import torch
from pyhocon import ConfigFactory


class Scorer(nn.Sequential):
    def __init__(self, input_size, hidden_size=-1, hidden_depth=0, dropout=1):
        modules = []
        for i in range(hidden_depth):
            modules.extend(
                [
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Dropout(dropout),
                ]
            )
            input_size = hidden_size
        modules.append(nn.Linear(input_size, 1))
        super().__init__(*modules)


def init_weights(m):
    if isinstance(m, nn.Linear):
        m.weight.data = truncate_normal(m.weight.data.size())
        m.bias.fill_(0)
    elif isinstance(m, nn.Embedding):
        m.weight.data = truncate_normal(m.weight.data.size())


def truncate_normal(size):
    # truncated normal distribution (stddev: 0.02)
    draw = torch.randn(size)
    while (trunc := draw.abs() > 2).any():
        redraw = torch.randn(size)
        draw[trunc] = redraw[trunc]
    return draw * 0.02



class Model(nn.Module):
    def __init__(self, config, model_path, device1, checkpointing=False):
        super().__init__()
        self.bert_model = ModelBert(model_path, device1, checkpointing)
        self.task_model = ModelTask(config, device1, checkpointing)

    def forward(self, sents, *args):
        bert_embs = self.bert_model(sents)
        return self.task_model(bert_embs, *args)


class ModelBert(nn.Module):
    def __init__(self, model_path, device, checkpointing=False):
        super().__init__()
        self.device = device
        # bert embedding
        model_id = model_path
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        bert_config = AutoConfig.from_pretrained(model_id)
        if bert_config.architectures[0] == "T5ForConditionalGeneration":
            self.model = T5EncoderModel.from_pretrained(model_id, config=bert_config)
        else:
            self.model = AutoModel.from_pretrained(model_id, config=bert_config)
        bert_config.gradient_checkpointing = checkpointing

    def forward(self, sents):
        # calculate bert embeddings
        embs = []
        for sent in sents:
            tokens_idx = self.tokenizer.convert_tokens_to_ids(sent)
            tokens_tensor = torch.tensor([tokens_idx], device=self.device)
            enc_layers = self.model(tokens_tensor)[0]
            embs.append(enc_layers.squeeze())
        return torch.cat(embs, dim=0)


class ModelTask(nn.Module):
    def __init__(self, config, device, checkpointing=False):
        super().__init__()
        self.config = config
        self.device = device
        self.condCheckpoint = checkpoint if checkpointing else lambda f, *i: f(*i)
        self.dropout = self.config["dropout"]
        self.max_width = self.config["max_ment_width"]

        # mention embedding
        bert_size = self.config["bert_emb_size"]
        self.span_head = nn.Linear(bert_size, 1)

        # feature embeddings
        bin_width = self.config["bin_widths"]
        feature_size = self.config["feature_size"]
        genre_num = len(self.config["genres"])
        self.speaker_emb = nn.Embedding(2, feature_size)
        self.genre_emb = nn.Embedding(genre_num, feature_size)
        self.ante_dist_emb = nn.Embedding(len(bin_width), feature_size)
        self.ment_width_emb = nn.Embedding(self.max_width, feature_size)

        # scorer for mentions and antecedents
        hidden_size = self.config["hidden_size"]
        hidden_depth = self.config["hidden_depth"]
        ment_emb_size = 3 * bert_size + feature_size
        ante_emb_size = 3 * ment_emb_size + 4 * feature_size
        # mention scoring
        self.mention_scorer = Scorer(
            ment_emb_size, hidden_size, hidden_depth, self.dropout
        )
        self.ment_width_scorer = Scorer(
            feature_size, hidden_size, hidden_depth, self.dropout
        )
        self.ment_width_scorer_emb = nn.Parameter(
            truncate_normal((self.max_width, feature_size))
        )
        # fast antecedent scoring
        self.fast_antecedent_scorer = nn.Linear(ment_emb_size, ment_emb_size)
        self.ante_dist_scorer = Scorer(feature_size, hidden_depth=0)
        self.ante_dist_scorer_emb = nn.Parameter(
            truncate_normal((len(bin_width), feature_size))
        )
        # slow antecedent scoring
        self.slow_antecedent_scorer = Scorer(
            ante_emb_size, hidden_size, hidden_depth, self.dropout
        )
        self.seg_dist_emb = nn.Embedding(self.config["max_segm_num"], feature_size)
        self.attended_gate = nn.Sequential(
            nn.Linear(2 * ment_emb_size, ment_emb_size), nn.Sigmoid()
        )

        # initialize weights
        with torch.no_grad():
            self.apply(init_weights)

        # bins for antecedent distance embedding
        # [0, 1, 2, 3, 4, 5-7, 8-15, 16-31, 32-63, 64+]
        self.bins = []
        for i, w in enumerate(bin_width):
            self.bins.extend([i] * w)
        self.bins = torch.as_tensor(self.bins, dtype=torch.long, device=self.device)

    def ment_embedding(self, bert_emb, ment_starts, ment_ends):
        # get representation for start and end of mention
        start_embs = bert_emb[ment_starts]
        end_embs = bert_emb[ment_ends]

        # calculate distance between mentions
        ment_dist = ment_ends - ment_starts

        # get mention width embedding
        width = ment_ends - ment_starts + 1
        width_embs = self.ment_width_emb(width - 1)
        width_embs = torch.dropout(width_embs, self.dropout, self.training)

        # get head representation
        doc_len, ment_num = len(bert_emb), len(ment_starts)
        # transform mask 0 -> -inf / 1 -> 0 for softmax and add to embeddings
        doc_range = torch.arange(doc_len, device=self.device).expand(ment_num, -1)
        ment_mask = (ment_starts.view(-1, 1) <= doc_range) * (
            doc_range <= ment_ends.view(-1, 1)
        )
        # calculate attention for word per mention
        word_attn = self.span_head(bert_emb).view(1, -1)
        # type depends on amp level (float or half)
        ment_mask = ment_mask.type(word_attn.dtype)
        ment_word_attn = word_attn + torch.log(ment_mask)
        ment_word_attn = F.softmax(ment_word_attn, dim=1)
        # calculate final head embedding as weighted sum
        head_embs = torch.matmul(ment_word_attn, bert_emb)

        # combine different embeddings to single mention embedding
        # warning: different order than proposed in the paper
        return (
            torch.cat((start_embs, end_embs, width_embs, head_embs), dim=1),
            ment_dist,
        )

    def prune_mentions(self, ment_starts, ment_ends, ment_scores, k):
        # get mention indices sorted by the mention score
        ment_idx = ment_scores.argsort(descending=True)

        # map current top indices to start and end index with the maximal spanning width
        # optimization from: https://github.com/YangXuanyue/pytorch-e2e-coref
        max_span_start, max_span_end = {}, {}

        # iterate over sorted mentions and build up top mentions
        top_ment_idx = []
        for idx in ment_idx:
            start_idx = ment_starts[idx].item()
            end_idx = ment_ends[idx].item()

            # check if mentions partially overlap with better scoring mention
            for i in range(start_idx, end_idx + 1):
                if i in max_span_end and i > start_idx and end_idx < max_span_end[i]:
                    break
                if (
                    i in max_span_start
                    and i < end_idx
                    and start_idx > max_span_start[i]
                ):
                    break
            else:
                # add mention if it does not overlap
                top_ment_idx.append(idx)
                if start_idx not in max_span_end or end_idx > max_span_end[start_idx]:
                    max_span_end[start_idx] = end_idx
                if end_idx not in max_span_start or start_idx < max_span_start[end_idx]:
                    max_span_start[end_idx] = start_idx

                # stop when k indices added
                if k == len(top_ment_idx):
                    break

        # find mention order by start and end indices
        top_ment_idx = torch.as_tensor(top_ment_idx)
        ment_pos = ment_starts[top_ment_idx] * ment_ends[-1] + ment_ends[top_ment_idx]
        order = ment_pos.argsort()
        # sort top indices and create tensor
        return top_ment_idx[order]

    def get_fast_antecedents(self, ment_emb, ment_scores, c):
        ment_range = torch.arange(ment_emb.shape[0], device=self.device)
        ante_offset = ment_range.view(-1, 1) - ment_range.view(1, -1)
        ante_mask = ante_offset > 0

        # calculate bilinear antecedent scoring (s_c)
        src_ment_emb = torch.dropout(
            self.fast_antecedent_scorer(ment_emb), 0.5, self.training
        )
        tgt_ment_emb = torch.dropout(ment_emb, 0.5, self.training)
        fast_ante_scores = src_ment_emb @ tgt_ment_emb.t()

        # calculate three factor antecedent scoring (s_m + s_m + s_c)
        fast_ante_scores += ment_scores.view(-1, 1) + ment_scores.view(1, -1)
        fast_ante_scores += torch.log(ante_mask.float())

        # add antecedents distance score (bert-coref)
        ante_dist_bin = self.bins[torch.clamp(ante_offset, min=0, max=64)]
        ante_dist_emb = torch.dropout(
            self.ante_dist_scorer_emb, self.dropout, self.training
        )
        ante_dist_score = self.ante_dist_scorer(ante_dist_emb)[ante_dist_bin]
        fast_ante_scores += ante_dist_score.squeeze()

        # get top antes and prune
        _, top_antes = torch.topk(fast_ante_scores, c, sorted=True)
        # top_antes = np.load('antes.npy')
        top_ante_mask = ante_mask[ment_range.view(-1, 1), top_antes]
        top_fast_ante_scores = fast_ante_scores[ment_range.view(-1, 1), top_antes]
        top_ante_offset = ante_offset[ment_range.view(-1, 1), top_antes]
        return top_antes, top_ante_mask, top_fast_ante_scores, top_ante_offset

    def antecedent_embedding(
        self, ment_emb, antecendets, genre_id, ment_speakers, seg_dist
    ):
        # build up input of shape [num_ment, max_ante, emb]
        num_ment, max_ante = antecendets.shape

        # genre embedding
        genre_emb = self.genre_emb(genre_id)
        genre_emb = genre_emb.view(1, 1, -1).repeat(num_ment, max_ante, 1)

        # same speaker embedding
        ante_speakers = ment_speakers[antecendets]
        same_speaker = torch.eq(ment_speakers.view(-1, 1), ante_speakers)
        speaker_emb = self.speaker_emb(same_speaker.long())

        # antecedent distance embedding
        ante_dist = torch.arange(num_ment, device=self.device).view(-1, 1) - antecendets
        ante_dist_bin = self.bins[torch.clamp(ante_dist, min=0, max=64)]
        ante_dist_emb = self.ante_dist_emb(ante_dist_bin)

        # segment distance embedding
        seg_dist_emb = self.seg_dist_emb(seg_dist)

        # apply dropout to feature embeddings
        feature_emb = torch.cat(
            (speaker_emb, genre_emb, ante_dist_emb, seg_dist_emb), dim=2
        )
        feature_emb = torch.dropout(feature_emb, self.dropout, self.training)

        # antecedent embedding / mention embedding / similarity
        antecedent_emb = ment_emb[antecendets]
        ment_emb = ment_emb.view(num_ment, 1, -1).repeat(1, max_ante, 1)
        similarity_emb = antecedent_emb * ment_emb

        return torch.cat((ment_emb, antecedent_emb, similarity_emb, feature_emb), dim=2)

    def forward_fast(self, bert_emb, speaker_ids, cand_starts, cand_ends):
        # get candidate mentions and scores
        cand_embs, cand_dist = self.ment_embedding(
            bert_emb, cand_starts.to(self.device), cand_ends.to(self.device)
        )
        cand_scores = self.mention_scorer(cand_embs).squeeze()
        # combine old mention scores and width score (bert-coref)
        width_scores = self.ment_width_scorer(self.ment_width_scorer_emb)
        cand_scores += width_scores[cand_dist].squeeze()

        # prune to get top scoring candidate mentions
        self.k = math.floor(bert_emb.shape[0] * self.config["ment_ratio"])
        top_ment_idx = self.prune_mentions(cand_starts, cand_ends, cand_scores, self.k)
        # assure that k is the actual number of pruned mentions
        # can be lower than the initial k, due to subtokens and crossing mentions
        self.k = len(top_ment_idx)

        # filter mention candidates for top scoring mentions
        self.ment_starts = cand_starts[top_ment_idx]
        self.ment_ends = cand_ends[top_ment_idx]
        ment_embs = cand_embs[top_ment_idx]
        ment_scores = cand_scores[top_ment_idx]
        self.ment_speakers = speaker_ids[self.ment_starts]

        # get top c antecedents per mention by fast scoring
        c = min(self.config["max_antes"], self.k)
        (
            self.antes,
            self.ante_mask,
            fast_scores,
            ante_offset,
        ) = self.get_fast_antecedents(ment_embs, ment_scores, c)
        return fast_scores, cand_scores, ment_embs

    def forward_slow(self, fast_scores, ment_embs, seg_dist, dummy_scores, genre_id):
        # get full scores for antecedents
        ante_ment_emb = ment_embs[self.antes]
        ante_emb = self.antecedent_embedding(
            ment_embs,
            self.antes,
            genre_id.to(self.device),
            self.ment_speakers.to(self.device),
            seg_dist.to(self.device),
        )
        ante_scores = fast_scores + self.slow_antecedent_scorer(ante_emb).squeeze()
        # refine mention representations
        ante_weights = torch.softmax(
            torch.cat((dummy_scores, ante_scores), dim=1), dim=-1
        )
        ante_emb = torch.cat((ment_embs.unsqueeze(1), ante_ment_emb), dim=1)
        attended_emb = torch.sum(ante_weights.unsqueeze(-1) * ante_emb, dim=1)
        f = self.attended_gate(torch.cat((ment_embs, attended_emb), dim=1))
        ment_embs = f * attended_emb + (1 - f) * ment_embs
        return ment_embs, ante_scores

    def forward(
        self, bert_emb, segm_len, genre_id, speaker_ids, cand_starts, cand_ends
    ):
        # create sentence mask to flatten tensors
        sent_num, max_segm_len = len(segm_len), max(segm_len)
        sent_mask = torch.arange(max_segm_len).view(1, -1).repeat(
            sent_num, 1
        ) < torch.as_tensor(segm_len).view(-1, 1)

        # compute fast scores until next checkpoint
        inputs = (bert_emb, speaker_ids, cand_starts, cand_ends)
        fast_scores, cand_scores, ment_embs = self.condCheckpoint(
            self.forward_fast, *inputs
        )

        # compute distance between mention and antecedent on segment level (bert-coref)
        seg_map = torch.arange(sent_num).view(-1, 1).repeat(1, max_segm_len)
        flat_seg_map = seg_map[sent_mask].view(-1)

        ment_seg, ante_seg = (
            flat_seg_map[self.ment_starts],
            flat_seg_map[self.ment_starts[self.antes.to(torch.device("cpu"))]],
        )
        seg_dist = torch.clamp(
            ment_seg.view(-1, 1) - ante_seg, min=0, max=self.config["max_segm_num"] - 1
        )

        # iterative inference procedure / type depends on amp level (float or half)
        dummy_scores = torch.zeros(
            self.k, 1, device=self.device, dtype=fast_scores.dtype
        )
        for i in range(self.config["coref_depth"]):
            inputs = (fast_scores, ment_embs, seg_dist, dummy_scores, genre_id)
            ment_embs, ante_scores = self.condCheckpoint(self.forward_slow, *inputs)

        # get final coreference score for antecedents and labels
        coref_score = torch.cat((dummy_scores, ante_scores), dim=1)

        return coref_score, self.antes, self.ment_starts, self.ment_ends, cand_scores

class Infer_Coreference:
    def __init__(self, model_path: Union[str, Path] = None):
        """
        Initializes the Infer_Noisy class instance.

        Args:
            model_path (Union[str, Path]): Path to the directory containing model files.
        """
        # load configuration
        self.config = ConfigFactory.parse_file(f"{str(model_path)}/coref.conf")[
            "bert-base-bn"
        ]

        # initialize model and move to gpu if available
        device1 = (
            torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        )
        # print(f'Running on: {device1}')

        # initialize model and move to gpu if available
        self.model = Model(self.config, model_path, device1)
        self.model.bert_model.to(device1)
        self.model.task_model.to(device1)
        self.device = device1
        # self.model.load_state_dict(torch.load(model_path / self.config['model_file'],
        #                                       map_location=self.device))
        self.model.load_state_dict(
            torch.load(f"{str(model_path)}/model.pt", map_location=self.device)
        )
        self.model.eval()

        self.tokenizer = self.model.bert_model.tokenizer

    def create_candidates(self, sent_map, token_map, segm_len):
        # calculate sentence lengths
        sent_idx = range(sent_map[-1] + 1)
        sent_len = [len([s for s in sent_map if s == sent]) for sent in sent_idx]

        # calculate all possible mentions
        max_ment_width = 30
        cand_starts, cand_ends = [], []
        offset = 0
        for s in sent_len:
            for i in range(s):
                width = min(max_ment_width, s - i)
                start = i + offset
                cand_starts.extend([start] * width)
                cand_ends.extend(range(start, start + width))
            offset += s

        # candidate boundaries as tensors
        cand_starts = torch.as_tensor(cand_starts)
        cand_ends = torch.as_tensor(cand_ends)

        # set -1 for CLS and SEP token
        token_map[0] = -1
        token_map[-1] = -1
        for sl in np.cumsum(segm_len[:-1]):
            token_map[sl - 1 : sl + 1] = [-1, -1]
        tkn_map = torch.tensor(token_map)

        # create tensor with possible starts
        tkn_map_sh = torch.tensor([-1] + token_map[:-1])
        start_ = tkn_map != tkn_map_sh
        start_ &= tkn_map >= 0
        # create tensor with possible ends
        tkn_map_sh = torch.tensor(token_map[1:] + [-1])
        end_ = tkn_map != tkn_map_sh
        end_ &= tkn_map >= 0

        # apply subtoken rules
        filter = start_[cand_starts] & end_[cand_ends]
        cand_starts = cand_starts[filter]
        cand_ends = cand_ends[filter]

        return cand_starts, cand_ends

    def convert_to_features(self, sen: str) -> Dict:
        words = sen.split()
        enc = self.tokenizer(words, is_split_into_words=True)
        tokens = list(enc.tokens())
        token_map = [enc.token_to_word(i) for i in range(len(tokens))]
        token_map[0], token_map[-1] = token_map[1], token_map[-2]
        sent_map = [0] * len(tokens)
        speakers = [["[SPL]"] + ["Speaker#1"] * (len(tokens) - 2) + ["[SPL]"]]
        speakers = list(itertools.chain.from_iterable(speakers))
        speaker_dict = {"UNK": 0, "[SPL]": 1}
        for s in speakers:
            if s not in speaker_dict and len(speaker_dict) < 20:
                speaker_dict[s] = len(speaker_dict)
        # if len(speaker_dict) == 20:
        #     print(f'Speaker limit reached: {doc["doc_key"]}')
        speaker_ids = torch.as_tensor([speaker_dict.get(s, 3) for s in speakers])
        segm_len = torch.tensor([len(tokens)])
        genre_id = torch.as_tensor([0])
        cand_starts, cand_ends = self.create_candidates(sent_map, token_map, segm_len)
        segms = [tokens]
        # return {'segms':segms,
        #         'segm_len':segm_len,
        #         'genre_id':genre_id,
        #         'speaker_ids':speaker_ids,
        #         'cand_starts':cand_starts,
        #         'cand_ends':cand_ends}
        return segms, segm_len, genre_id, speaker_ids, cand_starts, cand_ends, token_map

    def eval_antecedents(self, scores, antes, ment_starts, ment_ends):
        # tensor to numpy array
        ment_starts = ment_starts.numpy()
        ment_ends = ment_ends.numpy()

        # get best antecedent per mention (as mention index)
        pred_ante_idx = torch.argmax(scores, dim=1) - 1
        pred_antes = [
            -1 if ante_idx < 0 else antes[ment_idx, ante_idx]
            for ment_idx, ante_idx in enumerate(pred_ante_idx)
        ]

        # get predicted clusters and mapping of mentions to them
        # antecedents have to be sorted by mention start
        ment_to_pred_cluster = {}
        pred_clusters = []
        for ment_idx, pred_idx in enumerate(pred_antes):
            # ignore dummy antecedent
            if pred_idx < 0:
                continue

            # search for corresponding cluster or create new one
            pred_ante = (ment_starts[pred_idx], ment_ends[pred_idx])
            if pred_ante in ment_to_pred_cluster:
                cluster_idx = ment_to_pred_cluster[pred_ante]
            else:
                cluster_idx = len(pred_clusters)
                pred_clusters.append([pred_ante])
                ment_to_pred_cluster[pred_ante] = cluster_idx

            # add mention to cluster
            ment = (ment_starts[ment_idx], ment_ends[ment_idx])
            pred_clusters[cluster_idx].append(ment)
            ment_to_pred_cluster[ment] = cluster_idx

        # replace mention indices with mention boundaries
        pred_clusters = [tuple(cluster) for cluster in pred_clusters]
        ment_to_pred_cluster = {
            m: pred_clusters[i] for m, i in ment_to_pred_cluster.items()
        }

        return pred_clusters

    def infer(self, text: str) -> dict:
        # convert text to model features
        features = list(self.convert_to_features(text))
        scores, antes, ment_starts, ment_ends, cand_scores = self.model(
            features[0],
            *features[1:-1],
        )
        pred_clusters = self.eval_antecedents(scores, antes, ment_starts, ment_ends)

        token_map = features[-1]
        token_map = {i: word_id for i, word_id in enumerate(token_map)}

        coreferences, coref_response = {}, {}
        for i, ment_cluster in enumerate(pred_clusters):
            cluster = []
            for s_i, e_i in ment_cluster:
                cluster.append(
                    {"start_token": token_map[s_i], "end_token": token_map[e_i]}
                )
            coreferences[i] = cluster
        coref_response["text"] = text.split()
        coref_response["mention_indices"] = coreferences
        # return CoreferenceResponse(**coref_response)
        return coref_response
