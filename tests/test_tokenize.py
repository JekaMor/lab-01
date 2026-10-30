import inspect
import unicodedata

from findex.tokenize import tokenize


def toks(text):
    return list(tokenize(text))


def test_is_generator_function():
    assert inspect.isgeneratorfunction(tokenize)


def test_empty_string():
    assert toks("") == []


def test_mixed_case_and_punctuation():
    assert toks("Hello, World! It works.") == ["hello", "world", "it", "works"]


def test_cyrillic():
    assert toks("Привіт, СВІТЕ! Це тест.") == ["привіт", "світе", "це", "тест"]


def test_combining_mark_matches_precomposed():
    decomposed = "café"
    assert toks(decomposed) == toks("café") == ["café"]
    assert unicodedata.is_normalized("NFC", toks(decomposed)[0])


def test_casefold_not_lower():
    assert toks("Straße STRASSE") == ["strasse", "strasse"]


def test_apostrophe_kept_inside_word():
    assert toks("don't п'ять") == ["don't", "п'ять"]


def test_typographic_apostrophe_normalised():
    assert toks("don’t") == ["don't"]


def test_leading_and_trailing_apostrophes_dropped():
    assert toks("'quoted' words'") == ["quoted", "words"]


def test_hyphen_splits_words():
    assert toks("well-known state-of-the-art") == [
        "well", "known", "state", "of", "the", "art",
    ]


def test_digits_are_tokens():
    assert toks("Python 3.14 in 2026, abc123") == [
        "python", "3", "14", "in", "2026", "abc123",
    ]


def test_underscore_is_a_separator():
    assert toks("snake_case") == ["snake", "case"]


def test_lazy_nothing_consumed_before_next():
    gen = tokenize("a b c")
    assert next(gen) == "a"
