from fastapi import APIRouter, HTTPException, Depends
from careerforge.api.auth import get_current_user
from careerforge.api.models import (
    CVAnalyzeRequest, CVAnalyzeResponse,
    MatchRequest, MatchResponse,
    JobResult,
    ApplicationCreate, ApplicationRecord,
    RAGRequest, RAGResponse,
)
from careerforge.tools.tools import search_jobs_denmark, save_application, list_applications
from careerforge.rag.rag import answer_with_rag
from careerforge.pipeline.career_service import CareerService

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/cv/analyze", response_model=CVAnalyzeResponse)
def analyze_cv(req: CVAnalyzeRequest, current_user: str = Depends(get_current_user)):
    try:
        return CareerService().analyze_cv(req.cv_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/match", response_model=MatchResponse)
def match_cv(req: MatchRequest):
    try:
        return CareerService().match_cv(req.cv_text, req.job_description)
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
def get_applications(current_user: str = Depends(get_current_user)):   
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