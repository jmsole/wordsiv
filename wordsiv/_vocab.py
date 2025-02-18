from __future__ import annotations

from functools import lru_cache
from ._filter import _filter_wordcount
from importlib.abc import Traversable
import regex


class VocabEmptyError(Exception):
    pass


class VocabFormatError(Exception):
    pass


class Vocab:
    """A vocabulary of words and occurrence counts with metadata for filtering and punctuating.

    Attributes:
        lang (str): The language of the vocabulary.
        bicameral (bool): Specifies whether the vocabulary has uppercase and lowercase letters.
        punctuation (dict, optional): A dictionary or None for handling punctuation in generated text.
        data (str, optional): A TSV-formatted string with word-count pairs or a newline-delimited list of words.
        data_file (str | Traversable, optional): A path to a file to supply the data instead of the data attribute.
        meta (dict, optional): Additional metadata for the vocabulary.
    """

    def __init__(
        self,
        lang: str,
        bicameral: bool,
        punctuation: dict | None = None,
        data: str | None = None,
        data_file: str | Traversable | None = None,
        meta: dict | None = None,
    ):
        """Initializes the Vocab instance.

        Args:
            lang (str): The language of the vocabulary.
            bicameral (bool): Specifies whether the vocabulary has uppercase and lowercase letters.
            punctuation (dict, optional): A dictionary or None for handling punctuation in generated text.
            data (str, optional): A TSV-formatted string with word-count pairs or a newline-delimited list of words.
            data_file (str | Traversable, optional): A path to a file to supply the data instead of the data attribute.
            meta (dict, optional): Additional metadata for the vocabulary.
        """

        self.lang = lang
        self.bicameral = bicameral
        self.punctuation = punctuation
        self._data = data
        self.data_file = data_file
        self.meta = meta

        if data and data_file:
            raise ValueError("Cannot specify both 'data' and 'data_file'")
        elif data is None and not data_file:
            raise ValueError("Must specify either 'data' or 'data_file'")

    @property
    def data(self):
        """Returns raw data from parameter _data or data_file."""

        if self._data is not None:
            data = self._data
        elif getattr(self, "data_file", None):
            data = _read_file(self.data_file)
        if not data:
            raise VocabEmptyError(f"No data found in {self.data_file}")

        return data

    @property
    def wordcount_str(self) -> str:
        """Returns a TSV-formatted string with words and counts."""

        firstline = self.data.partition("\n")[0]

        if regex.match(r"[[:alpha:]]+\t\d+$", firstline):
            # if we have counts, return the original string
            return self.data
        elif regex.match(r"[[:alpha:]]+$", firstline):
            # if we just have newline-delimited words, add counts of 1
            return _add_counts_to_wordcount_str(self.data)
        else:
            raise VocabFormatError(
                "The vocab file is formatted incorrectly. "
                "Should be a TSV file with words and counts as columns, or a newline-delimited list of words."
            )

    @property
    def wordcount(self) -> tuple[tuple[str, int], ...]:
        """Returns a tuple of tuples with words and counts."""

        return _wordcount_str_to_wordcount_tuple(self.wordcount_str)

    def filter(self, **kwargs):
        return _filter_wordcount(self.wordcount_str, self.bicameral, **kwargs)


@lru_cache(maxsize=None)
def _read_file(file):
    with open(file, "r", encoding="utf8") as f:
        return f.read()


@lru_cache(maxsize=None)
def _wordcount_str_to_wordcount_tuple(wordcount_str):
    return tuple(
        (line.split()[0], int(line.split()[1])) for line in wordcount_str.splitlines()
    )


@lru_cache(maxsize=None)
def _add_counts_to_wordcount_str(wordcount_str):
    return "\n".join(f"{w}\t1" for w in wordcount_str.splitlines())
