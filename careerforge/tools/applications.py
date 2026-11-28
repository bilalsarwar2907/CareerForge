import sqlite3
from datetime import datetime
from careerforge.config import DB_PATH


class ApplicationRepository:
    """All SQLite access for the job application tracker."""

    def __init__(self, db_path=None):
        self.db_path = db_path

    def _connect(self):
        """Open the DB and make sure the table exists."""
        conn = sqlite3.connect(self.db_path or DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT, role TEXT, status TEXT, created_at TEXT
            )
        """)
        return conn

    def save(self, company: str, role: str, status: str) -> dict:
        """Save one application and return the new total."""
        conn = self._connect()
        conn.execute(
            "INSERT INTO applications (company, role, status, created_at) VALUES (?, ?, ?, ?)",
            (company, role, status, datetime.now().isoformat())
        )
        conn.commit()
        count = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        conn.close()
        return {"saved": True, "total_applications": count}

    def list_all(self) -> list:
        """List all applications, newest first."""
        conn = self._connect()
        rows = conn.execute(
            "SELECT company, role, status, created_at FROM applications ORDER BY created_at DESC"
        ).fetchall()
        conn.close()
        return [{"company": r[0], "role": r[1], "status": r[2], "date": r[3]} for r in rows]


_default = ApplicationRepository()


def save_application(company: str, role: str, status: str) -> dict:
    """Save application to SQLite."""
    return _default.save(company, role, status)


def list_applications() -> list:
    """List all tracked applications from SQLite."""
    return _default.list_all()