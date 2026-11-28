from abc import ABC, abstractmethod
import requests
from careerforge.config import ADZUNA_APP_ID, ADZUNA_APP_KEY


class JobProvider(ABC):
    """Contract: every job source must have search()."""

    @abstractmethod
    def search(self, keywords: str, location: str, results: int) -> list:
        ...


class AdzunaProvider(JobProvider):
    """UK jobs via Adzuna API (gb endpoint)."""

    def search(self, keywords: str, location: str = "london", results: int = 5) -> list:
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


class RemotiveProvider(JobProvider):
    """Remote tech jobs via Remotive (free, no auth)."""

    def search(self, keywords: str, location: str = "copenhagen", results: int = 5) -> list:
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


def search_jobs(keywords: str, location: str = "london", results: int = 5) -> list:
    """Search UK jobs via Adzuna API (gb endpoint)."""
    return AdzunaProvider().search(keywords, location, results)


def search_jobs_denmark(keywords: str, location: str = "copenhagen", results: int = 5) -> list:
    """Search remote tech jobs via Remotive (free, no auth). Danish job boards linked separately in UI."""
    return RemotiveProvider().search(keywords, location, results)