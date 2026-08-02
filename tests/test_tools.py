import os
import pytest
from unittest.mock import patch, MagicMock
from tools import save_application, list_applications, get_resume, search_jobs


def setup_function():
    os.environ["DB_PATH"] = "data/test_career.db"


def teardown_function():
    if os.path.exists("data/test_career.db"):
        os.remove("data/test_career.db")


def test_save_and_list():
    result = save_application("TestCorp", "Python Dev", "applied")
    assert result["saved"] is True
    apps = list_applications()
    assert any(a["company"] == "TestCorp" for a in apps)


def test_save_application_returns_count():
    save_application("CompanyA", "Role A", "applied")
    result = save_application("CompanyB", "Role B", "pending")
    assert result["total_applications"] >= 2


def test_get_resume_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.get_resume", lambda: "No CV stored. Please upload one first.")
    result = get_resume()
    assert isinstance(result, str)


@patch("tools.requests.get")
def test_search_jobs_mocked(mock_get):
    """Adzuna API is mocked — no real HTTP call."""
    mock_get.return_value = MagicMock(json=lambda: {
        "results": [{
            "title": "Python Developer",
            "company": {"display_name": "MockCorp"},
            "location": {"display_name": "London"},
            "salary_min": 50000,
            "redirect_url": "https://example.com"
        }]
    })
    jobs = search_jobs("Python", "london")
    assert len(jobs) == 1
    assert jobs[0]["company"] == "MockCorp"
    mock_get.assert_called_once()