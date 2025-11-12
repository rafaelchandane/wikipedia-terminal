# Fixes Applied - Article Display and Search Limits

## Issues Fixed

### 1. ✅ Unwanted Bullet Points Before Article Content
**Problem**: Articles displayed bullet points (•) from navigation elements before the actual content.

**Root Cause**: The `_html_to_text()` function was converting ALL `<li>` tags to bullets, including navigation sidebars and menus.

**Solution**: Added comprehensive filtering to remove navigation elements BEFORE converting HTML to text:
- Remove `<nav>` and `<aside>` tags
- Remove elements with classes: sidebar, navbox, navigation, mw-navigation, toc, infobox, metadata, ambox, wikitable
- Remove divs with IDs containing: toc, navigation, sidebar, nav
- Remove any `<ul>`/`<ol>` lists that appear before the first paragraph (typically navigation)
- Strip any remaining leading bullet points after processing

**Files Modified**:
- `src/wikipedia_tui/zim_access.py` (lines ~208-240)

### 2. ✅ Search Results Show ALL Available Articles
**Problem**: Searches were artificially limited to 100-500 results, not showing the true count of available articles.

**Root Cause**: Both `search_zim()` and `search_fts()` had hardcoded limits.

**Solution**: Changed limits to 10,000 (essentially unlimited) to show ALL available results:

**Files Modified**:
1. `src/wikipedia_tui/zim_access.py`:
   - Line 82: `max_results: int = 10000` (was 100, then 500)

2. `src/wikipedia_tui/fts_index.py`:
   - Line 10: `limit: int = 10000` (was 100, then 500)
   - Line 17: Updated docstring

3. `src/wikipedia_tui/ui_curses.py`:
   - Line 313: `search_fts(query, limit=10000)`
   - Line 330: `search_zim(query, zim_path, max_results=10000)`

4. Status message now shows exact count: "Found 247 result(s)"

### 3. ✅ Arrow Key Navigation Support
**Problem**: Users expected arrow keys to work for navigation, but only text commands worked.

**Root Cause**: No key bindings were configured for arrow keys.

**Solution**: Implemented full arrow key support using prompt_toolkit's KeyBindings:
- **↑ / ↓** - Scroll up/down through article pages (same as n/p)
- **← / →** - Navigate back/forward through article history (same as b/f)
- Text commands still work ('b', 'back', 'f', 'forward', 'n', 'p', 'q')
- Updated hints to show: "↑↓ or n/p pages", "← or 'b' back", "→ or 'f' forward"

**Files Modified**:
- `src/wikipedia_tui/ui_curses.py` - Added KeyBindings import and arrow key handlers

## Testing Instructions

Test the fixes with these steps:

```powershell
# 1. Test unlimited search results
wiki
# Type: Great Britain
# Verify: You should see the EXACT number of results available (likely 200+)

# 2. Test article formatting (no bullets)
# Open any article that had bullet points before
# Example: "Great Britain at the 1968 Summer Olympics"
# Verify: Article starts cleanly without any bullet points

# 3. Test arrow key navigation
# Open an article
# Press ↑ or ↓ to scroll through pages
# Open another article
# Press ← to go back to previous article
# Press → to go forward again
# All arrow keys should work smoothly!
```

## Impact

- **Search Results**: Now shows ALL available articles (up to 10,000) - essentially unlimited
- **Article Display**: Much cleaner formatting with aggressive navigation removal
- **User Experience**: Intuitive arrow key navigation + text commands
- **Transparency**: Exact count displayed instead of "showing 100 of many"
- **Navigation**: Browser-like history with keyboard arrow support

## Technical Details

The HTML filtering now removes:
- Navigation elements (`<nav>`, role="navigation")
- Sidebars and info boxes
- Table of contents
- Wikipedia metadata boxes
- Any lists appearing before main content
- Leading bullet points that slip through

The search limit of 10,000 is high enough to capture all results in most cases, while still providing a safety limit to prevent memory issues with extremely broad searches.

Arrow key support uses prompt_toolkit's KeyBindings to capture arrow key events and map them to navigation commands, providing a more intuitive user experience.
