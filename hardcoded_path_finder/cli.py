"""Command-line interface for hardcoded-path-finder."""
import argparse
import json
from collections import Counter

from .core import scan_path


def main(argv=None):
    ap = argparse.ArgumentParser(prog="hardcoded-path-finder", description="Find non-portable hard-coded paths.")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--summary", action="store_true", help="only counts per file")
    args = ap.parse_args(argv)
    hits, n = [], 0
    for p in args.paths:
        h, k = scan_path(p)
        hits += h
        n += k
    if args.json:
        print(json.dumps([h._asdict() for h in hits], indent=2))
    elif args.summary:
        for f, c in Counter(h.file for h in hits).most_common():
            print("%4d  %s" % (c, f))
    else:
        for h in hits:
            print("%s:%d:%d: [%s] %s" % (h.file, h.line, h.col, h.kind, h.path))
        if hits:
            print("\nTip: %s" % hits[0].suggestion)
    print("%d file(s) scanned, %d hard-coded path(s)" % (n, len(hits)))
    return 1 if hits else 0
