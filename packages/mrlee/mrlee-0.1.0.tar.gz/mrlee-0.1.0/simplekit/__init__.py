# __init__.py
from .file_utils import get_extension, writefile, readfile
from .string_utils import group, matchstr, mget, getindent
from .text_tools import templater, comment

# Optional: Define __all__ to explicitly specify what gets imported with `from simplekit import *`
# __all__ = [
#     "get_extension",
#     "writefile",
#     "readfile",
#     "group",
#     "matchstr",
#     "mget",
#     "templater",
# ]

# Optional: Add a package-level docstring
__doc__ = """
SimpleKit - A collection of simple and useful utilities for file and string operations.

This package provides the following utilities:
- File Utilities: Functions for reading, writing, and manipulating files.
- String Utilities: Functions for grouping, regex matching, and string manipulation.

Example usage:
    >>> from simplekit import readfile, writefile
    >>> writefile("example.txt", "Hello, World!")
    >>> readfile("example.txt")
    'Hello, World!'
"""
