import json
from anthropic import Anthropic
from config import ANTHROPIC_API_KEY
from pdf_handler import analyze_cv_pdf
from rag import index_document, answer_with_rag
from tools import save_application
from prompts import MATCH_PROMPT_FINAL
from client import call_claude_json, call_claude

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def run_career_workflow(cv_path: str, job_description: str) -> dict:

    print("\n[1/6] Extracting CV from PDF...")
    cv_data = analyze_cv_pdf(cv_path)
    print(f"  Found: {cv_data.get('name')}, skills: {cv_data.get('skills', [])[:3]}")

    print("\n[2/6] Scoring job match...")
    prompt = MATCH_PROMPT_FINAL.format(
        cv_text=json.dumps(cv_data),
        job_text=job_description
    )
    match = call_claude_json(prompt)
    print(f"  Score: {match.get('score')} | Gaps: {match.get('gaps', [])}")

    print("\n[3/6] Finding resources for skill gaps...")
    gap_resources = {}
    for gap in match.get("gaps", [])[:3]:
        resources = answer_with_rag(f"How to learn or demonstrate {gap}?", client)
        gap_resources[gap] = resources[:300]
        print(f"  {gap}: found resources")

    print("\n[4/6] Generating cover letter...")
    cover_prompt = f"""Write a professional cover letter (3 paragraphs).
Candidate: {json.dumps(cv_data)}
Job: {job_description}
Strengths to emphasize: {match.get('strengths', [])}
Keep it under 300 words."""
    cover_letter = call_claude(cover_prompt, stream=True)

    print("\n[5/6] Saving application...")
    save_application(
        company="Extracted from JD",
        role="Applied Role",
        status="applied"
    )

    print("\n[6/6] Saving report...")
    report = {
        "cv": cv_data,
        "match_score": match.get("score"),
        "strengths": match.get("strengths", []),
        "gaps": match.get("gaps", []),
        "gap_resources": gap_resources,
        "cover_letter": cover_letter
    }
    with open("data/latest_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Complete. Score: {match.get('score')}. Report saved.")
    return report


if __name__ == "__main__":
    job = """
    We are looking for a Senior Python Developer with experience in FastAPI,
    PostgreSQL, and Docker. The candidate should have 3+ years of experience
    building REST APIs and be comfortable with CI/CD pipelines.
    """
    run_career_workflow("data/pdfs/Dubai Brochure.pdf", job)