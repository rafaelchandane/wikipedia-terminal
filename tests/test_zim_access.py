"""Tests for ZIM access module."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wikipedia_tui import zim_access


def test_search_empty_query():
    """Test that empty queries return empty results."""
    result = zim_access.search_zim("", None)
    assert result == []


def test_search_query_type_validation():
    """Test that non-string queries raise TypeError."""
    try:
        zim_access.search_zim(123, None)  # type: ignore
        assert False, "Should have raised TypeError"
    except TypeError:
        assert True
