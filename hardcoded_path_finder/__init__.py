"""Find absolute and user-specific paths that break portability of analysis code."""
from .core import scan_text, scan_path, PATTERNS

__version__ = "0.1.0"
__all__ = ["scan_text", "scan_path", "PATTERNS"]
