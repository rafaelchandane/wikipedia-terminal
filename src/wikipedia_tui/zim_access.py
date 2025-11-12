"""
ZIM backend using zimply library - Server-free version.
Directly accesses ZIM files without any web server.
"""
import os
from typing import List, Optional
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


def search_zim(query: str, zim_path: Optional[str] = None, max_results: int = 100) -> List[str]:
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


def _html_to_text(html_str: str) -> str:
    """
    Convert HTML to plain text.
    
    Removes scripts, styles, and HTML tags while preserving basic formatting.
    
    Args:
        html_str: HTML content string
        
    Returns:
        Plain text version of HTML
    """
    # Remove script and style elements
    html_str = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", html_str)
    
    # Convert common HTML elements to text formatting
    html_str = re.sub(r"(?i)<br\s*/?>", "\n", html_str)
    html_str = re.sub(r"(?i)</p\s*>", "\n\n", html_str)
    html_str = re.sub(r"(?i)<li.*?>", "\n• ", html_str)
    html_str = re.sub(r"(?i)</h[1-6]>", "\n\n", html_str)
    
    # Remove all remaining HTML tags
    text = re.sub(r"<[^>]+>", "", html_str)
    
    # Decode HTML entities
    text = _html.unescape(text)
    
    # Clean up whitespace
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    
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