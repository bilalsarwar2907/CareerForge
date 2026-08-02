from client import call_claude_json, call_claude
from prompts import SYSTEM_PROMPT, CV_ANALYSIS_PROMPT


def analyze_cv(cv_text: str) -> dict:
    prompt = CV_ANALYSIS_PROMPT.format(cv_text=cv_text)
    return call_claude_json(prompt, system=SYSTEM_PROMPT)


if __name__ == "__main__":
    cv = input("Paste CV text:\n")
    result = analyze_cv(cv)
    import json
    print(json.dumps(result, indent=2))