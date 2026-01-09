from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import List
from app.api.dependencies import get_current_user
from app.services.document_service import DocumentService
from app.services.rag_service import RAGService
from app.core.config import settings
from pathlib import Path
import os

router = APIRouter()
document_service = DocumentService()
rag_service = RAGService()


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload and process a document (PDF or Excel)."""
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    try:
        # Save file
        file_path = document_service.save_uploaded_file(file_content, file.filename)
        
        # Ingest into vector database
        result = rag_service.ingest_document(file_path)
        
        return {
            "status": "success",
            "message": "Document uploaded and processed successfully",
            "filename": file.filename,
            "chunks_ingested": result["chunks_ingested"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )


@router.get("/documents/list")
async def list_documents(
    current_user: dict = Depends(get_current_user)
):
    """List all uploaded documents."""
    try:
        upload_dir = Path(settings.UPLOAD_DIR)
        documents = []
        
        if upload_dir.exists():
            for file_path in upload_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in settings.ALLOWED_EXTENSIONS:
                    documents.append({
                        "filename": file_path.name,
                        "size": file_path.stat().st_size,
                        "uploaded_at": file_path.stat().st_mtime
                    })
        
        return {
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing documents: {str(e)}"
        )
