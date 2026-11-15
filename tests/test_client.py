from client import extract_json


def test_extract_clean_json():
    assert extract_json('{"score": 85}') == {"score": 85}


def test_extract_markdown_fenced():
    assert extract_json('```json\n{"score": 85}\n```') == {"score": 85}


def test_extract_with_prose():
    text = 'Here is the result:\n{"score": 85, "strengths": []}'
    result = extract_json(text)
    assert result["score"] == 85


def test_extract_nested_json():
    text = '{"score": 90, "strengths": ["Python", "FastAPI"], "gaps": []}'
    result = extract_json(text)
    assert result["strengths"] == ["Python", "FastAPI"]

def test_repair_handles_fenced_reply(mocker):
    fake = mocker.Mock()
    fake.content = [mocker.Mock(text='```json\n{"score": 70}\n```')]
    mocker.patch("client.client.messages.create", return_value=fake)
    assert extract_json("not json at all") == {"score": 70}    