import collections

from bkit.shallow.utils import token
from bkit.shallow.utils.attutil import FindNgrams

from . import trees


class Vocabulary(object):
    """
    A class representing a vocabulary of tokens.

    Attributes:
        frozen (bool): Indicates whether the vocabulary is frozen.
        values (list): List of token values in the vocabulary.
        indices (dict): Mapping of token values to their indices.
        counts (collections.defaultdict): Counts of token occurrences.
    """

    def __init__(self):
        self.frozen = False
        self.values = []
        self.indices = {}
        self.counts = collections.defaultdict(int)

    @property
    def size(self):
        """
        Get the size of the vocabulary.

        Returns:
            int: The size of the vocabulary.
        """
        return len(self.values)

    def value(self, index):
        """
        Get the value of a token at a given index.

        Args:
            index (int): Index of the token.

        Returns:
            str: The token value.
        """
        assert 0 <= index < len(self.values)
        return self.values[index]

    def index(self, value):
        """
        Get the index of a token value. If the value is not in the vocabulary, add it.

        Args:
            value (str): The token value.

        Returns:
            int: The index of the token value.
        """
        if not self.frozen:
            self.counts[value] += 1

        if value in self.indices:
            return self.indices[value]

        elif not self.frozen:
            self.values.append(value)
            self.indices[value] = len(self.values) - 1
            return self.indices[value]

        else:
            raise ValueError("Unknown value: {}".format(value))

    def index_or_unk(self, value, unk_value):
        """
        Get the index of a token value or the index of the unknown token value.

        Args:
            value (str): The token value.
            unk_value (str): The value of the unknown token.

        Returns:
            int: The index of the token value or the unknown token index.
        """
        assert self.frozen
        if value in self.indices:
            return self.indices[value]
        else:
            return self.indices[unk_value]

    def count(self, value):
        """
        Get the count of a token value in the vocabulary.

        Args:
            value (str): The token value.

        Returns:
            int: The count of the token value.
        """
        return self.counts[value]

    def freeze(self):
        """
        Freeze the vocabulary, preventing further modifications.
        """
        self.frozen = True

    def in_vocab(self, value):
        """
        Check if a token value is in the vocabulary.

        Args:
            value (str): The token value.

        Returns:
            bool: True if the token value is in the vocabulary, False otherwise.
        """
        return value in self.indices


def get_vocabs(logger, args, hparams, train_parse, dev_parse):
    """
    Construct and return vocabulary objects for tags, words, labels, characters, and n-grams.

    Args:
        logger: The logger object for logging messages.
        args: Arguments provided to the script.
        hparams: Hyperparameters for constructing the vocabularies.
        train_parse: Training parse data.
        dev_parse: Development parse data.

    Returns:
        tuple: A tuple containing tag_vocab, word_vocab, label_vocab, char_vocab, and ngram_vocab.
    """

    # Construct tag, word, and label vocabularies
    logger.info("Constructing vocabularies...")

    tag_vocab = Vocabulary()
    tag_vocab.index(token.START)
    tag_vocab.index(token.STOP)
    tag_vocab.index(token.TAG_UNK)

    word_vocab = Vocabulary()
    word_vocab.index(token.START)
    word_vocab.index(token.STOP)
    word_vocab.index(token.UNK)

    label_vocab = Vocabulary()
    label_vocab.index(())

    char_set = set()

    # Populate tag, word, and label vocabularies from training data
    for tree in train_parse:
        nodes = [tree]
        while nodes:
            node = nodes.pop()
            if isinstance(node, trees.InternalParseNode):
                label_vocab.index(node.label)
                nodes.extend(reversed(node.children))
            else:
                tag_vocab.index(node.tag)
                word_vocab.index(node.word)
                char_set |= set(node.word)

    char_vocab = Vocabulary()

    # Determine the highest codepoint for character indexing
    highest_codepoint = max(
        ord(char) for char in char_set
    )  # ord()= representing the unicode number
    if (
        highest_codepoint < 512
    ):  # If codepoints are small (e.g. Latin alphabet), index by codepoint directly
        if highest_codepoint < 256:
            highest_codepoint = 256
        else:
            highest_codepoint = 512

        # Index characters by codepoint directly
        for codepoint in range(highest_codepoint):
            char_index = char_vocab.index(chr(codepoint))
            assert char_index == codepoint
    else:
        # Index special characters and characters in the character set
        char_vocab.index(token.CHAR_UNK)
        char_vocab.index(token.CHAR_START_SENTENCE)
        char_vocab.index(token.CHAR_START_WORD)
        char_vocab.index(token.CHAR_STOP_WORD)
        char_vocab.index(token.CHAR_STOP_SENTENCE)
        for char in sorted(char_set):
            char_vocab.index(char)

    # Freeze vocabularies
    tag_vocab.freeze()
    word_vocab.freeze()
    label_vocab.freeze()
    char_vocab.freeze()

    # Construct n-gram vocabulary using FindNgrams utility
    ngram_vocab = Vocabulary()
    ngram_vocab.index(())
    ngram_finder = FindNgrams(min_count=hparams.ngram_threshold)

    # Function to extract sentences from parse data
    def get_sentence(parse):
        sentences = []
        for tree in parse:
            sentence = []
            for leaf in tree.leaves():
                sentence.append(leaf.word)
            sentences.append(sentence)
        return sentences

    # Generate sentence lists for n-gram counting
    sentence_list = get_sentence(train_parse)
    if not args.cross_domain:
        sentence_list.extend(get_sentence(dev_parse))

    # Count n-grams based on the specified n-gram type
    if hparams.ngram_type == "freq":
        logger.info("ngram type: freq")
        ngram_finder.count_ngram(sentence_list, hparams.ngram)
    elif hparams.ngram_type == "pmi":
        logger.info("ngram type: pmi")
        ngram_finder.find_ngrams_pmi(
            sentence_list, hparams.ngram, hparams.ngram_freq_threshold
        )
    else:
        raise ValueError()

    # Index n-grams in the vocabulary
    ngram_type_count = [0 for _ in range(hparams.ngram)]
    for w, c in ngram_finder.ngrams.items():
        ngram_type_count[len(list(w)) - 1] += 1
        for _ in range(c):
            ngram_vocab.index(w)
    logger.info(str(ngram_type_count))
    ngram_vocab.freeze()

    # Count n-gram occurrences
    ngram_count = [0 for _ in range(hparams.ngram)]
    for sentence in sentence_list:
        for n in range(len(ngram_count)):
            length = n + 1
            for i in range(len(sentence)):
                gram = tuple(sentence[i : i + length])
                if gram in ngram_finder.ngrams:
                    ngram_count[n] += 1
    logger.info(str(ngram_count))

    return tag_vocab, word_vocab, label_vocab, char_vocab, ngram_vocab
