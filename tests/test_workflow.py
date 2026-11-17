import json
from unittest.mock import patch

from careerforge.services import workflow
from careerforge.infrastructure.tools import list_applications

FAKE_CV = {"name": "Test Person", "skills": ["Python", "SQL"]}
FAKE_MATCH = {"score": 70, "strengths": ["Python"], "gaps": ["Docker", "Kubernetes"]}
FAKE_JOB_INFO = {"company": "Coop", "role": "AI Engineer"}


def test_workflow_characterization(tmp_path, monkeypatch):
    # workflow writes "data/latest_report.json" (relative path) -> run inside tmp_path
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()

    with patch("careerforge.services.workflow.analyze_cv_pdf", return_value=FAKE_CV) as mock_pdf, \
         patch("careerforge.services.workflow.call_claude_json", side_effect=[FAKE_MATCH, FAKE_JOB_INFO]) as mock_json, \
         patch("careerforge.services.workflow.answer_with_rag", return_value="Take a course.") as mock_rag, \
         patch("careerforge.services.workflow.call_claude", return_value="Dear team...") as mock_letter:
        report = workflow.run_career_workflow("cv.pdf", "AI Engineer at Coop")


    # 1. Output shape
    assert set(report) == {"cv", "match_score", "strengths", "gaps", "gap_resources", "cover_letter"}
    assert report["match_score"] == 70
    assert report["gap_resources"] == {"Docker": "Take a course.", "Kubernetes": "Take a course."}
    assert report["cover_letter"] == "Dear team..."

    # 2. Calls
    mock_pdf.assert_called_once_with("cv.pdf")
    assert mock_json.call_count == 2      # match + job info
    assert mock_rag.call_count == 2       # one per gap
    mock_letter.assert_called_once()

    # 3. Saved to the (temp) DB
    apps = list_applications()
    assert apps[0]["company"] == "Coop"
    assert apps[0]["role"] == "AI Engineer"

    # 4. Report file written with same content
    saved = json.loads((tmp_path / "data" / "latest_report.json").read_text())
    assert saved == report