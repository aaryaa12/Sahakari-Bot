from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_current_user
from app.models.schemas import ChatQuery, ChatResponse, Citation
from app.services.rag import rag_service

router = APIRouter()


@router.post("/chat/query", response_model=ChatResponse)
async def chat_query(
    query: ChatQuery,
    current_user: dict = Depends(get_current_user)
):
    """Process a chat query using RAG."""
    if not query.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    
    try:
        result = rag_service.query(
            user_query=query.query,
            top_k=query.top_k or 5
        )
        
        # Convert citations to response model
        citations = [
            Citation(**citation) for citation in result["citations"]
        ]
        
        return ChatResponse(
            answer=result["answer"],
            citations=citations,
            sources_count=result["sources_count"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )
