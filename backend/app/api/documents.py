from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import List
from app.api.dependencies import get_current_user
from app.services.rag import rag_service
from app.core.config import settings
from pathlib import Path
import os

router = APIRouter()


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
    
    # Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading file: {str(e)}"
        )
    
    # Check file size
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum of {settings.MAX_FILE_SIZE / (1024*1024):.0f}MB"
        )
    
    try:
        # Save file
        from app.services.documents import document_service
        file_path = document_service.save_file(file_content, file.filename)
        
        # Ingest into vector database
        result = rag_service.ingest_document(file_path)
        
        return {
            "status": "success",
            "message": "Document uploaded and processed successfully",
            "filename": file.filename,
            "chunks_processed": result["chunks_ingested"]
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
    """List all documents (both uploaded and existing)."""
    try:
        documents = []
        
        # Get files from uploads folder
        upload_dir = Path(settings.UPLOAD_DIR)
        if upload_dir.exists():
            for file_path in upload_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in settings.ALLOWED_EXTENSIONS:
                    documents.append({
                        "filename": file_path.name,
                        "size": file_path.stat().st_size,
                        "uploaded_at": file_path.stat().st_mtime,
                        "source": "uploaded"
                    })
        
        # Get files from existing documents folder
        existing_docs_dir = Path(settings.EXISTING_DOCS_DIR)
        if existing_docs_dir.exists():
            for file_path in existing_docs_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in settings.ALLOWED_EXTENSIONS:
                    documents.append({
                        "filename": file_path.name,
                        "size": file_path.stat().st_size,
                        "uploaded_at": file_path.stat().st_mtime,
                        "source": "existing"
                    })
        
        return {
            "documents": documents,
            "total": len(documents)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing documents: {str(e)}"
        )


@router.post("/documents/reload")
async def reload_documents(
    current_user: dict = Depends(get_current_user)
):
    """Manually reload existing documents from the documents folder."""
    try:
        from app.services.startup import load_existing_documents
        load_existing_documents()
        return {
            "status": "success",
            "message": "Documents reloaded successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reloading documents: {str(e)}"
        )


@router.get("/documents/status")
async def get_document_status(
    current_user: dict = Depends(get_current_user)
):
    """Get status of documents in the vector database."""
    try:
        from app.core.database import get_collection
        collection = get_collection()
        count = collection.count()
        
        # Get list of ingested files
        results = collection.get()
        ingested_files = set()
        if results and "metadatas" in results:
            for metadata in results["metadatas"]:
                if "source" in metadata:
                    ingested_files.add(metadata["source"])
        
        return {
            "total_chunks": count,
            "ingested_files": list(ingested_files),
            "files_count": len(ingested_files),
            "has_documents": count > 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting document status: {str(e)}"
        )
