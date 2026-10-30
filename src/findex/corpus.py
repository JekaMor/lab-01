"""Lazy corpus intake: one document in memory at a time."""

import logging
from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple

log = logging.getLogger(__name__)


class Document(NamedTuple):
    doc_id: int
    path: Path
    text: str


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        log.warning("bad UTF-8 in %s; undecodable bytes replaced", path)
        return path.read_text(encoding="utf-8", errors="replace")


def iter_documents(root: Path) -> Iterator[Document]:
    """Yield every ``*.txt`` file under ``root`` as a Document, lazily."""
    for doc_id, path in enumerate(root.rglob("*.txt")):
        try:
            text = _read(path)
        except OSError as exc:
            log.warning("unreadable %s: %s", path, exc)
            continue
        yield Document(doc_id, path, text)
