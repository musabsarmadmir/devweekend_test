import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

# Database path: can be overridden by EXPENSES_DB env var or via set_db_path()
DB_PATH = Path(os.getenv("EXPENSES_DB")) if os.getenv("EXPENSES_DB") else Path(__file__).resolve().parent.parent / "data" / "expenses.db"


def set_db_path(path: str) -> None:
    global DB_PATH
    DB_PATH = Path(path)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    init_db()


def _get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS expenses (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      amount REAL NOT NULL,
      note TEXT,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    )
    """
    )
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS expense_tags (
      expense_id INTEGER NOT NULL,
      tag TEXT NOT NULL,
      FOREIGN KEY(expense_id) REFERENCES expenses(id)
    )
    """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_expense_tags_tag ON expense_tags(tag)")
    conn.commit()
    conn.close()


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def add_expense(title: str, amount: float, tags: Optional[List[str]] = None, note: Optional[str] = None) -> int:
    tags = tags or []
    now = _now_iso()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO expenses (title, amount, note, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (title, amount, note, now, now),
    )
    eid = cur.lastrowid
    for t in tags:
        cur.execute("INSERT INTO expense_tags (expense_id, tag) VALUES (?, ?)", (eid, t))
    conn.commit()
    conn.close()
    return eid


def get_expense(expense_id: int) -> Optional[Dict[str, Any]]:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    cur.execute("SELECT tag FROM expense_tags WHERE expense_id = ?", (expense_id,))
    tags = [r[0] for r in cur.fetchall()]
    result = dict(row)
    result["tags"] = tags
    conn.close()
    return result


def list_expenses(q: Optional[str] = None, tag: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    conn = _get_conn()
    cur = conn.cursor()
    params: List[Any] = []
    where: List[str] = []
    if q:
        where.append("(e.title LIKE ? OR e.note LIKE ?)")
        like_q = f"%{q}%"
        params.extend([like_q, like_q])
    if tag:
        where.append("e.id IN (SELECT expense_id FROM expense_tags WHERE tag = ?)")
        params.append(tag)
    where_sql = "WHERE " + " AND ".join(where) if where else ""
    limit_sql = f"LIMIT {int(limit)}" if limit else ""
    sql = f"""
    SELECT e.id, e.title, e.amount, e.note, e.created_at, e.updated_at,
           GROUP_CONCAT(t.tag, ',') as tags
    FROM expenses e
    LEFT JOIN expense_tags t ON e.id = t.expense_id
    {where_sql}
    GROUP BY e.id
    ORDER BY e.created_at DESC
    {limit_sql}
    """
    cur.execute(sql, params)
    rows = cur.fetchall()
    results: List[Dict[str, Any]] = []
    for r in rows:
        tags = r["tags"].split(",") if r["tags"] else []
        results.append(
            {
                "id": r["id"],
                "title": r["title"],
                "amount": r["amount"],
                "note": r["note"],
                "tags": tags,
                "created_at": r["created_at"],
                "updated_at": r["updated_at"],
            }
        )
    conn.close()
    return results


def update_expense(expense_id: int, title: Optional[str] = None, amount: Optional[float] = None, tags: Optional[List[str]] = None, note: Optional[str] = None) -> bool:
    conn = _get_conn()
    cur = conn.cursor()
    fields: List[str] = []
    params: List[Any] = []
    if title is not None:
        fields.append("title = ?")
        params.append(title)
    if amount is not None:
        fields.append("amount = ?")
        params.append(amount)
    if note is not None:
        fields.append("note = ?")
        params.append(note)
    if fields:
        fields.append("updated_at = ?")
        params.append(_now_iso())
        params.append(expense_id)
        sql = f"UPDATE expenses SET {', '.join(fields)} WHERE id = ?"
        cur.execute(sql, params)
    if tags is not None:
        cur.execute("DELETE FROM expense_tags WHERE expense_id = ?", (expense_id,))
        for t in tags:
            cur.execute("INSERT INTO expense_tags (expense_id, tag) VALUES (?, ?)", (expense_id, t))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok


def delete_expense(expense_id: int) -> bool:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM expense_tags WHERE expense_id = ?", (expense_id,))
    cur.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok


# Ensure DB is initialized on import
init_db()
