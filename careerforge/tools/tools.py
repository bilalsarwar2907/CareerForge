import os
import json
from careerforge.config import DATA_DIR
from careerforge.tools.applications import save_application, list_applications
from careerforge.tools.job_providers import search_jobs, search_jobs_denmark


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