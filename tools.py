import os
import json
import sqlite3
import requests
from datetime import datetime
from config import ADZUNA_APP_ID, ADZUNA_APP_KEY, DB_PATH


def search_jobs(keywords: str, location: str = "denmark", results: int = 5) -> list:
    """Search real jobs via Adzuna API."""
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


def save_application(company: str, role: str, status: str) -> dict:
    """Save application to SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT, role TEXT, status TEXT, created_at TEXT
        )
    """)
    conn.execute(
        "INSERT INTO applications (company, role, status, created_at) VALUES (?, ?, ?, ?)",
        (company, role, status, datetime.now().isoformat())
    )
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    conn.close()
    return {"saved": True, "total_applications": count}


def get_resume() -> str:
    """Return stored CV text."""
    try:
        with open("data/cv.txt") as f:
            return f.read()
    except FileNotFoundError:
        return "No CV stored. Please upload one first."


def list_applications() -> list:
    """List all tracked applications from SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT, role TEXT, status TEXT, created_at TEXT
        )
    """)
    rows = conn.execute(
        "SELECT company, role, status, created_at FROM applications ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [{"company": r[0], "role": r[1], "status": r[2], "date": r[3]} for r in rows]


# Tool schemas for Claude
TOOLS = [
    {
        "name": "search_jobs",
        "description": "Search real job listings. Use when user wants to find jobs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "keywords": {"type": "string", "description": "Job keywords e.g. Python backend"},
                "location": {"type": "string", "description": "Country or city", "default": "denmark"},
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
        "description": "Search job listings in Denmark via Jobnet.dk. Use when user wants to find jobs in Denmark or Copenhagen.",
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