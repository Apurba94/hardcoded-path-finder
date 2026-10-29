"""Regex scanner for hard-coded paths inside string literals of scripts and notebooks."""
import json
import os
import re
from collections import namedtuple

Hit = namedtuple("Hit", "file line col kind path suggestion")

PATTERNS = [
    ("windows-drive", re.compile(r"(?<![A-Za-z])[A-Za-z]:(?:\\\\|\\|/)(?:[^\s\"'<>|*?]+)")),
    ("unc-share", re.compile(r"\\\\\\\\?[A-Za-z0-9_.$-]+\\\\?\\[^\s\"']+")),
    ("unix-home", re.compile(r"/(?:home|Users)/[A-Za-z0-9_.-]+(?:/[^\s\"'<>|]*)?")),
    ("tilde-home", re.compile(r"(?<![\w/])~/[^\s\"'<>|]*")),
    ("mounted-volume", re.compile(r"/(?:Volumes|mnt|media)/[A-Za-z0-9_. -]+(?:/[^\s\"'<>|]*)?")),
    ("cloud-sync", re.compile(r"(?i)[^\s\"']*(?:Dropbox|OneDrive|Google Drive|iCloud)[^\s\"']*")),
]
EXTENSIONS = (".py", ".r", ".rmd", ".qmd", ".m", ".jl", ".sh", ".bat", ".ps1", ".do", ".sas", ".ipynb", ".json",
              ".yaml", ".yml", ".toml", ".cfg", ".ini", ".tex", ".mk", "makefile")
_STRING = re.compile(r"(?P<q>\"\"\"|'''|\"|')(?P<body>.*?)(?P=q)", re.S)
_URL = re.compile(r"[a-z][a-z0-9+.-]*://\S+", re.I)


def _suggest(kind, path):
    if kind in ("windows-drive", "unix-home", "tilde-home", "mounted-volume", "cloud-sync"):
        return "use a path relative to the project root (e.g. pathlib.Path(__file__).parent / 'data') or a config/env variable"
    return "read the location from a configuration file or environment variable"


def scan_text(text, filename="<text>", strings_only=True):
    """Find hard-coded paths. With strings_only, only string literals are scanned (fewer false positives
    in code files); config-like files should be scanned with strings_only=False."""
    hits = []
    regions = [(m.start("body"), m.group("body")) for m in _STRING.finditer(text)] if strings_only else [(0, text)]
    line_starts = [0] + [m.end() for m in re.finditer("\n", text)]

    def loc(pos):
        lo, hi = 0, len(line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if line_starts[mid] <= pos:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1, pos - line_starts[lo] + 1

    seen = set()
    for offset, body in regions:
        masked = _URL.sub(lambda m: " " * len(m.group(0)), body)
        for kind, rx in PATTERNS:
            for m in rx.finditer(masked):
                pos = offset + m.start()
                if any(a <= pos < b for a, b in seen):
                    continue
                seen.add((pos, offset + m.end()))
                line, col = loc(pos)
                hits.append(Hit(filename, line, col, kind, m.group(0).rstrip(".,;)"), _suggest(kind, m.group(0))))
    return sorted(hits, key=lambda h: (h.line, h.col))


def _notebook_text(path):
    with open(path, encoding="utf-8") as fh:
        nb = json.load(fh)
    return "\n".join("".join(c.get("source", "")) if isinstance(c.get("source"), list) else c.get("source", "")
                     for c in nb.get("cells", []) if c.get("cell_type") == "code")


def scan_path(root, extensions=EXTENSIONS):
    files = []
    if os.path.isfile(root):
        files = [root]
    else:
        for dp, dns, fns in os.walk(root):
            dns[:] = [d for d in dns if d not in (".git", ".venv", "venv", "node_modules", "__pycache__", ".ipynb_checkpoints")]
            files += [os.path.join(dp, f) for f in sorted(fns) if f.lower().endswith(extensions) or f.lower() in extensions]
    hits = []
    for f in files:
        low = f.lower()
        if low.endswith(".ipynb"):
            text, strings_only = _notebook_text(f), True
        else:
            with open(f, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            strings_only = low.endswith((".py", ".r", ".rmd", ".qmd", ".m", ".jl"))
        hits += scan_text(text, f, strings_only)
    return hits, len(files)
