import pytest
from unittest.mock import patch, MagicMock
from careerforge.tools.tools import save_application, list_applications, get_resume, search_jobs


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
    """No cv.txt in DATA_DIR -> friendly message."""
    monkeypatch.setattr("careerforge.tools.tools.DATA_DIR", tmp_path)
    assert get_resume() == "No CV stored. Please upload one first."


def test_get_resume_present(tmp_path, monkeypatch):
    """cv.txt in DATA_DIR -> its text is returned."""
    (tmp_path / "cv.txt").write_text("My CV text")
    monkeypatch.setattr("careerforge.tools.tools.DATA_DIR", tmp_path)
    assert get_resume() == "My CV text"


@patch("careerforge.tools.tools.requests.get")
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