import sqlite3
from datetime import datetime
from careerforge.config import DB_PATH


def save_application(company: str, role: str, status: str) -> dict:
    """Save application to SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT, role TEXT, status TEXT, created_at TEXT
        )
    """)
    conn.execute(
        "INSERT INTO applications (company, role, status, created_at) VALUES (?, ?, ?, ?)",
        (company, role, status, datetime.now().isoformat())
    )
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    conn.close()
    return {"saved": True, "total_applications": count}


def list_applications() -> list:
    """List all tracked applications from SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT, role TEXT, status TEXT, created_at TEXT
        )
    """)
    rows = conn.execute(
        "SELECT company, role, status, created_at FROM applications ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [{"company": r[0], "role": r[1], "status": r[2], "date": r[3]} for r in rows]