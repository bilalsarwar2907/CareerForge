import json
from careerforge.infrastructure.pdf_handler import analyze_cv_pdf
from careerforge.infrastructure.rag.rag import index_document, answer_with_rag
from careerforge.infrastructure.tools import save_application
from careerforge.prompts import MATCH_PROMPT_FINAL, JOB_INFO_PROMPT
from careerforge.core.client import call_claude_json, call_claude



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
        resources = answer_with_rag(f"How to learn or demonstrate {gap}?")
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
    job_info = call_claude_json(JOB_INFO_PROMPT.format(job_text=job_description))
    company = job_info.get("company", "Unknown")
    role = job_info.get("role", "Unknown")
    save_application(company=company, role=role, status="applied")
    print(f"  Saved: {role} at {company}")

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
    # Replace with your actual CV PDF path in data/pdfs/
    CV_PATH = "data/pdfs/cv.pdf"
    job = """..."""
    run_career_workflow(CV_PATH, job)