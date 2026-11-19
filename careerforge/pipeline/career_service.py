from careerforge.llm.client import call_claude_json
from careerforge.llm.prompts import MATCH_PROMPT_FINAL, CV_ANALYSIS_PROMPT, SYSTEM_PROMPT


class CareerService:
    """Facade: one front door for career features."""

    def match_cv(self, cv_text: str, job_text: str) -> dict:
        prompt = MATCH_PROMPT_FINAL.format(cv_text=cv_text, job_text=job_text)
        return call_claude_json(prompt)

    
    def analyze_cv(self, cv_text: str) -> dict:
        prompt = CV_ANALYSIS_PROMPT.format(cv_text=cv_text)
        return call_claude_json(prompt, system=SYSTEM_PROMPT)