import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import json
from fastmcp import FastMCP
from tools import search_jobs, search_jobs_denmark, save_application, get_resume, list_applications

mcp = FastMCP("CareerForge")


@mcp.tool()
def search_jobs_tool(keywords: str, location: str = "london") -> str:
    """Search real job listings from Adzuna."""
    return json.dumps(search_jobs(keywords, location))


@mcp.tool()
def search_jobs_denmark_tool(keywords: str, location: str = "copenhagen") -> str:
    """Search job listings in Denmark via JSearch."""
    return json.dumps(search_jobs_denmark(keywords, location))


@mcp.tool()
def save_application_tool(company: str, role: str, status: str) -> str:
    """Save a job application. Status must be: applied, pending, interview, or rejected."""
    return json.dumps(save_application(company, role, status))


@mcp.tool()
def get_resume_tool() -> str:
    """Retrieve the user's stored CV."""
    return get_resume()


@mcp.tool()
def list_applications_tool() -> str:
    """List all tracked job applications."""
    return json.dumps(list_applications())


@mcp.tool()
def ask_career_advisor(question: str) -> str:
    """Ask a career question. Answers come from the CareerForge knowledge base."""
    from rag import answer_with_rag
    return answer_with_rag(question)

@mcp.resource("career://applications")
def applications_resource() -> str:
    """All tracked job applications."""
    return json.dumps(list_applications(), indent=2)


if __name__ == "__main__":
    mcp.run()