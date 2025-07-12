"""
WSJ Adapter - A package to download articles from the Wall Street Journal via the Wayback Machine.

This package provides the WSJAdapter class which allows you to:
- Query the Wayback Machine for archived WSJ pages
- Extract article links from those pages
- Download and parse article content
- Handle multiple topics and date ranges
"""

from .wsj_adapter import WSJAdapter, TOPICS, EXCLUDE_PATTERNS

__version__ = "0.0.1"
__author__ = "Ariana Christodoulou"
__email__ = "ariana.chr@gmail.com"

__all__ = ["WSJAdapter", "TOPICS", "EXCLUDE_PATTERNS"]
