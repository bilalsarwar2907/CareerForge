import os
import json
import requests
from careerforge.config import ADZUNA_APP_ID, ADZUNA_APP_KEY, DATA_DIR
from careerforge.tools.applications import save_application, list_applications


def search_jobs(keywords: str, location: str = "london", results: int = 5) -> list:
    """Search UK jobs via Adzuna API (gb endpoint)."""
    url = "https://api.adzuna.com/v1/api/jobs/gb/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": keywords,
        "where": location,
        "results_per_page": results,
        "content-type": "application/json"
    }
    response = requests.get(url, params=params)
    data = response.json()
    return [
        {
            "title": job["title"],
            "company": job.get("company", {}).get("display_name", "Unknown"),
            "location": job.get("location", {}).get("display_name", location),
            "salary": job.get("salary_min", "Not specified"),
            "url": job.get("redirect_url", "")
        }
        for job in data.get("results", [])
    ]


def search_jobs_denmark(keywords: str, location: str = "copenhagen", results: int = 5) -> list:
    """Search remote tech jobs via Remotive (free, no auth). Danish job boards linked separately in UI."""
    url = "https://remotive.com/api/remote-jobs"
    params = {"search": keywords, "limit": results}
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        jobs = data.get("jobs", [])[:results]
        print(f"[Remotive] jobs_found={len(jobs)}")
        return [
            {
                "title": job.get("title", "Unknown"),
                "company": job.get("company_name", "Unknown"),
                "location": job.get("candidate_required_location", "Remote"),
                "salary": job.get("salary") or "Not specified",
                "url": job.get("url", "")
            }
            for job in jobs
        ]
    except Exception as e:
        print(f"[Remotive] Error: {e}")
        return []



def get_resume() -> str:
    """Return stored CV text."""
    try:
        with open(DATA_DIR / "cv.txt") as f:
            return f.read()
    except FileNotFoundError:
        return "No CV stored. Please upload one first."


# Tool schemas for Claude
TOOLS = [
    {
        "name": "search_jobs",
        "description": "Search UK job listings via Adzuna. Use only for jobs in the United Kingdom.",
        "input_schema": {
            "type": "object",
            "properties": {
                "keywords": {"type": "string", "description": "Job keywords e.g. Python backend"},
                "location": {"type": "string", "description": "UK city e.g. london, manchester", "default": "london"},
                "results": {"type": "integer", "description": "Number of results", "default": 5}
            },
            "required": ["keywords"]
        }
    },
    {
        "name": "save_application",
        "description": "Save a job application to the tracker.",
        "input_schema": {
            "type": "object",
            "properties": {
                "company": {"type": "string"},
                "role": {"type": "string"},
                "status": {"type": "string", "enum": ["applied", "pending", "interview", "rejected"]}
            },
            "required": ["company", "role", "status"]
        }
    },
    {
        "name": "search_jobs_denmark",
       "description": "Search remote tech jobs via Remotive (remote-only, not Danish job boards). Use when user wants remote jobs they can do from Denmark.",
        "input_schema": {
            "type": "object",
            "properties": {
                "keywords": {"type": "string", "description": "Job keywords e.g. Python developer"},
                "location": {"type": "string", "description": "Danish city e.g. copenhagen, aarhus", "default": "copenhagen"},
                "results": {"type": "integer", "description": "Number of results", "default": 5}
            },
            "required": ["keywords"]
        }
    },
    {
        "name": "get_resume",
        "description": "Retrieve the user's stored CV.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "list_applications",
        "description": "List all tracked job applications.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    }
]


def execute_tool(name: str, inputs: dict):
    dispatch = {
        "search_jobs": search_jobs,
        "search_jobs_denmark": search_jobs_denmark,
        "save_application": save_application,
        "get_resume": get_resume,
        "list_applications": list_applications,
    }
    if name not in dispatch:
        return {"error": f"Unknown tool: {name}"}
    return dispatch[name](**inputs)