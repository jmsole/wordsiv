from .fontinfo import FontInfo
from functools import lru_cache
import pkg_resources
import re


# utilties
def installed_source_modules():
    packages = []
    for entry_point in pkg_resources.iter_entry_points("wordsiv_source_modules"):
        packages.append(entry_point.load())

    return packages


def all_utf8():
    return "".join(chr(c) for c in range(1114111))


@lru_cache(maxsize=None)
def has_glyphs(word, available_glyphs_string):
    """
    Are all the chars in word in available_glyphs_string?

    Example:
    >>> has_glyphs("speaker", "sperk")
    False
    >>> has_glyphs("speaker", "aekrps")
    True
    >>> has_glyphs("dog,cat", "dogcat")
    False
    """

    if available_glyphs_string:
        return all(char in available_glyphs_string for char in word)
    else:
        return True


@lru_cache(maxsize=None)
def has_glyph_position(word, glyph, position):
    """
    Are all the chars in word in glyph?

    Example:
    >>> has_glyphs("speaker", "sperk")
    False
    >>> has_glyphs("speaker", "aekrps")
    True
    >>> has_glyphs("dog,cat", "dogcat")
    False
    """
    positions = (
        ("isol", r"^" + re.escape(glyph) + r"$"),
        (
            "init_fina",
            r"^"
            + re.escape(glyph)
            + r"[^"
            + re.escape(glyph)
            + r"]*"
            + re.escape(glyph)
            + r"$",
        ),
        (
            "init_medi_fina",
            r"^"
            + re.escape(glyph)
            + r".*"
            + re.escape(glyph)
            + r"+.*"
            + re.escape(glyph)
            + r"$",
        ),
        (
            "init_medi",
            r"^"
            + re.escape(glyph)
            + r".*["
            + re.escape(glyph)
            + r"]+.*[^"
            + re.escape(glyph)
            + r"]$",
        ),
        (
            "medi_fina",
            r"\B"
            + re.escape(glyph)
            + r".*["
            + re.escape(glyph)
            + r"]*"
            + re.escape(glyph)
            + r"\b",
        ),
        (
            "medi",
            r"^[^"
            + re.escape(glyph)
            + r"].*"
            + re.escape(glyph)
            + r"+.*[^"
            + re.escape(glyph)
            + r"]$",
        ),
        ("init", r"^" + re.escape(glyph) + r"[^" + re.escape(glyph) + r"]+$"),
        ("fina", r"^[^" + re.escape(glyph) + r"]+" + re.escape(glyph) + r"$"),
    )
    regex_string = ""
    for pos, term in positions:
        if position == pos:
            regex_string = term

    if re.search(regex_string, word):
        return True
    else:
        return False


# A Dictionary with a hash represented by its keys and values
class Hashabledict(dict):
    def __hash__(self):
        return hash((frozenset(self), frozenset(self.values())))


class HashabledictKeys(dict):
    def __hash__(self):
        return hash(frozenset(self))
