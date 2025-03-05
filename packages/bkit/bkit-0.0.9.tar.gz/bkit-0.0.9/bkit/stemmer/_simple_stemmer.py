import re
import importlib
import warnings
import pickle
from typing import Union, List
from functools import lru_cache
from bkit.tokenizer._word_tokenization import tokenize
from bkit.transform.cleaning import (
    clean_emojis, 
    clean_html, 
    clean_multiple_punctuations, 
    clean_multiple_spaces, 
    clean_non_bangla, 
    clean_punctuations, 
    clean_special_characters, 
    clean_urls
)
from bkit.transform.normalizing import Normalizer



builtin_prefixes = [
    'অগা','অঘা','অন','অন্','অভি','ইঙ্গ','উপ','কুচকুচ','গর','জাত','নও','নিঃ',
    'পরি','পুনর্','বে','ভূ','শ্রী','সু',"অ","অন","অতি","অপর","প্রতি","পরি","উপ",
    "স","সু", "দূর", "নি", "বিশ", "অস", "হিম","অধি","অন্ত","প্র","অপ","অভি"
    ]

builtin_suffixes = [
    'অক্ত','অনীয়','আ','আধিক','আনী','আর','আলয়','আশ্রিত','ই','ইক','ইনী','ইয়া','ঈ',
    'ঈয়','এ','এছ','এছি','এছিল','এছিলেন','এছে','এছেন','এন','এর','এরগুলো','এরগুলোর',
    'এরটা','এরটার','এরা','এল','এলো','এয়ে','এয়েছিল','রা''এয়েছিলেন','ও','ওয়ালা','ওরা',
    'ওয়া','কনা','করে','কামী','কারী','কালে','কে','কেই','খানা','গা','য়ে''গুলা','গুলি',
    'গুলো','গুলোতে','গুলোর','ঘর','চ্ছ','চ্ছি','চ্ছিল','চ্ছিলেন','চ্ছিস','য়েছে''চ্ছে','ছিলি',
    'ছিস','ছে','জন','জনক','জনিত','জনী','জা','জাত','জাদা','জাদী','টা','টার','টােরটা',
    'টি','টির','তম','তা','ছি''তে','তো','ত্ব','দার','দারি','দারী','দের','নবিস','না','নামা',
    'নী','পতি','পনা','পরায়ণ','প্রদ','প্রবণ','বত','বরাবর','বা','বাদ','বাদী','বাসী','বাহক',
    'বি','বিদ','বিষয়ক','বেন','ভান্ডার','ভাবে','ভাষী','ভুক','মন্দ','ময়','মি','মুখী','য়',
    'যোগ','যোগী','র','রছ','রব','লাম','লি','লে','লেন','শক্তি','শালা','শীল','সংক্রান্ত',
    'সংযোগী','সংস্থাপক','সমৃদ্ধ','স্তান','স্থান','হীন','ার','িস','ে','ে.ে','ে.েছিলেন','েছ',
    'েছিল','েছিলেন','েছে','েছেন','েন','ের','েরগুলো','েরগুলোর','েরটার',
    'েল','বাসী','লো','য়ে','য়েছিল','য়েছিলেন','য়','য়ে','য়েছিল','তে','ন'
    ]



class SimpleStemmer:
    """
    A simple and fast stemmer for Bangla language that removes prefixes and suffixes from words.

    ## Args:
        `vocabularies (list)`: List of valid words for checking after removing affixes.
        `prefixes (list)`: List of prefixes to be removed from words.
        `suffixes (list)`: List of suffixes to be removed from words.
        `use_caching (bool)`: Whether to use caching to speed up the stemming process.


    ## Example:
    ```python
    from bkit.stemmer import SimpleStemmer
    stemmer = SimpleStemmer()

    print(stemmer.sentence_stemmer("পৃথিবীর জনসংখ্যা ৮ বিলিয়নের কিছু কম"))
    >>> পৃথিবী জনসংখ্যা ৮ বিলিয়ন কিছু কম

    print(stemmer.word_stemmer("পৃথিবীর")
    >>> পৃথিবী
    ```

    ## Customization:
    ```python
    my_vocabularies = [..., ..., ...] # List of words
    my_prefixes = [..., ..., ...] # List of prefixes
    my_suffixes = [..., ..., ...] # List of suffixes

    stemmer = SimpleStemmer(
        vocabularies=my_vocabularies,
        prefixes=my_prefixes,
        suffixes=my_suffixes
    )
    stemmer.sentence_stemmer("ঢাকায় বাংলাদেশের একমাত্র রাজধানী।")
    ```
    ## Recommandation:
    If you care about accuracy we recommand to use bkit.lemmatizer instead of bkit.stemmer.
    """

    def __init__(
            self,
            vocabularies: Union[List[str], None] = None,
            prefixes: Union[List[str], None] = None,
            suffixes: Union[List[str], None] = None,
            use_caching: bool = True) -> None:

        self._valid_words = vocabularies
        self._prefixes = prefixes
        self._suffixes = suffixes
        self._use_caching = use_caching

        if prefixes and suffixes:
            self._prefixes = set(prefixes)
            self._suffixes = set(suffixes)
        else:
            self._prefixes = set(builtin_prefixes)
            self._suffixes = set(builtin_suffixes)

        if vocabularies is not None:
            self._valid_words = set(vocabularies)
        else:
            try:
                with importlib.resources.open_binary("bkit.stemmer.data", "words.pkl") as f:
                    self._valid_words = set(pickle.load(f))
            except Exception as e:
                raise Exception(f"Failed to load words.pkl: {str(e)}")

    def _is_bangla_word(self, word: str) -> str:
        return bool(re.match(r'^[\u0980-\u09FF]+$', word))


    def remove_prefix(self, word: str) -> str:
        for prefix in self._prefixes:
            if word.startswith(prefix):
                candidate = word[len(prefix):]
                if candidate in self._valid_words:
                    return candidate
        return word


    def remove_suffix(self, word: str) -> str:
        if len(word) <= 3:
            word = self._remove_sign(word)
            return word
        else:
            for suffix in self._suffixes:
                if word.endswith(suffix):
                    candidate = word[: -len(suffix)]
                    if candidate in self._valid_words:
                        return candidate
        return word


    def _remove_sign(self, word: str) -> str:
        signs = ['া', 'ি', 'ী', 'ু', 'ূ', 'ে', 'ৈ', 'ো', 'ৌ', 'ঁ', 'ং', 'ঃ']
        for sign in signs:
            if word.endswith(sign):
                return word[:-1]
        return word


    def _preprocess(self, text: str) -> str:
        normalizer = Normalizer()
        text = clean_punctuations(text)
        text = clean_multiple_spaces(text)
        text = clean_multiple_punctuations(text)
        text = clean_html(text)
        text = clean_emojis(text)
        text = clean_special_characters(text)
        text = clean_urls(text)
        text = clean_non_bangla(text)
        text = normalizer(text)
        return text.strip()


    @lru_cache(maxsize=1000000)
    def _caching_stemmer_imple(self, word: str) -> str:
        original_word = word
        word = self.remove_prefix(word)
        word = self.remove_suffix(word)
        if word in self._valid_words:
            return word
        if word in self._valid_words:
            return word
        word = self._remove_sign(word)
        if word in self._valid_words:
            return word
        return original_word


    def _stemmer_imple(self, word: str) -> str:
        original_word = word
        word = self.remove_prefix(word)
        word = self.remove_suffix(word)
        if word in self._valid_words:
            return word
        if word in self._valid_words:
            return word
        word = self._remove_sign(word)
        if word in self._valid_words:
            return word
        return original_word


    def word_stemmer(self, word: str) -> str:
        """
        Stems a word to its root form.

        Parameters
        ----------
        word : str
            The word to stem.

        Returns
        -------
        str
            The stemmed word.
        """
        original_word = word
        warnings.warn(
            "If you know what you are doing, It's recommended to use lemmatizer instead of stemmer."
        )
        if not isinstance(word, str):
            raise TypeError(f"Input '{word}' is not a string!")

        if word == "":
            raise ValueError(f"Input '{original_word}' is not a valid word!")
        if not self._is_bangla_word(word):
            warnings.warn(f"Word '{original_word}' is not a valid bangla word")
            return word

        if self._use_caching:
            word = self._caching_stemmer_imple(word)
        else:
            word = self._stemmer_imple(word)
        return word


    def sentence_stemmer(self, sentence: Union[str, list, List[str]]) -> str:
        """
        Stems a sentence to its root form.

        Parameters
        ----------
        sentence : Union[str, list, List[str]]
            The sentence to stem.

        Returns
        -------
        str
            The stemmed sentence.
        """
        if isinstance(sentence, list):
            sentence = " ".join(sentence)

        original_sentence = sentence
        sentence = self._preprocess(sentence)
        if sentence == "":
            raise ValueError(f"Input '{original_sentence}' is not a valid sentence!")

        return " ".join([
            self.word_stemmer(w) for w in tokenize(sentence)
            if w != ""
            ]
        )


# if __name__=="__main__":
#     stemmer = SimpleStemmer()
#     print(stemmer.sentence_stemmer("'পৃথিবীর জনসংখ্যা ৮ বিলিয়নের কিছু কম'"))
#     print(stemmer.sentence_stemmer("বিকেলে রোদ কিছুটা কমেছে।"))
#     print(stemmer.sentence_stemmer('ভোগান্তিতে পড়েন নগরবাসী'))
#     print(stemmer.sentence_stemmer("আমাদের বাড়িতে আজ একটি অনুষ্ঠান আছে।"))