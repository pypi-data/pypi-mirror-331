import math
import re
from collections import defaultdict


class FindNgrams:
    def __init__(self, min_count=0, min_pmi=0, language="en"):
        """
        Initialize the FindNgrams object.

        Args:
            min_count (int, optional): Minimum count for considering n-grams. Defaults to 0.
            min_pmi (float, optional): Minimum Pointwise Mutual Information (PMI) value for strong segments. Defaults to 0.
            language (str, optional): Language identifier. Defaults to 'en'.
        """
        self.min_count = min_count
        self.min_pmi = min_pmi
        self.words = defaultdict(int)
        self.ngrams, self.pairs = defaultdict(int), defaultdict(int)
        self.total = 0.0
        self.language = language

    def text_filter(self, sentence):
        """
        Clean and filter a sentence.

        Args:
            sentence (List[str]): List of words in a sentence.

        Returns:
            List[List[str]]: Cleaned and filtered sentences.
        """
        cleaned_text = []
        index = 0
        for i, w in enumerate(sentence):
            if re.match("[^\u0600-\u06FF\u0750-\u077F\u4e00-\u9fa50-9a-zA-Z]+", w):
                if i > index:
                    cleaned_text.append([w.lower() for w in sentence[index:i]])
                index = 1 + i
        if index < len(sentence):
            cleaned_text.append([w.lower() for w in sentence[index:]])
        return cleaned_text

    def count_ngram(self, texts, n):
        """
        Count n-grams in the given texts.

        Args:
            texts (List[List[str]]): List of tokenized sentences.
            n (int): Maximum n-gram length.
        """
        self.ngrams = defaultdict(int)
        for sentence in texts:
            for sub_sentence in self.text_filter(sentence):
                for i in range(n):
                    n_len = i + 1
                    for j in range(len(sub_sentence) - i):
                        ngram = tuple([w for w in sub_sentence[j : j + n_len]])
                        self.ngrams[ngram] += 1
        self.ngrams = {i: j for i, j in self.ngrams.items() if j > self.min_count}

    def find_ngrams_pmi(self, texts, n, freq_threshold):
        """
        Find n-grams using Pointwise Mutual Information (PMI) filtering.

        Args:
            texts (List[List[str]]): List of tokenized sentences.
            n (int): Maximum n-gram length.
            freq_threshold (int): Frequency threshold for n-grams.

        Returns:
            None
        """
        for sentence in texts:
            for sub_sentence in self.text_filter(sentence):
                self.words[sub_sentence[0]] += 1
                for i in range(len(sub_sentence) - 1):
                    self.words[sub_sentence[i + 1]] += 1
                    self.pairs[(sub_sentence[i], sub_sentence[i + 1])] += 1
                    self.total += 1
        self.words = {i: j for i, j in self.words.items() if j > self.min_count}
        self.pairs = {i: j for i, j in self.pairs.items() if j > self.min_count}

        min_mi = math.inf
        max_mi = -math.inf

        self.strong_segments = set()
        for i, j in self.pairs.items():
            if i[0] in self.words and i[1] in self.words:
                mi = math.log(self.total * j / (self.words[i[0]] * self.words[i[1]]))
                if mi > max_mi:
                    max_mi = mi
                if mi < min_mi:
                    min_mi = mi
                if mi >= self.min_pmi:
                    self.strong_segments.add(i)

        self.ngrams = defaultdict(int)
        for sentence in texts:
            for sub_sentence in self.text_filter(sentence):
                s = [sub_sentence[0]]
                for i in range(len(sub_sentence) - 1):
                    if (sub_sentence[i], sub_sentence[i + 1]) in self.strong_segments:
                        s.append(sub_sentence[i + 1])
                    else:
                        self.ngrams[tuple(s)] += 1
                        s = [sub_sentence[i + 1]]
        self.ngrams = {
            i: j for i, j in self.ngrams.items() if j > self.min_count and len(i) <= n
        }

        self.renew_ngram_by_freq(texts, freq_threshold, n)

    def renew_ngram_by_freq(self, all_sentences, min_feq, ngram_len=10):
        """
        Renew n-grams based on frequency.

        Args:
            all_sentences (List[List[str]]): List of tokenized sentences.
            min_feq (int): Minimum frequency for considering n-grams.
            ngram_len (int, optional): Maximum n-gram length. Defaults to 10.
        """
        new_ngram2count = {}

        new_all_sentences = []

        for sentence in all_sentences:
            for sen in self.text_filter(sentence):
                for i in range(len(sen)):
                    for n in range(1, ngram_len + 1):
                        if i + n > len(sentence):
                            break
                        n_gram = tuple(sentence[i : i + n])
                        if n_gram not in self.ngrams:
                            continue
                        if n_gram not in new_ngram2count:
                            new_ngram2count[n_gram] = 1
                        else:
                            new_ngram2count[n_gram] += 1
        self.ngrams = {gram: c for gram, c in new_ngram2count.items() if c > min_feq}
