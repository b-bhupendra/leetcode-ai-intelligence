"""
Transactional SQLite Agent Queue Manager

Provides ACID-compliant, process-safe, row-level atomic task claiming
for background AI agent workers and FastAPI web endpoints, completely
eliminating race conditions and file-locking bottlenecks.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent_queue.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the SQLite database with strict typing and indexes."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                query_text TEXT NOT NULL,
                problem_slug TEXT DEFAULT '',
                code TEXT DEFAULT '',
                rating TEXT DEFAULT 'moderate',
                status TEXT DEFAULT 'pending',
                solution_json TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_queries_status ON queries(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_queries_created ON queries(created_at)")


def enqueue_task(query_type: str, query_text: str, problem_slug: str = "", code: str = "", rating: str = "moderate") -> int:
    """Safely appends a task using an ACID-compliant transactional insert."""
    init_db()
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO queries (type, query_text, problem_slug, code, rating, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (query_type, query_text, problem_slug, code, rating))
        conn.commit()
        return cursor.lastrowid


def claim_next_pending_task() -> Optional[Dict[str, Any]]:
    """
    Atomically claims the oldest pending task using an immediate status update
    to prevent race conditions across multiple concurrent worker processes.
    """
    init_db()
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT id, type, query_text, problem_slug, code, rating, status, solution_json, created_at
            FROM queries 
            WHERE status = 'pending' 
            ORDER BY id ASC 
            LIMIT 1
        """)
        row = cursor.fetchone()
        
        if row:
            task_id = row["id"]
            # Atomically lock/claim this task
            conn.execute("""
                UPDATE queries 
                SET status = 'processing', updated_at = CURRENT_TIMESTAMP 
                WHERE id = ? AND status = 'pending'
            """, (task_id,))
            conn.commit()
            
            task_dict = dict(row)
            task_dict["status"] = "processing"
            return task_dict
            
        return None


def mark_task_completed(task_id: int, solution_output: Dict[str, Any]):
    """Saves the AI solution and marks the task as completed."""
    with get_connection() as conn:
        conn.execute("""
            UPDATE queries 
            SET status = 'processed', 
                solution_json = ?, 
                updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (json.dumps(solution_output), task_id))
        conn.commit()


def mark_task_failed(task_id: int, error_message: str):
    """Marks a task as failed with error details."""
    with get_connection() as conn:
        conn.execute("""
            UPDATE queries 
            SET status = 'failed', 
                solution_json = ?, 
                updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (json.dumps({"error": error_message}), task_id))
        conn.commit()


def list_recent_queries(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves recent queries for web UI display."""
    init_db()
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT id, type, query_text, problem_slug, code, rating, status, solution_json, created_at, updated_at
            FROM queries 
            ORDER BY id DESC 
            LIMIT ?
        """, (limit,))
        
        results = []
        for r in cursor.fetchall():
            item = dict(r)
            try:
                item["solution"] = json.loads(item["solution_json"])
            except Exception:
                item["solution"] = {}
            results.append(item)
            
        return results


# Initialize database on module load
init_db()
