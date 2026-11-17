from pydantic import BaseModel
from typing import Optional


# --- CV ---
class CVAnalyzeRequest(BaseModel):
    cv_text: str


class CVAnalyzeResponse(BaseModel):
    name: Optional[str] = None
    skills: list[str] = []
    experience: list[str] = []
    education: list[str] = []


# --- Match ---
class MatchRequest(BaseModel):
    cv_text: str
    job_description: str


class MatchResponse(BaseModel):
    score: int
    strengths: list[str] = []
    gaps: list[str] = []


# --- Jobs ---
class JobResult(BaseModel):
    title: str
    company: str
    location: str
    salary: str | int
    url: str


# --- Applications ---
class ApplicationCreate(BaseModel):
    company: str
    role: str
    status: str  # applied | pending | interview | rejected


class ApplicationRecord(BaseModel):
    company: str
    role: str
    status: str
    date: str


# --- RAG ---
class RAGRequest(BaseModel):
    question: str


class RAGResponse(BaseModel):
    answer: str


# --- Auth ---
class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"