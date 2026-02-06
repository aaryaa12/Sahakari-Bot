from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# User Schemas
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Chat Schemas
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatQuery(BaseModel):
    query: str
    top_k: Optional[int] = 5
    history: Optional[List[ChatMessage]] = None


class Citation(BaseModel):
    source: str
    page: str
    excerpt: str
    relevance_score: Optional[float] = None


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    sources_count: int


# Document Schemas
class DocumentInfo(BaseModel):
    filename: str
    size: int
    uploaded_at: float


class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]
    total: int


# Assessment Schemas
class AssessmentStartResponse(BaseModel):
    assessment_id: str
    question: str
    question_id: str
    section_title: str
    references: List[str]
    question_index: int
    total_questions: int
    instructions: str


class AssessmentAnswerRequest(BaseModel):
    assessment_id: str
    answer: str


class AssessmentAnswerResponse(BaseModel):
    completed: bool
    assessment_id: str
    question: Optional[str] = None
    question_id: Optional[str] = None
    section_title: Optional[str] = None
    references: Optional[List[str]] = None
    question_index: Optional[int] = None
    total_questions: Optional[int] = None
    total_score: Optional[int] = None
    max_score: Optional[int] = None
    score_percent: Optional[float] = None
    risk_level: Optional[str] = None
    section_scores: Optional[Dict[str, Dict[str, int]]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None


class AssessmentCancelResponse(BaseModel):
    cancelled: bool
    assessment_id: str


class AssessmentCancelRequest(BaseModel):
    assessment_id: str
