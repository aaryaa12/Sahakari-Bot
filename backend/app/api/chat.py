from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from app.api.dependencies import get_current_user
from app.models.schemas import ChatQuery, ChatResponse, Citation
from app.services.rag import rag_service
import json
from typing import AsyncGenerator

router = APIRouter()


@router.post("/chat/query", response_model=ChatResponse)
async def chat_query(
    query: ChatQuery,
    current_user: dict = Depends(get_current_user)
):
    """Process a chat query using RAG (non-streaming)."""
    if not query.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    
    try:
        result = rag_service.query(
            user_query=query.query,
            top_k=query.top_k or 5,
            history=query.history
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


@router.post("/chat/query-stream")
async def chat_query_stream(
    query: ChatQuery,
    current_user: dict = Depends(get_current_user)
):
    """Process a chat query using RAG with streaming response."""
    if not query.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    
    async def generate() -> AsyncGenerator[str, None]:
        try:
            # Stream chunks from RAG service
            async for chunk in rag_service.query_stream(
                user_query=query.query,
                top_k=query.top_k or 5,
                history=query.history
            ):
                # Send as server-sent events format
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            error_chunk = {
                "type": "error",
                "content": f"Error: {str(e)}"
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
