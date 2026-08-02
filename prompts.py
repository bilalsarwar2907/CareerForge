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
# Version A — Zero-shot
MATCH_PROMPT_V1 = """
Analyze this CV against this job description and return JSON only.
CV: {cv_text}
Job: {job_text}
Return: {{"score": 0-100, "strengths": [], "gaps": []}}
"""

# Version B — Few-shot
MATCH_PROMPT_V2 = """
Analyze CV-job fit. Examples:

CV: Senior Python dev, FastAPI, Docker | Job: Python backend dev
Output: {{"score": 88, "strengths": ["Python", "FastAPI", "Docker"], "gaps": ["No mention of tests"]}}

CV: Marketing manager, no tech skills | Job: React developer
Output: {{"score": 4, "strengths": [], "gaps": ["No React", "No JavaScript"]}}

Now analyze:
CV: {cv_text}
Job: {job_text}
Return JSON only: {{"score": 0-100, "strengths": [], "gaps": []}}
"""

# Version C — XML structure
MATCH_PROMPT_V3 = """
<task>Analyze fit between a CV and a job description.</task>
<instructions>
- Score 0-100 based on skill match
- List concrete strengths from CV matching job
- List concrete gaps where CV falls short
- Return JSON ONLY
</instructions>
<input>
<cv>{cv_text}</cv>
<job>{job_text}</job>
</input>
<format>{{"score": integer, "strengths": [strings], "gaps": [strings]}}</format>
"""

PROMPT_REGISTRY = {
    "cv_analysis_v1": CV_ANALYSIS_PROMPT,
    "match_v1": MATCH_PROMPT_V1,
    "match_v2": MATCH_PROMPT_V2,
    "match_v3": MATCH_PROMPT_V3,
}
MATCH_PROMPT_FINAL = MATCH_PROMPT_V1  # Winner: 90% accuracy on 20 test cases