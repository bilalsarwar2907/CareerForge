import os
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret")

import pytest
from careerforge.infrastructure import tools
import interfaces.api.auth


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Every test uses its own empty DB file, never data/career.db."""
    db = str(tmp_path / "test_career.db")
    monkeypatch.setattr(tools, "DB_PATH", db)
    monkeypatch.setattr(interfaces.api.auth, "DB_PATH", db)
    interfaces.api.auth.init_users_table()
    return db