"""Download a Project Gutenberg slice into data/ (not committed)."""

import sys
import urllib.request
from pathlib import Path

IDS = [1342, 11, 84, 1661, 2701, 98, 1232, 174, 345, 1952, 2554, 2600, 1400,
       76, 74, 5200, 205, 2814, 1080, 844, 215, 160, 43, 1260, 2591, 16328,
       3207, 1184, 120, 36, 35, 5230, 219, 408, 4300, 1399, 28054, 768, 2542, 1497]


def main(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for book_id in IDS:
        out = dest / f"pg{book_id}.txt"
        if out.exists():
            continue
        url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
        try:
            out.write_bytes(urllib.request.urlopen(url, timeout=60).read())
        except OSError as exc:
            print(f"skip {book_id}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "data"))
