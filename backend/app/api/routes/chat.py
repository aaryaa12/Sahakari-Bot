from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.api.dependencies import get_current_user
from app.services.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()


class ChatQuery(BaseModel):
    query: str
    top_k: Optional[int] = 5


class Citation(BaseModel):
    source: str
    page: str
    type: str
    excerpt: str
    relevance_score: Optional[float] = None


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    context_used: int


@router.post("/chat/query", response_model=ChatResponse)
async def chat_query(
    chat_query: ChatQuery,
    current_user: dict = Depends(get_current_user)
):
    """Process a chat query using RAG."""
    try:
        result = rag_service.query(
            user_query=chat_query.query,
            top_k=chat_query.top_k
        )
        
        # Convert citations to response model
        citations = [
            Citation(**citation) for citation in result["citations"]
        ]
        
        return ChatResponse(
            answer=result["answer"],
            citations=citations,
            context_used=result["context_used"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )
