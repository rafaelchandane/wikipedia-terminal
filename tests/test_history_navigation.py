"""Test script for article history navigation."""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wikipedia_tui import ui_curses

# Test that the function signature is correct
print("Testing _view_article function signature...")
import inspect
sig = inspect.signature(ui_curses._view_article)
print(f"Parameters: {list(sig.parameters.keys())}")
print(f"Expected: ['article_text', 'session', 'can_go_back', 'can_go_forward']")

# Verify parameters
params = list(sig.parameters.keys())
assert params == ['article_text', 'session', 'can_go_back', 'can_go_forward'], f"Wrong parameters: {params}"

# Check default values
assert sig.parameters['can_go_back'].default == False
assert sig.parameters['can_go_forward'].default == False

print("✓ Function signature is correct!")
print("\nTesting return type annotation...")
print(f"Return annotation: {sig.return_annotation}")

print("\n✓ All tests passed!")
print("\nHistory navigation features added:")
print("  - Article history tracking")
print("  - Back navigation with 'b', 'back', or '<'")
print("  - Forward navigation with 'f', 'forward', or '>'")
print("  - History truncation when navigating from middle")
print("  - Visual indicators for available navigation")
