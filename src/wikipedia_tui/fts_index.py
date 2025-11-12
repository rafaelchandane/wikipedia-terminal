"""
Full-Text Search (FTS) index for Wikipedia Terminal.
Provides fast search across article content using SQLite FTS5.
"""
import os
import sqlite3
from typing import List, Dict, Optional


def search_fts(query: str, db_path: Optional[str] = None, limit: int = 10000) -> List[Dict[str, any]]:
    """
    Search FTS index for articles matching query.
    
    Args:
        query: Search query string
        db_path: Optional path to FTS database file
        limit: Maximum number of results (default: 10000)
        
    Returns:
        List of dicts with 'title' and 'rowid' keys
        
    Raises:
        RuntimeError: If FTS database cannot be accessed
    """
    if not db_path:
        db_path = os.environ.get("FTS_DB_PATH", "wikipedia_fts.db")
    
    if not os.path.exists(db_path):
        return []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Search using FTS5
        cursor.execute(
            "SELECT rowid, title FROM articles_fts WHERE articles_fts MATCH ? LIMIT ?",
            (query, limit)
        )
        
        results = [{"rowid": row[0], "title": row[1]} for row in cursor.fetchall()]
        conn.close()
        
        return results
    except Exception as e:
        raise RuntimeError(f"FTS search failed: {e}") from e


def get_body(rowid: int, db_path: Optional[str] = None) -> Optional[str]:
    """
    Retrieve article body by rowid.
    
    Args:
        rowid: FTS database row ID
        db_path: Optional path to FTS database file
        
    Returns:
        Article body text, or None if not found
        
    Raises:
        RuntimeError: If FTS database cannot be accessed
    """
    if not db_path:
        db_path = os.environ.get("FTS_DB_PATH", "wikipedia_fts.db")
    
    if not os.path.exists(db_path):
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT body FROM articles_fts WHERE rowid = ?", (rowid,))
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve article body: {e}") from e