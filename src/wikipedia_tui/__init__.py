"""
Wikipedia Terminal - Offline Wikipedia reader for the terminal.

A fast, offline Wikipedia reader that works directly with ZIM files.
No web server required.
"""

__version__ = "0.1.0"
__author__ = "Rafael Chandane"
__license__ = "MIT"

from .ui_curses import main, run_prompt_ui
from . import zim_access

__all__ = ["main", "run_prompt_ui", "zim_access"]