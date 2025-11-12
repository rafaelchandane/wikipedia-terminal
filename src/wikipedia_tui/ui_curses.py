"""
Terminal UI for Wikipedia Terminal.
Interactive search and article viewing with Fallout-style green theme.
"""
from typing import List, Optional
import os
import sys
import textwrap
import html as _html_lib
import warnings

# Suppress zimply's pkg_resources deprecation warning
warnings.filterwarnings("ignore", message=".*pkg_resources.*")

# Minimal curses stub for Windows compatibility
try:
    import curses  # type: ignore
except Exception:
    class _CursesStub:
        A_BOLD = 1
        A_REVERSE = 2
        KEY_UP = -1
        KEY_DOWN = -2
        KEY_LEFT = -3
        KEY_RIGHT = -4
        def initscr(self): return None
        def cbreak(self): pass
        def nocbreak(self): pass
        def echo(self): pass
        def noecho(self): pass
        def endwin(self): pass
    curses = _CursesStub()

from prompt_toolkit import PromptSession, print_formatted_text, HTML
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import clear as ptk_clear
from prompt_toolkit.styles import Style

# Import backend modules
try:
    from . import zim_access
    from . import fts_index
except ImportError:
    import zim_access  # type: ignore
    try:
        import fts_index  # type: ignore
    except ImportError:
        fts_index = None

# Fallout-style green color scheme
FALLOUT_STYLE = Style.from_dict({
    '': '#00ff00',  # Bright green text
    'prompt': '#00ff00 bold',
    'title': '#00ff00 bold',
    'status': '#00cc00',  # Slightly darker green
    'error': '#ff0000',  # Red for errors
})


def _escape_html(text: str) -> str:
    """Escape HTML special characters for safe display."""
    return _html_lib.escape(text)


def get_user_input(session: PromptSession, prompt_text: str) -> str:
    """
    Get user input with fallback for different Python versions.
    
    Args:
        session: PromptSession instance
        prompt_text: Prompt to display
        
    Returns:
        User input string
        
    Raises:
        KeyboardInterrupt: If user presses Ctrl+C
        EOFError: If user presses Ctrl+D
    """
    force_simple = os.environ.get("USE_SIMPLE_INPUT") == "1" or sys.version_info >= (3, 14)
    if force_simple:
        return input(prompt_text)
    
    try:
        with patch_stdout():
            return session.prompt(prompt_text, style=FALLOUT_STYLE)
    except Exception:
        return input(prompt_text)


def clear_terminal():
    """Clear terminal screen (cross-platform)."""
    os.system('cls' if os.name == 'nt' else 'clear')


def _view_article(article_text: str, session: PromptSession):
    """
    Display article content with pagination.
    
    Args:
        article_text: Article content to display
        session: PromptSession instance for user input
    """
    if not article_text:
        article_text = "<no content>"
    
    # Wrap text to 80 columns
    lines: List[str] = []
    for paragraph in str(article_text).splitlines():
        wrapped = textwrap.wrap(paragraph, width=80)
        if wrapped:
            lines.extend(wrapped)
        else:
            lines.append("")  # Preserve empty lines
    
    # Pagination settings
    per_page = 20
    page = 0
    total_pages = max(1, (len(lines) + per_page - 1) // per_page)

    while True:
        with patch_stdout():
            ptk_clear()
            start = page * per_page
            end = start + per_page
            
            page_lines = lines[start:end]
            
            # Display page content
            for ln in page_lines:
                print_formatted_text(
                    HTML(f"<ansigreen>{_escape_html(ln)}</ansigreen>"), 
                    style=FALLOUT_STYLE
                )
            
            # Display navigation footer
            print_formatted_text(
                HTML(f"\n<b><ansibrightgreen>Page {page+1}/{total_pages}</ansibrightgreen></b> — n/p nav, b back, q quit"), 
                style=FALLOUT_STYLE
            )

        try:
            cmd = get_user_input(session, "> ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            return

        if cmd in ("b", ""):
            return
        elif cmd == "n" and page + 1 < total_pages:
            page += 1
        elif cmd == "p" and page > 0:
            page -= 1
        elif cmd == "q":
            sys.exit(0)


def run_prompt_ui(zim_path: Optional[str] = None):
    """
    Main interactive UI loop.
    
    Provides search interface and article viewing with pagination.
    Uses FTS index if available, falls back to direct ZIM search.
    
    Args:
        zim_path: Optional path to ZIM file
    """
    session = PromptSession()
    status = "Type a query and press Enter. q to quit."
    articles: List[str] = []
    fts_results = None  # Cache for FTS results

    while True:
        try:
            clear_terminal()
            print_formatted_text(
                HTML("<b><ansibrightgreen>WIKIPEDIA TERMINAL</ansibrightgreen></b>"), 
                style=FALLOUT_STYLE
            )
            print_formatted_text(
                HTML(f"<ansigreen>{_escape_html(status)}</ansigreen>\n"), 
                style=FALLOUT_STYLE
            )

            # Display search results
            if articles:
                for i, a in enumerate(articles):
                    # Show first 70 chars of title
                    title = a[:70] if len(a) <= 70 else a[:67] + "..."
                    escaped_title = _escape_html(title)
                    print_formatted_text(
                        HTML(f"<ansigreen>{i+1}. {escaped_title}</ansigreen>"), 
                        style=FALLOUT_STYLE
                    )
                print()

            # Choose prompt based on state
            prompt_text = "Open # / new query / q > " if articles else "Query> "

            try:
                user_input = get_user_input(session, prompt_text).strip()
            except (KeyboardInterrupt, EOFError):
                break

            # Handle empty input
            if not user_input:
                if articles:
                    articles = []
                    fts_results = None
                    status = "Type a query and press Enter. q to quit."
                else:
                    status = "Empty query — try again or q to quit."
                continue
            
            # Handle quit command
            if user_input.lower() == "q":
                break

            # Handle article selection (numeric input when results are displayed)
            if articles and user_input.isdigit():
                idx = int(user_input) - 1
                if 0 <= idx < len(articles):
                    content = None
                    
                    # Try FTS index first (faster if available)
                    if fts_results is not None and fts_index is not None:
                        try:
                            content = fts_index.get_body(fts_results[idx]["rowid"])
                        except Exception:
                            pass
                    
                    # Fall back to ZIM file access
                    if not content:
                        try:
                            content = zim_access.get_article_content(articles[idx], zim_path)
                        except FileNotFoundError as e:
                            status = f"Error: {e}"
                            continue
                        except Exception as e:
                            status = f"Failed to load article: {e}"
                            continue
                    
                    # Display article
                    _view_article(content if content else articles[idx], session)
                    continue
                else:
                    status = f"Invalid number. Enter 1-{len(articles)} or new query."
                    continue

            # Treat input as new search query
            query = user_input
            
            # Try FTS search first (fast path)
            fts_results = None
            articles = []
            
            if fts_index is not None:
                try:
                    fts_results = fts_index.search_fts(query)
                    if fts_results:
                        articles = [r["title"] for r in fts_results]
                        status = f"Found {len(articles)} result(s) (FTS). Enter number to open."
                except Exception:
                    pass

            # Fall back to ZIM search if FTS not available or failed
            if not articles:
                status = "Searching ZIM..."
                clear_terminal()
                print_formatted_text(
                    HTML("<ansibrightgreen>Searching ZIM...</ansibrightgreen>"), 
                    style=FALLOUT_STYLE
                )
                
                try:
                    articles = zim_access.search_zim(query, zim_path)
                    fts_results = None  # Clear FTS cache
                except FileNotFoundError as e:
                    status = f"ZIM file not found: {e}"
                    articles = []
                    continue
                except Exception as e:
                    status = f"Search error: {e}"
                    articles = []
                    continue

            # Update status based on results
            if not articles:
                status = "No results found."
            else:
                status = f"Found {len(articles)} result(s). Enter number to open, or new query."

        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            status = f"Unexpected error: {e}"
            articles = []


def main():
    """Entry point for the Wikipedia Terminal application."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Wikipedia Terminal - Offline Wikipedia reader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use environment variable
  export ZIM_PATH=/path/to/wikipedia.zim
  python -m src.wikipedia_tui.ui_curses
  
  # Or pass path directly
  python -m src.wikipedia_tui.ui_curses --zim /path/to/wikipedia.zim
        """
    )
    parser.add_argument(
        '--zim', 
        type=str, 
        help='Path to ZIM file (overrides ZIM_PATH environment variable)'
    )
    
    args = parser.parse_args()
    
    # Get ZIM path from argument or environment
    zim_path = args.zim or os.environ.get("ZIM_PATH", "")
    
    # Try common default locations if not specified
    if not zim_path:
        common_paths = [
            os.path.expanduser("~/wikipedia.zim"),
            os.path.expanduser("~/Downloads/wikipedia.zim"),
            "./wikipedia.zim",
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                zim_path = path
                print(f"Found ZIM file at: {zim_path}")
                break
    
    if not zim_path or not os.path.exists(zim_path):
        print("Error: No ZIM file found.")
        print("\nPlease specify ZIM file location using one of these methods:")
        print("  1. Set environment variable: export ZIM_PATH=/path/to/wikipedia.zim")
        print("  2. Pass as argument: python -m src.wikipedia_tui.ui_curses --zim /path/to/wikipedia.zim")
        print("  3. Place wikipedia.zim in current directory or ~/Downloads")
        print("\nDownload ZIM files from: https://wiki.kiwix.org/wiki/Content_in_all_languages")
        sys.exit(1)
    
    try:
        run_prompt_ui(zim_path)
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    finally:
        # Clean up ZIM file handles
        zim_access.close_all()


if __name__ == "__main__":
    main()