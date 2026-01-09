from pydantic import BaseModel, EmailStr
from typing import Optional, List
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
class ChatQuery(BaseModel):
    query: str
    top_k: Optional[int] = 5


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
