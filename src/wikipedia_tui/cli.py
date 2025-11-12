"""
Command-line interface for Wikipedia Terminal.
Provides multiple modes: interactive UI, quick search, direct article access, and index building.
"""
import argparse
import sys
import os
import json
import tempfile
from typing import Optional, List

try:
    from . import zim_access
    from . import fts_index
    from . import ui_curses
except ImportError:
    import zim_access  # type: ignore
    import fts_index  # type: ignore
    import ui_curses  # type: ignore


# Cache file for storing last search results
def _get_cache_file() -> str:
    """Get path to cache file for storing last search results."""
    cache_dir = tempfile.gettempdir()
    return os.path.join(cache_dir, ".wiki_last_search.json")


def _save_search_results(results: List[str], query: str, zim_path: str) -> None:
    """Save search results to cache file."""
    try:
        cache_data = {
            "query": query,
            "zim_path": zim_path,
            "results": results
        }
        with open(_get_cache_file(), 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # Silently fail if cache write fails


def _load_search_results() -> Optional[dict]:
    """Load last search results from cache file."""
    try:
        cache_file = _get_cache_file()
        if not os.path.exists(cache_file):
            return None
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def cmd_interactive(args: argparse.Namespace) -> int:
    """Launch interactive UI mode."""
    ui_curses.main()
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    """Quick search mode - display results and exit."""
    query = ' '.join(args.query)
    zim_path = args.zim or os.environ.get("ZIM_PATH", "")
    
    if not zim_path or not os.path.exists(zim_path):
        print("Error: No ZIM file found.", file=sys.stderr)
        print("Set ZIM_PATH environment variable or use --zim option.", file=sys.stderr)
        return 1
    
    try:
        # Try FTS search first if available
        results = []
        if fts_index is not None:
            try:
                fts_results = fts_index.search_fts(query)
                if fts_results:
                    results = [r["title"] for r in fts_results]
            except Exception:
                pass
        
        # Fall back to ZIM search
        if not results:
            results = zim_access.search_zim(query, zim_path, max_results=args.limit)
        
        if not results:
            print(f"No results found for: {query}")
            return 1
        
        print(f"Found {len(results)} result(s) for '{query}':\n")
        for i, title in enumerate(results, 1):
            print(f"{i:3d}. {title}")
        
        # Save results to cache for 'wiki read N' command
        _save_search_results(results, query, zim_path)
        print(f"\nTip: Use 'wiki read <number>' to open an article from this list")
        
        return 0
        
    except Exception as e:
        print(f"Search error: {e}", file=sys.stderr)
        return 1


def cmd_read(args: argparse.Namespace) -> int:
    """Read an article from the last search results by number."""
    number = args.number
    
    # Load last search results
    cache = _load_search_results()
    if not cache:
        print("Error: No recent search found.", file=sys.stderr)
        print("Run 'wiki search <query>' first, then use 'wiki read <number>'", file=sys.stderr)
        return 1
    
    results = cache.get("results", [])
    zim_path = cache.get("zim_path", "")
    query = cache.get("query", "")
    
    if not results:
        print("Error: No results in last search.", file=sys.stderr)
        return 1
    
    if number < 1 or number > len(results):
        print(f"Error: Number must be between 1 and {len(results)}", file=sys.stderr)
        print(f"Last search for '{query}' returned {len(results)} results.", file=sys.stderr)
        return 1
    
    # Get the article title
    title = results[number - 1]
    
    try:
        content = zim_access.get_article_content(title, zim_path)
        
        if not content:
            print(f"Article not found: {title}", file=sys.stderr)
            return 1
        
        # Print article with title header
        print("=" * 80)
        print(title.upper())
        print("=" * 80)
        print()
        print(content)
        print()
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"Error reading article: {e}", file=sys.stderr)
        return 1


def cmd_get(args: argparse.Namespace) -> int:
    """Get and display a specific article."""
    title = ' '.join(args.title)
    zim_path = args.zim or os.environ.get("ZIM_PATH", "")
    
    if not zim_path or not os.path.exists(zim_path):
        print("Error: No ZIM file found.", file=sys.stderr)
        print("Set ZIM_PATH environment variable or use --zim option.", file=sys.stderr)
        return 1
    
    try:
        content = zim_access.get_article_content(title, zim_path)
        
        if not content:
            print(f"Article not found: {title}", file=sys.stderr)
            return 1
        
        # Print article with title header
        print("=" * 80)
        print(title.upper())
        print("=" * 80)
        print()
        print(content)
        print()
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"Error retrieving article: {e}", file=sys.stderr)
        return 1


def cmd_quick(args: argparse.Namespace) -> int:
    """Quick mode - search and display first matching article."""
    query = ' '.join(args.query)
    zim_path = args.zim or os.environ.get("ZIM_PATH", "")
    
    if not zim_path or not os.path.exists(zim_path):
        print("Error: No ZIM file found.", file=sys.stderr)
        print("Set ZIM_PATH environment variable or use --zim option.", file=sys.stderr)
        return 1
    
    try:
        # Search for articles
        results = []
        if fts_index is not None:
            try:
                fts_results = fts_index.search_fts(query, limit=1)
                if fts_results:
                    results = [r["title"] for r in fts_results]
            except Exception:
                pass
        
        if not results:
            results = zim_access.search_zim(query, zim_path, max_results=1)
        
        if not results:
            print(f"No results found for: {query}", file=sys.stderr)
            return 1
        
        # Get first article
        title = results[0]
        content = zim_access.get_article_content(title, zim_path)
        
        if not content:
            print(f"Could not retrieve article: {title}", file=sys.stderr)
            return 1
        
        # Display article
        print("=" * 80)
        print(title.upper())
        print("=" * 80)
        print()
        print(content)
        print()
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_build_index(args: argparse.Namespace) -> int:
    """Build FTS5 search index."""
    try:
        # Import the build script
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))
        import build_fts_index  # type: ignore
        
        # Call the build function
        build_fts_index.build_index(
            args.zim,
            args.output,
            batch=args.batch,
            replace=args.replace
        )
        
        return 0
        
    except Exception as e:
        print(f"Index build error: {e}", file=sys.stderr)
        return 1


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="wiki",
        description="Wikipedia Terminal - Offline Wikipedia reader",
        epilog="For more information, visit: https://github.com/rafaelchandane/wikipedia-terminal"
    )
    
    parser.add_argument(
        '--zim',
        type=str,
        help='Path to ZIM file (overrides ZIM_PATH environment variable)'
    )
    
    # Create subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Interactive mode (default)
    subparsers.add_parser(
        'interactive',
        aliases=['ui', 'i'],
        help='Launch interactive UI (default mode)'
    )
    
    # Search mode
    parser_search = subparsers.add_parser(
        'search',
        aliases=['s'],
        help='Search for articles and display results'
    )
    parser_search.add_argument('query', nargs='+', help='Search query')
    parser_search.add_argument(
        '--limit',
        type=int,
        default=20,
        help='Maximum number of results (default: 20)'
    )
    
    # Get mode
    parser_get = subparsers.add_parser(
        'get',
        aliases=['g'],
        help='Get and display a specific article by exact title'
    )
    parser_get.add_argument('title', nargs='+', help='Article title')
    
    # Quick mode
    parser_quick = subparsers.add_parser(
        'quick',
        aliases=['q'],
        help='Quick search - display first matching article'
    )
    parser_quick.add_argument('query', nargs='+', help='Search query')
    
    # Read mode (read article from last search by number)
    parser_read = subparsers.add_parser(
        'read',
        aliases=['r'],
        help='Read article from last search results by number'
    )
    parser_read.add_argument(
        'number',
        type=int,
        help='Article number from last search (e.g., 1, 2, 3...)'
    )
    
    # Build index mode
    parser_build = subparsers.add_parser(
        'build-index',
        aliases=['build', 'index'],
        help='Build FTS5 search index from ZIM file'
    )
    parser_build.add_argument(
        'zim',
        help='Path to ZIM file'
    )
    parser_build.add_argument(
        '-o', '--output',
        default='wikipedia_fts.db',
        help='Output database path (default: wikipedia_fts.db)'
    )
    parser_build.add_argument(
        '-b', '--batch',
        type=int,
        default=500,
        help='Batch insert size (default: 500)'
    )
    parser_build.add_argument(
        '--replace',
        action='store_true',
        help='Drop and recreate existing index'
    )
    
    args = parser.parse_args()
    
    # If no command specified, launch interactive mode
    if not args.command:
        return cmd_interactive(args)
    
    # Route to appropriate command handler
    commands = {
        'interactive': cmd_interactive,
        'ui': cmd_interactive,
        'i': cmd_interactive,
        'search': cmd_search,
        's': cmd_search,
        'get': cmd_get,
        'g': cmd_get,
        'quick': cmd_quick,
        'q': cmd_quick,
        'read': cmd_read,
        'r': cmd_read,
        'build-index': cmd_build_index,
        'build': cmd_build_index,
        'index': cmd_build_index,
    }
    
    handler = commands.get(args.command)
    if handler:
        try:
            sys.exit(handler(args))
        except KeyboardInterrupt:
            print("\nInterrupted by user", file=sys.stderr)
            sys.exit(130)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
