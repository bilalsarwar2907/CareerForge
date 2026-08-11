from fastapi import APIRouter, HTTPException
from api.models import (
    CVAnalyzeRequest, CVAnalyzeResponse,
    MatchRequest, MatchResponse,
    JobResult,
    ApplicationCreate, ApplicationRecord,
    RAGRequest, RAGResponse,
)
from tools import search_jobs_denmark, save_application, list_applications
from rag import answer_with_rag
from prompts import MATCH_PROMPT_FINAL
from client import call_claude_json

router = APIRouter()


@router.post("/cv/analyze", response_model=CVAnalyzeResponse)
def analyze_cv(req: CVAnalyzeRequest):
    try:
        from prompts import CV_ANALYSIS_PROMPT
        from client import call_claude_json
        prompt = CV_ANALYSIS_PROMPT.format(cv_text=req.cv_text)
        result = call_claude_json(prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/match", response_model=MatchResponse)
def match_cv(req: MatchRequest):
    try:
        prompt = MATCH_PROMPT_FINAL.format(
            cv_text=req.cv_text,
            job_text=req.job_description
        )
        result = call_claude_json(prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/search", response_model=list[JobResult])
def search_jobs(keywords: str, location: str = "copenhagen", results: int = 5):
    try:
        return search_jobs_denmark(keywords, location, results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/applications", response_model=dict)
def create_application(req: ApplicationCreate):
    try:
        return save_application(req.company, req.role, req.status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/applications", response_model=list[ApplicationRecord])
def get_applications():
    try:
        return list_applications()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/ask", response_model=RAGResponse)
def rag_ask(req: RAGRequest):
    try:
        answer = answer_with_rag(req.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))