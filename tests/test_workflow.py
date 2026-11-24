import json
from unittest.mock import patch

from careerforge.pipeline import workflow
from careerforge.tools.tools import list_applications

FAKE_CV = {"name": "Test Person", "skills": ["Python", "SQL"]}
FAKE_MATCH = {"score": 70, "strengths": ["Python"], "gaps": ["Docker", "Kubernetes"]}
FAKE_JOB_INFO = {"company": "Coop", "role": "AI Engineer"}


def test_workflow_characterization(tmp_path, monkeypatch):
    # workflow writes DATA_DIR / "latest_report.json" -> point DATA_DIR at tmp_path
    monkeypatch.setattr(workflow, "DATA_DIR", tmp_path / "data")
    (tmp_path / "data").mkdir()

    with patch("careerforge.pipeline.workflow.analyze_cv_pdf", return_value=FAKE_CV) as mock_pdf, \
         patch("careerforge.pipeline.career_service.call_claude_json", return_value=FAKE_MATCH) as mock_match, \
         patch("careerforge.pipeline.workflow.call_claude_json", return_value=FAKE_JOB_INFO) as mock_json, \
         patch("careerforge.pipeline.workflow.answer_with_rag", return_value="Take a course.") as mock_rag, \
         patch("careerforge.pipeline.workflow.call_claude", return_value="Dear team...") as mock_letter:
        report = workflow.run_career_workflow("cv.pdf", "AI Engineer at Coop")


    # 1. Output shape
    assert set(report) == {"cv", "match_score", "strengths", "gaps", "gap_resources", "cover_letter"}
    assert report["match_score"] == 70
    assert report["gap_resources"] == {"Docker": "Take a course.", "Kubernetes": "Take a course."}
    assert report["cover_letter"] == "Dear team..."

    # 2. Calls
    mock_pdf.assert_called_once_with("cv.pdf")
    mock_match.assert_called_once()       # match (via CareerService)
    mock_json.assert_called_once()        # job info      
    assert mock_rag.call_count == 2       # one per gap
    mock_letter.assert_called_once()

    # 3. Saved to the (temp) DB
    apps = list_applications()
    assert apps[0]["company"] == "Coop"
    assert apps[0]["role"] == "AI Engineer"

    # 4. Report file written with same content
    saved = json.loads((tmp_path / "data" / "latest_report.json").read_text())
    assert saved == report