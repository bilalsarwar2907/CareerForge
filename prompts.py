SYSTEM_PROMPT = """
You are a professional career advisor.
When asked to return JSON, return ONLY valid JSON — no prose, no markdown fences.
"""

CV_ANALYSIS_PROMPT = """
Analyze this CV and return a JSON object with exactly this structure:
{{
  "summary": "2-3 sentence professional summary",
  "skills": ["skill1", "skill2", "skill3"],
  "recommendations": ["recommendation1", "recommendation2"]
}}

CV:
{cv_text}
"""