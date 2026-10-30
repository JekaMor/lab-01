"""Streaming tokenizer.

Rules
-----
1. Text is NFC-normalised, then ``casefold()``-ed (``ß`` -> ``ss``).
2. A token is a run of letters/digits (Unicode-aware, so Cyrillic works).
3. Apostrophes (``'``, ``’``, ``ʼ``) *inside* a word are kept and written as
   ASCII ``'``: ``don't``, ``п'ять``. Leading/trailing ones are dropped.
4. Hyphens split words: ``well-known`` -> ``well``, ``known``.
5. Digits are tokens: ``3.14`` -> ``3``, ``14``; ``abc123`` stays one token.
6. Underscore is a separator.
7. A letter with a combining mark that has no precomposed form is split at
   the mark (a known limitation).
"""

import re
import unicodedata
from collections.abc import Iterator

_APOSTROPHES = str.maketrans({"’": "'", "ʼ": "'"})
_WORD = re.compile(r"[^\W_]+(?:'[^\W_]+)*")


def tokenize(text: str) -> Iterator[str]:
    normalised = unicodedata.normalize("NFC", text).casefold().translate(_APOSTROPHES)
    for match in _WORD.finditer(normalised):
        yield match.group()
