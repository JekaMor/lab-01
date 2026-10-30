"""Corpus statistics in a single pass: ``python -m findex.stats data/``."""

import argparse
import time
import tracemalloc
from collections import Counter
from collections.abc import Sequence
from itertools import islice
from pathlib import Path
from typing import NamedTuple

from findex.corpus import iter_documents
from findex.tokenize import tokenize


class Stats(NamedTuple):
    documents: int
    tokens: int
    vocabulary: int
    top: tuple[tuple[str, int], ...]


def _summarise(documents: int, counts: Counter[str], top: int) -> Stats:
    return Stats(documents, counts.total(), len(counts), tuple(counts.most_common(top)))


def lazy_stats(root: Path, limit: int | None = None, top: int = 50) -> Stats:
    """Stream documents -> tokens -> Counter; only the Counter grows."""
    counts: Counter[str] = Counter()
    documents = 0
    for doc in islice(iter_documents(root), limit):
        documents += 1
        counts.update(tokenize(doc.text))
    return _summarise(documents, counts, top)


def eager_stats(root: Path, limit: int | None = None, top: int = 50) -> Stats:
    """Deliberately greedy: every text, then every token, held in lists."""
    docs = list(islice(iter_documents(root), limit))
    token_lists = [list(tokenize(doc.text)) for doc in docs]
    counts: Counter[str] = Counter()
    for tokens in token_lists:
        counts.update(tokens)
    return _summarise(len(docs), counts, top)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="findex.stats", description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--limit", type=int, help="only the first N documents")
    parser.add_argument("--top", type=int, default=50)
    parser.add_argument("--eager", action="store_true", help="use the list-based version")
    args = parser.parse_args(argv)

    run = eager_stats if args.eager else lazy_stats
    tracemalloc.start()
    started = time.perf_counter()
    stats = run(args.root, args.limit, args.top)
    elapsed = time.perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"mode:         {'eager' if args.eager else 'lazy'}")
    print(f"documents:    {stats.documents}")
    print(f"tokens:       {stats.tokens}")
    print(f"vocabulary:   {stats.vocabulary}")
    print(f"elapsed:      {elapsed:.2f} s")
    print(f"peak memory:  {peak / 2**20:.1f} MiB")
    print(f"top {args.top}:")
    for term, count in stats.top:
        print(f"  {term:<20}{count}")


if __name__ == "__main__":
    main()
