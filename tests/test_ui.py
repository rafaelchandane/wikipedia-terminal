"""Tests for UI module."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wikipedia_tui import ui_curses


def test_escape_html():
    """Test HTML escaping function."""
    assert ui_curses._escape_html("<test>") == "&lt;test&gt;"
    assert ui_curses._escape_html("hello & world") == "hello &amp; world"


def test_clear_terminal():
    """Test clear terminal function exists and is callable."""
    assert callable(ui_curses.clear_terminal)
