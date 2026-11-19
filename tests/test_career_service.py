from unittest.mock import patch
from careerforge.pipeline.career_service import CareerService

FAKE_MATCH = {"score": 70, "strengths": ["Python"], "gaps": ["Docker"]}


@patch("careerforge.pipeline.career_service.call_claude_json", return_value=FAKE_MATCH)
def test_match_cv(mock_claude):
    result = CareerService().match_cv("my cv", "the job")

    assert result == FAKE_MATCH
    prompt = mock_claude.call_args[0][0]
    assert "my cv" in prompt and "the job" in prompt



@patch("careerforge.pipeline.career_service.call_claude_json", return_value={"skills": ["Python"]})
def test_analyze_cv(mock_claude):
    result = CareerService().analyze_cv("my cv")

    assert result == {"skills": ["Python"]}
    assert "my cv" in mock_claude.call_args[0][0]
    assert "system" in mock_claude.call_args.kwargs    