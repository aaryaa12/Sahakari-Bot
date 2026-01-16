from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.database import get_collection
from pathlib import Path

router = APIRouter()


@router.get("/documents/list")
async def list_documents(
    current_user: dict = Depends(get_current_user)
):
    """List all documents from the documents folder."""
    try:
        documents = []
        
        # Get files from documents folder
        docs_dir = Path(settings.DOCUMENTS_DIR)
        if docs_dir.exists():
            for file_path in docs_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in settings.ALLOWED_EXTENSIONS:
                    documents.append({
                        "filename": file_path.name,
                        "size": file_path.stat().st_size,
                        "uploaded_at": file_path.stat().st_mtime
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
    force: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """
    Manually reload documents from the data/documents folder.
    
    Args:
        force: If True, reprocess all documents. If False, only process new/modified documents.
    """
    try:
        from app.services.startup import load_existing_documents
        load_existing_documents(force_reload=force)
        
        collection = get_collection()
        count = collection.count()
        
        return {
            "status": "success",
            "message": "Documents reloaded successfully",
            "total_chunks": count,
            "force_reload": force
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
    """Get status of documents in the vector database and folder."""
    try:
        collection = get_collection()
        count = collection.count()
        
        # Get list of ingested files
        results = collection.get()
        ingested_files = set()
        if results and "metadatas" in results:
            for metadata in results["metadatas"]:
                if "source" in metadata:
                    ingested_files.add(metadata["source"])
        
        # Also check folder for files
        docs_dir = Path(settings.DOCUMENTS_DIR)
        folder_files = []
        folder_count = 0
        if docs_dir.exists():
            for file_path in docs_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in settings.ALLOWED_EXTENSIONS:
                    folder_files.append(file_path.name)
                    folder_count += 1
        else:
            # Log if directory doesn't exist for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Documents directory does not exist: {docs_dir}")
        
        return {
            "total_chunks": count,
            "ingested_files": list(ingested_files),
            "files_count": len(ingested_files),
            "has_documents": count > 0,
            "folder_files": folder_files,
            "folder_count": folder_count,
            "needs_processing": folder_count > 0 and len(ingested_files) == 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting document status: {str(e)}"
        )
