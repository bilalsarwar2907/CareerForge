from unittest.mock import patch
from evaluate import evaluate_prompt
from prompts import MATCH_PROMPT_V1


@patch("evaluate.call_claude_json")
def test_evaluate_prompt_mocked(mock_call):
    """Claude API is mocked — no real API call."""
    mock_call.return_value = {"score": 85, "strengths": ["Python"], "gaps": []}
    tests = [{
        "id": 1,
        "cv": "Python developer",
        "job": "Python backend role",
        "expected_score_min": 70,
        "expected_score_max": 100
    }]
    result = evaluate_prompt(MATCH_PROMPT_V1, tests)
    assert result["valid_json_pct"] == 100
    assert result["score_accuracy_pct"] == 100
    mock_call.assert_called_once()


@patch("evaluate.call_claude_json")
def test_evaluate_prompt_out_of_range(mock_call):
    """Score outside expected range = 0% accuracy."""
    mock_call.return_value = {"score": 20, "strengths": [], "gaps": []}
    tests = [{
        "id": 1,
        "cv": "Python developer",
        "job": "Python backend role",
        "expected_score_min": 70,
        "expected_score_max": 100
    }]
    result = evaluate_prompt(MATCH_PROMPT_V1, tests)
    assert result["score_accuracy_pct"] == 0


@patch("evaluate.call_claude_json")
def test_evaluate_prompt_missing_fields(mock_call):
    """Missing fields = has_fields_pct 0%."""
    mock_call.return_value = {"score": 85}
    tests = [{
        "id": 1,
        "cv": "Python developer",
        "job": "Python backend role",
        "expected_score_min": 70,
        "expected_score_max": 100
    }]
    result = evaluate_prompt(MATCH_PROMPT_V1, tests)
    assert result["has_fields_pct"] == 0