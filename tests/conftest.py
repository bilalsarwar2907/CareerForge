import os
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret")

import pytest
import tools
import api.auth


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Every test uses its own empty DB file, never data/career.db."""
    db = str(tmp_path / "test_career.db")
    monkeypatch.setattr(tools, "DB_PATH", db)
    monkeypatch.setattr(api.auth, "DB_PATH", db)
    api.auth.init_users_table()
    return db