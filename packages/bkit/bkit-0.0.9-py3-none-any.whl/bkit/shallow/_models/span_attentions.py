import torch
import torch.nn as nn


class NgramAttentions(nn.Module):
    """
    N-gram attentions module.

    Args:
        ngram_size (int): Size of the n-gram.
        d_emb (int): Dimensionality of the embedding.
        n_channels (int): Number of channels.
    """

    def __init__(self, ngram_size, d_emb, n_channels):
        super(NgramAttentions, self).__init__()
        self.temper = d_emb**0.5
        self.word_embedding = nn.Embedding(ngram_size, d_emb, padding_idx=0)
        self.channel_weight = nn.Embedding(n_channels, 1)

    def forward(self, ngram_seq, hidden_state, word_ngram_mask_matrix, channel_ids):
        """
        Forward pass of the N-gram attentions module.

        Args:
            ngram_seq (torch.Tensor): N-gram sequence tensor.
            hidden_state (torch.Tensor): Hidden state tensor.
            word_ngram_mask_matrix (torch.Tensor): Word-ngram mask matrix.
            channel_ids (torch.Tensor): Channel IDs.

        Returns:
            torch.Tensor: Character attention tensor.
        """

        embedding = self.word_embedding(ngram_seq)

        # tmp_hidden_state (hidden_size, word_seq_len)
        tmp_hidden_state = hidden_state.permute(1, 0)

        # u (channel, ngram_seq_len, word_seq_len)
        u = torch.matmul(embedding, tmp_hidden_state) / self.temper

        # u (channel, word_seq_len, ngram_seq_len)
        u = u.permute(0, 2, 1)

        tmp_word_mask_metrix = torch.clamp(word_ngram_mask_matrix, 0, 1)

        exp_u = torch.exp(u)

        # delta_exp_u (channel, word_seq_len, ngram_seq_len)
        delta_exp_u = torch.mul(exp_u, tmp_word_mask_metrix)

        sum_delta_exp_u = torch.stack(
            [torch.sum(delta_exp_u, 2)] * delta_exp_u.shape[2], 2
        )

        # attention (channel, word_seq_len, ngram_seq_len)
        attention = torch.div(delta_exp_u, sum_delta_exp_u + 1e-10)

        # character_attention (channel, word_seq_len, hidden_size)
        character_attention = torch.bmm(attention, embedding)

        channel_w = self.channel_weight(channel_ids)
        channel_w = nn.Softmax(dim=1)(channel_w)
        channel_w = channel_w.view(-1, 1, 1)
        character_attention = torch.mul(character_attention, channel_w)

        character_attention = character_attention.permute(1, 0, 2)
        character_attention = character_attention.flatten(start_dim=1)

        return character_attention


class SpanNgramAttentions(nn.Module):
    """
    Span N-gram attentions module.

    Args:
        ngram_size (int): Size of the n-gram.
        d_emb (int): Dimensionality of the embedding.
        n_channels (int): Number of channels.
    """

    def __init__(self, ngram_size, d_emb, n_channels):
        super(SpanNgramAttentions, self).__init__()
        self.temper = d_emb**0.5
        self.word_embedding = nn.Embedding(ngram_size, d_emb, padding_idx=0)
        self.channel_weight = nn.Embedding(n_channels, 1)
        self.drop_out = nn.Dropout(0.5)

    def forward(self, ngram_seq, span_matrix, span_ngram_mask_matrix, channel_ids):
        """
        Forward pass of the Span N-gram attentions module.

        Args:
            ngram_seq (torch.Tensor): N-gram sequence tensor.
            span_matrix (torch.Tensor): Span matrix.
            span_ngram_mask_matrix (torch.Tensor): Span-ngram mask matrix.
            channel_ids (torch.Tensor): Channel IDs.

        Returns:
            torch.Tensor: Character attention tensor.
        """

        channel = ngram_seq.shape[0]
        sen_len = span_matrix.shape[0]
        hidden_size = span_matrix.shape[2]
        ngram_seq_len = span_ngram_mask_matrix.shape[-1]

        # embedding (channel, ngram_seq_len, hidden_size)
        embedding = self.word_embedding(ngram_seq)

        # tmp_hidden_state (hidden_size, span_i * span_j)
        reshaped_span_matrix = span_matrix.view(-1, hidden_size)
        tmp_span_matrix = reshaped_span_matrix.permute(1, 0)

        # u (channel, ngram_seq_len, span_i * span_j)
        u = torch.matmul(embedding, tmp_span_matrix) / self.temper

        # u (span_i * span_j, channel, ngram_seq_len)
        u = u.permute(2, 0, 1)

        tmp_word_mask_metrix = torch.clamp(span_ngram_mask_matrix, 0, 1)

        exp_u = torch.exp(u)

        # delta_exp_u (span_i * span_j, channel, ngram_seq_len)
        reshaped_mask_matrix = tmp_word_mask_metrix.view(
            sen_len * sen_len, channel, ngram_seq_len
        )
        delta_exp_u = torch.mul(exp_u, reshaped_mask_matrix)

        sum_delta_exp_u = torch.stack(
            [torch.sum(delta_exp_u, 2)] * delta_exp_u.shape[2], 2
        )

        # attention (channel, span_i * span_j, , ngram_seq_len)
        attention = torch.div(delta_exp_u, sum_delta_exp_u + 1e-10)
        attention = attention.permute(1, 0, 2)

        # character_attention (channel, span_i * span_j, hidden_size)
        character_attention = torch.bmm(attention, embedding)

        channel_w = self.channel_weight(channel_ids)
        channel_w = nn.Softmax(dim=0)(channel_w)
        channel_w = channel_w.view(-1, 1, 1)
        character_attention = torch.mul(character_attention, channel_w)

        character_attention = character_attention.permute(1, 0, 2)
        character_attention = character_attention.flatten(start_dim=1)
        character_attention = self.drop_out(character_attention)
        character_attention = character_attention.view(sen_len, sen_len, -1)

        return character_attention
