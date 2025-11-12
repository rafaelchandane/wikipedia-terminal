"""
ZIM backend using zimply library - Server-free version.
Directly accesses ZIM files without any web server.
"""
import os
from typing import List, Optional, Tuple
import re
import html as _html
import threading
import warnings

# Suppress zimply's pkg_resources deprecation warning
warnings.filterwarnings("ignore", message=".*pkg_resources.*")

try:
    from zimply.zimply import ZIMFile
except ImportError as e:
    raise ImportError(
        "Cannot import ZIMFile from zimply. Install it with: pip install zimply"
    ) from e

# Default ZIM path (can be overridden by environment variable)
DEFAULT_ZIM_PATH = os.environ.get("ZIM_PATH", "")

# Cache for opened ZIM files
_ZIM_CACHE = {}
_ZIM_CACHE_LOCK = threading.Lock()


def _resolve_path(zim_path: Optional[str]) -> str:
    """
    Resolve ZIM file path from parameter, environment variable, or default.
    
    Args:
        zim_path: Optional path to ZIM file
        
    Returns:
        Absolute path to ZIM file
        
    Raises:
        FileNotFoundError: If no valid ZIM path is found
    """
    path = zim_path or DEFAULT_ZIM_PATH
    if not path:
        raise FileNotFoundError(
            "No ZIM file path provided. Set ZIM_PATH environment variable or pass path parameter."
        )
    if not os.path.exists(path):
        raise FileNotFoundError(f"ZIM file not found: {path}")
    return os.path.abspath(path)


def _open_zim(path: str) -> ZIMFile:
    """
    Open ZIM file with caching.
    
    Args:
        path: Absolute path to ZIM file
        
    Returns:
        Opened ZIMFile instance
        
    Raises:
        RuntimeError: If ZIM file cannot be opened
    """
    with _ZIM_CACHE_LOCK:
        cached = _ZIM_CACHE.get(path)
        if cached:
            return cached
    
    try:
        zim_file = ZIMFile(path, 'utf-8')
        
        with _ZIM_CACHE_LOCK:
            _ZIM_CACHE[path] = zim_file
        
        return zim_file
    except Exception as e:
        raise RuntimeError(f"Failed to open ZIM file '{path}': {e}") from e


def search_zim(query: str, zim_path: str = "", max_results: int = 10000) -> List[Dict[str, str]]:
    """
    Search for articles in ZIM file using binary search.
    
    Performs efficient binary search through the sorted article index,
    then scans nearby entries for matches.
    
    Args:
        query: Search query string
        zim_path: Optional path to ZIM file
        max_results: Maximum number of results to return (default: 100)
        
    Returns:
        List of article titles matching the query
        
    Raises:
        TypeError: If query is not a string
        FileNotFoundError: If ZIM file not found
        RuntimeError: If search fails
    """
    if not isinstance(query, str):
        raise TypeError("Query must be a string")
    if not query.strip():
        return []
    
    path = _resolve_path(zim_path)
    
    try:
        zim = _open_zim(path)
        results = []
        
        query_normalized = query.replace(' ', '_')
        query_lower = query_normalized.lower()
        
        # Get article count from ZIM header
        article_count = zim.header_fields.get('articleCount', 0)
        if article_count == 0:
            return []
        
        # Binary search to find starting position
        left, right = 0, article_count - 1
        start_idx = 0
        
        while left <= right and left < article_count:
            mid = (left + right) // 2
            try:
                entry = zim.read_directory_entry_by_index(mid)
                if not isinstance(entry, dict):
                    break
                
                url = entry.get('url', '')
                if isinstance(url, bytes):
                    url = url.decode('utf-8', errors='ignore')
                
                # Extract article name (remove namespace prefix)
                article_name = url.split('/', 1)[-1] if '/' in url else url
                
                if article_name.lower() < query_lower:
                    left = mid + 1
                    start_idx = mid
                else:
                    right = mid - 1
            except Exception:
                break
        
        # Scan forward from starting position (limit scan range)
        max_scan = min(start_idx + 50000, article_count)
        
        for idx in range(start_idx, max_scan):
            try:
                entry = zim.read_directory_entry_by_index(idx)
                if not isinstance(entry, dict):
                    continue
                
                url = entry.get('url', '')
                namespace = entry.get('namespace', b'')
                
                if isinstance(url, bytes):
                    url = url.decode('utf-8', errors='ignore')
                if isinstance(namespace, bytes):
                    namespace = namespace.decode('utf-8', errors='ignore')
                
                # Only search article namespaces (A = Article, C = Category)
                if namespace not in ('A', 'C'):
                    continue
                
                # Extract article name
                article_name = url.split('/', 1)[-1] if '/' in url else url
                
                # Check if matches query (case-insensitive substring match)
                if query_lower in article_name.lower():
                    display_title = article_name.replace('_', ' ')
                    if display_title not in results:
                        results.append(display_title)
                        if len(results) >= max_results:
                            break
                
                # Stop scanning if we've gone past the query alphabetically
                if article_name.lower() > query_lower and not article_name.lower().startswith(query_lower[0]):
                    if len(results) > 0:
                        break
                    
            except Exception:
                continue
        
        return results
        
    except FileNotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"Search failed: {e}") from e


def _parse_table_to_ascii(html_str: str, max_width: int = 80) -> str:
    """
    Convert HTML tables to ASCII art with box-drawing characters.
    Optimized for performance and readability.
    
    Args:
        html_str: HTML string containing table
        max_width: Maximum total table width (default: 80)
        
    Returns:
        ASCII representation of the table, or empty string if table is too complex
    """
    # Find all rows
    row_matches = re.findall(r'(?is)<tr\b[^>]*>(.*?)</tr>', html_str)
    
    if not row_matches or len(row_matches) > 50:  # Skip very large tables
        return ""
    
    # Extract and clean cells
    rows = []
    tag_pattern = re.compile(r'<[^>]+>')
    cell_pattern = re.compile(r'(?is)<t[hd]\b[^>]*?>(.*?)</t[hd]>')
    
    for row_html in row_matches:
        cells = []
        for cell_match in cell_pattern.finditer(row_html):
            cell_content = cell_match.group(1)
            
            # Remove nested tables (can cause issues)
            cell_content = re.sub(r'(?is)<table\b[^>]*>.*?</table>', '', cell_content)
            
            # Remove images, references, and other non-text elements
            cell_content = re.sub(r'(?is)<(img|figure|svg)[^>]*>.*?</\1>', '', cell_content)
            cell_content = re.sub(r'(?is)<img[^>]*/?>', '', cell_content)
            cell_content = re.sub(r'(?is)<sup\b[^>]*>.*?</sup>', '', cell_content)  # Remove references
            
            # Clean remaining HTML tags
            cell_text = tag_pattern.sub(' ', cell_content)
            cell_text = _html.unescape(cell_text)
            cell_text = ' '.join(cell_text.split()).strip()  # Normalize whitespace
            
            # Only add non-empty cells
            cells.append(cell_text if cell_text else '')
        
        # Only add rows that have at least one non-empty cell
        if cells and any(cell for cell in cells):
            rows.append(cells)
    
    if not rows:
        return ""
    
    # Calculate optimal column widths
    col_count = max(len(row) for row in rows)
    if col_count == 0:
        return ""
    
    # Skip tables with too many columns - they won't display well
    if col_count > 6:  # Reduced from 15 - most terminals can't handle more
        return ""
    
    # Initialize column widths
    col_widths = [0] * col_count
    
    for row in rows:
        for i, cell in enumerate(row):
            if i < col_count:
                col_widths[i] = max(col_widths[i], len(cell))
    
    # If table has no content, skip it
    if sum(col_widths) == 0:
        return ""
    
    # Distribute available width more intelligently
    total_content_width = sum(col_widths)
    available_width = max_width - (col_count + 1) - (col_count * 2)  # Account for borders and padding
    
    # Set reasonable minimum and maximum widths per column
    min_col_width = 10  # At least 10 chars to be readable
    max_col_width = 50  # Don't let any column dominate
    
    if total_content_width > available_width and available_width > 0:
        # Scale down columns proportionally
        scale = available_width / total_content_width
        col_widths = [int(w * scale) for w in col_widths]
    
    # Apply min/max constraints
    col_widths = [max(min_col_width, min(w, max_col_width)) for w in col_widths]
    
    # If still too wide, give up - table won't fit
    if sum(col_widths) + (col_count + 1) + (col_count * 2) > max_width:
        return ""
    
    # Build ASCII table using list for efficiency
    result = []
    
    # Box-drawing characters
    chars = {
        'h': '─', 'v': '│',
        'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
        'lj': '├', 'rj': '┤', 'tj': '┬', 'bj': '┴', 'x': '┼'
    }
    
    # Helper to build horizontal line
    def make_hline(left, mid, right):
        parts = [left]
        for i, width in enumerate(col_widths):
            parts.append(chars['h'] * (width + 2))
            if i < col_count - 1:
                parts.append(mid)
        parts.append(right)
        return ''.join(parts)
    
    # Top border
    result.append(make_hline(chars['tl'], chars['tj'], chars['tr']))
    
    # Rows
    for row_idx, row in enumerate(rows):
        # Pad row to match column count
        while len(row) < col_count:
            row.append('')
        
        # Row content
        row_parts = [chars['v']]
        for cell, width in zip(row, col_widths):
            # Clean truncation - just cut at width
            if len(cell) > width:
                cell = cell[:width-1] + '…'
            else:
                cell = cell.ljust(width)
            row_parts.append(f' {cell} ')
            row_parts.append(chars['v'])
        result.append(''.join(row_parts))
        
        # Separator after header row (first row)
        if row_idx == 0 and len(rows) > 1:
            result.append(make_hline(chars['lj'], chars['x'], chars['rj']))
    
    # Bottom border
    result.append(make_hline(chars['bl'], chars['bj'], chars['br']))
    
    return '\n'.join(result)


def _parse_list_to_text(html_str: str, list_type: str, indent_level: int = 0, max_depth: int = 5) -> str:
    """
    Convert HTML lists to formatted text with proper indentation.
    Optimized with recursion limits and better string handling.
    
    Args:
        html_str: HTML string containing list
        list_type: 'ul' or 'ol'
        indent_level: Current nesting level
        max_depth: Maximum recursion depth to prevent stack overflow
        
    Returns:
        Formatted list text
    """
    # Prevent excessive nesting
    if indent_level >= max_depth:
        return ""
    
    indent = '  ' * indent_level
    items = []
    counter = 1
    
    # Compile patterns for reuse
    tag_pattern = re.compile(r'<[^>]+>')
    nested_ul_pattern = re.compile(r'(?is)<ul\b[^>]*>(.*?)</ul>')
    nested_ol_pattern = re.compile(r'(?is)<ol\b[^>]*>(.*?)</ol>')
    
    # Find all list items efficiently
    for match in re.finditer(r'(?is)<li\b[^>]*>(.*?)</li>', html_str):
        item_html = match.group(1)
        
        # Check for nested lists
        nested_ul = nested_ul_pattern.search(item_html)
        nested_ol = nested_ol_pattern.search(item_html)
        
        # Remove nested lists from content
        if nested_ul:
            item_html = item_html[:nested_ul.start()] + item_html[nested_ul.end():]
        if nested_ol:
            item_html = item_html[:nested_ol.start()] + item_html[nested_ol.end():]
        
        # Clean item text efficiently
        item_text = tag_pattern.sub(' ', item_html)
        item_text = _html.unescape(item_text)
        item_text = ' '.join(item_text.split()).strip()
        
        # Add bullet or number
        if item_text:
            if list_type == 'ol':
                items.append(f"{indent}{counter}. {item_text}")
                counter += 1
            else:
                items.append(f"{indent}• {item_text}")
        
        # Process nested lists recursively
        if nested_ul and indent_level + 1 < max_depth:
            nested_text = _parse_list_to_text(nested_ul.group(1), 'ul', indent_level + 1, max_depth)
            if nested_text:
                items.append(nested_text)
        
        if nested_ol and indent_level + 1 < max_depth:
            nested_text = _parse_list_to_text(nested_ol.group(1), 'ol', indent_level + 1, max_depth)
            if nested_text:
                items.append(nested_text)
    
    return '\n'.join(items) if items else ""


# Compile regex patterns once for performance
_HTML_PATTERNS = {
    'script_style': re.compile(r"(?is)<(script|style).*?>.*?</\1>"),
    'nav': re.compile(r"(?is)<nav\b[^>]*>.*?</nav>"),
    'aside': re.compile(r"(?is)<aside\b[^>]*>.*?</aside>"),
    'nav_divs': re.compile(r'(?is)<div\b[^>]*class="[^"]*(?:sidebar|navbox|navigation|mw-navigation|toc|infobox|metadata|ambox)[^"]*"[^>]*>.*?</div>'),
    'nav_tables': re.compile(r'(?is)<table\b[^>]*class="[^"]*(?:sidebar|navbox|vertical-navbox)[^"]*"[^>]*>.*?</table>'),  # Removed infobox from here
    'nav_id_divs': re.compile(r'(?is)<div\b[^>]*id="[^"]*(?:toc|navigation|sidebar|nav)[^"]*"[^>]*>.*?</div>'),
    'early_lists': re.compile(r'(?is)^(.*?)<[uo]l\b[^>]*>.*?</[uo]l>(.*?<p\b)'),
    'table': re.compile(r'(?is)<table\b[^>]*>.*?</table>'),
    'ul': re.compile(r'(?is)<ul\b[^>]*>(.*?)</ul>'),
    'ol': re.compile(r'(?is)<ol\b[^>]*>(.*?)</ol>'),
    'dl': re.compile(r'(?is)<dl\b[^>]*>(.*?)</dl>'),
    'dt': re.compile(r'(?is)<dt\b[^>]*>(.*?)</dt>'),
    'dd': re.compile(r'(?is)<dd\b[^>]*>(.*?)</dd>'),
    'pre': re.compile(r'(?is)<pre\b[^>]*>(.*?)</pre>'),
    'br': re.compile(r"(?i)<br\s*/?>"),
    'p_end': re.compile(r"(?i)</p\s*>"),
    'h_end': re.compile(r"(?i)</h[1-6]>"),
    'code_start': re.compile(r"(?i)<code\b[^>]*>"),
    'code_end': re.compile(r"(?i)</code>"),
    'tags': re.compile(r"<[^>]+>"),
    'multi_newlines': re.compile(r"\n\s*\n\s*\n+"),
    'spaces': re.compile(r"[ \t]+"),
    'trailing_space': re.compile(r" \n"),
    'leading_bullets': re.compile(r"^(\s*•\s*[^\n]*\n)+", re.MULTILINE),
}


def _html_to_text(html_str: str) -> str:
    """
    Convert HTML to plain text with enhanced formatting for tables and lists.
    Optimized with compiled regex patterns and efficient string operations.
    
    Removes scripts, styles, and HTML tags while preserving structure.
    Tables are rendered as ASCII art, lists are properly indented.
    
    Args:
        html_str: HTML content string
        
    Returns:
        Plain text version of HTML with formatted tables and lists
    """
    if not html_str:
        return ""
    
    # Remove script and style elements
    html_str = _HTML_PATTERNS['script_style'].sub("", html_str)
    
    # Remove navigation and non-content elements (optimized order for performance)
    html_str = _HTML_PATTERNS['nav'].sub("", html_str)
    html_str = _HTML_PATTERNS['aside'].sub("", html_str)
    html_str = _HTML_PATTERNS['nav_divs'].sub("", html_str)
    html_str = _HTML_PATTERNS['nav_tables'].sub("", html_str)
    html_str = _HTML_PATTERNS['nav_id_divs'].sub("", html_str)
    html_str = _HTML_PATTERNS['early_lists'].sub(r'\1\2', html_str)
    
    # Process tables - replace with ASCII art
    def replace_table(match):
        table_html = match.group(0)
        table_lower = table_html.lower()
        
        # Skip ONLY navigation-specific tables
        # Be very selective - we want to keep data tables
        skip_keywords = ['navbox', 'vertical-navbox', 'ambox', 'mbox-small']
        if any(keyword in table_lower for keyword in skip_keywords):
            return ""
        
        # Skip sidebar tables (usually narrow info panels)
        if 'class="sidebar' in table_lower:
            return ""
            
        # Try to render all other tables
        ascii_table = _parse_table_to_ascii(table_html, max_width=100)  # Increased from 78 to 100
        if ascii_table:
            return f"\n\n{ascii_table}\n\n"
        
        # If table parsing failed, return empty (don't show broken table)
        return ""
    
    html_str = _HTML_PATTERNS['table'].sub(replace_table, html_str)
    
    # Process lists
    html_str = _HTML_PATTERNS['ul'].sub(
        lambda m: "\n" + _parse_list_to_text(m.group(1), 'ul') + "\n", 
        html_str
    )
    html_str = _HTML_PATTERNS['ol'].sub(
        lambda m: "\n" + _parse_list_to_text(m.group(1), 'ol') + "\n", 
        html_str
    )
    
    # Process definition lists
    def replace_dl(match):
        dl_content = match.group(1)
        terms = _HTML_PATTERNS['dt'].findall(dl_content)
        defs = _HTML_PATTERNS['dd'].findall(dl_content)
        
        if not terms:
            return ""
        
        result = []
        for term, definition in zip(terms, defs):
            term_text = _HTML_PATTERNS['tags'].sub('', term).strip()
            def_text = _HTML_PATTERNS['tags'].sub('', definition).strip()
            if term_text:
                term_text = _html.unescape(term_text)
                def_text = _html.unescape(def_text)
                result.append(f"\n{term_text}:")
                if def_text:
                    result.append(f"  {def_text}")
        
        return '\n'.join(result) + '\n' if result else ''
    
    html_str = _HTML_PATTERNS['dl'].sub(replace_dl, html_str)
    
    # Preserve code blocks with indentation
    def replace_pre(match):
        code_content = match.group(1)
        code_text = _HTML_PATTERNS['tags'].sub('', code_content)
        code_text = _html.unescape(code_text)
        if not code_text.strip():
            return ""
        lines = code_text.split('\n')
        indented = '\n'.join('    ' + line for line in lines if line.strip())
        return f"\n\n{indented}\n\n" if indented else ""
    
    html_str = _HTML_PATTERNS['pre'].sub(replace_pre, html_str)
    
    # Convert remaining common HTML elements
    html_str = _HTML_PATTERNS['br'].sub("\n", html_str)
    html_str = _HTML_PATTERNS['p_end'].sub("\n\n", html_str)
    html_str = _HTML_PATTERNS['h_end'].sub("\n\n", html_str)
    html_str = _HTML_PATTERNS['code_start'].sub("`", html_str)
    html_str = _HTML_PATTERNS['code_end'].sub("`", html_str)
    
    # Remove all remaining HTML tags
    text = _HTML_PATTERNS['tags'].sub("", html_str)
    
    # Decode HTML entities
    text = _html.unescape(text)
    
    # Clean up whitespace efficiently
    text = _HTML_PATTERNS['multi_newlines'].sub("\n\n", text)  # Max 2 newlines
    text = _HTML_PATTERNS['spaces'].sub(" ", text)
    text = _HTML_PATTERNS['trailing_space'].sub("\n", text)
    
    # Remove leading bullet points (navigation remnants)
    text = _HTML_PATTERNS['leading_bullets'].sub("", text)
    
    return text.strip()

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" \n", "\n", text)  # Remove trailing spaces
    
    # Remove leading bullet points (navigation remnants)
    text = re.sub(r"^(\s*•\s*[^\n]*\n)+", "", text, flags=re.MULTILINE)
    
    return text.strip()


def get_article_content(title: str, zim_path: Optional[str] = None) -> Optional[str]:
    """
    Retrieve article content by title.
    
    Searches for the article in multiple namespaces and converts HTML to plain text.
    
    Args:
        title: Article title
        zim_path: Optional path to ZIM file
        
    Returns:
        Article content as plain text, or None if not found
        
    Raises:
        TypeError: If title is not a string
        FileNotFoundError: If ZIM file not found
        RuntimeError: If retrieval fails
    """
    if not isinstance(title, str):
        raise TypeError("Title must be a string")
    
    path = _resolve_path(zim_path)
    
    try:
        zim = _open_zim(path)
        
        url_normalized = title.replace(' ', '_')
        
        # Try different namespace/URL combinations
        # A = Article namespace, C = Category namespace, - = Main namespace
        patterns = [
            ('A', url_normalized),
            ('C', url_normalized),
            ('-', url_normalized),
        ]
        
        article = None
        for namespace, url in patterns:
            try:
                article = zim.get_article_by_url(namespace, url)
                if article:
                    break
            except Exception:
                continue
        
        if not article:
            return None
        
        # Extract content from article object
        content = None
        
        # Try dictionary access (some zimply versions return dict)
        if isinstance(article, dict):
            content = article.get('data') or article.get('content') or article.get('body')
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='replace')
        
        # Try .data attribute (Article objects)
        if not content and hasattr(article, 'data'):
            try:
                data = article.data
                if isinstance(data, bytes):
                    content = data.decode('utf-8', errors='replace')
                elif callable(data):
                    data_result = data()
                    if isinstance(data_result, bytes):
                        content = data_result.decode('utf-8', errors='replace')
                    else:
                        content = str(data_result)
                else:
                    content = str(data)
            except Exception:
                pass
        
        if not content:
            return None
        
        # Convert HTML to plain text if content contains HTML tags
        if isinstance(content, str) and any(tag in content.lower() for tag in ["<html", "<body", "<p>", "<div"]):
            return _html_to_text(content)
        
        return content
    
    except FileNotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve article '{title}': {e}") from e


def close_all():
    """
    Close all cached ZIM files.
    
    Should be called on application shutdown to ensure proper cleanup.
    """
    with _ZIM_CACHE_LOCK:
        for zim_file in _ZIM_CACHE.values():
            try:
                if hasattr(zim_file, 'close'):
                    zim_file.close()
            except Exception:
                pass
        _ZIM_CACHE.clear()