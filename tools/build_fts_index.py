"""
Build SQLite FTS5 index from ZIM file.
Usage: python tools/build_fts_index.py --zim path/to/file.zim --db wiki_index.db --replace
"""
from typing import Iterator, Optional
import argparse
import sqlite3
import time
import sys
import os

# Add src to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from wikipedia_tui import zim_access
except ImportError as e:
    print(f"ERROR: Cannot import zim_access: {e}")
    print("Make sure you run this from the repository root:")
    print('  python tools\\build_fts_index.py --zim "path\\to\\file.zim" --db wiki_index.db')
    sys.exit(1)

def iter_titles(zim_path: Optional[str]) -> Iterator[str]:
    """Iterate all titles from ZIM file."""
    try:
        if hasattr(zim_access, "_open_zim"):
            handle = zim_access._open_zim(zim_path)
            if hasattr(handle, "titles") and handle.titles:
                yield from handle.titles
                return
            if hasattr(handle, "get_titles"):
                yield from handle.get_titles()
                return
            if hasattr(handle, "__iter__"):
                for entry in handle:
                    title = getattr(entry, "title", None) or getattr(entry, "name", None) or str(entry)
                    if title:
                        yield title
                return
    except Exception as e:
        print(f"Warning: Could not extract titles directly: {e}")
    
    # Fallback: prefix scan
    print("Falling back to prefix-based title extraction (slower)...")
    seen = set()
    prefixes = [chr(c) for c in range(ord("a"), ord("z")+1)] + [str(d) for d in range(10)]
    for p in prefixes:
        try:
            results = zim_access.search_zim(p, zim_path)
            for t in results:
                if t not in seen:
                    seen.add(t)
                    yield t
        except Exception:
            continue

def get_content_for_title(title: str, zim_path: Optional[str]) -> Optional[str]:
    """Get article content."""
    try:
        return zim_access.get_article_content(title, zim_path)
    except Exception:
        return None

def prepare_db(conn: sqlite3.Connection, replace: bool = False):
    """Create FTS5 table."""
    cur = conn.cursor()
    if replace:
        cur.execute("DROP TABLE IF EXISTS articles;")
    cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS articles USING fts5(
            title UNINDEXED,
            body,
            tokenize='porter'
        );
    """)
    conn.commit()

def build_index(zim_path: str, db_path: str, batch: int = 500, replace: bool = False):
    """Build FTS index from ZIM."""
    if not os.path.exists(zim_path):
        print(f"ERROR: ZIM file not found: {zim_path}")
        sys.exit(1)
    
    start_time = time.time()
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA temp_store = MEMORY;")
    prepare_db(conn, replace=replace)
    cur = conn.cursor()

    total = 0
    inserted = 0
    batch_rows = []

    print(f"Indexing ZIM file: {zim_path}")
    print(f"Output database: {db_path}")
    print("Starting indexing (this may take a while for large ZIMs)...\n")
    
    try:
        for title in iter_titles(zim_path):
            total += 1
            content = get_content_for_title(title, zim_path) or ""
            body = " ".join(content.split())
            batch_rows.append((title, body))
            
            if len(batch_rows) >= batch:
                cur.executemany("INSERT INTO articles(title, body) VALUES (?, ?);", batch_rows)
                conn.commit()
                inserted += len(batch_rows)
                print(f"Indexed {inserted} articles... (total seen: {total})", flush=True)
                batch_rows.clear()

        if batch_rows:
            cur.executemany("INSERT INTO articles(title, body) VALUES (?, ?);", batch_rows)
            conn.commit()
            inserted += len(batch_rows)

    except KeyboardInterrupt:
        print("\n\nIndexing interrupted by user.")
    finally:
        conn.commit()
        conn.close()

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"Done!")
    print(f"Titles seen: {total}")
    print(f"Articles inserted: {inserted}")
    print(f"Time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
    print(f"Database: {db_path}")
    print(f"{'='*60}")

def main(argv=None):
    p = argparse.ArgumentParser(
        description="Build FTS index from ZIM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools\\build_fts_index.py --zim "C:\\path\\to\\file.zim" --db wiki_index.db --replace
  python tools\\build_fts_index.py -z wiki.zim -d index.db -b 1000
        """
    )
    p.add_argument("--zim", "-z", required=True, help="Path to .zim file")
    p.add_argument("--db", "-d", default="wiki_index.db", help="Output DB path (default: wiki_index.db)")
    p.add_argument("--batch", "-b", type=int, default=500, help="Batch insert size (default: 500)")
    p.add_argument("--replace", action="store_true", help="Drop and recreate existing index")
    args = p.parse_args(argv)
    
    build_index(args.zim, args.db, batch=args.batch, replace=args.replace)

if __name__ == "__main__":
    main()