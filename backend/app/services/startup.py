"""
Startup service to automatically load existing documents on application start.
"""
import logging
from pathlib import Path
from typing import Set
from app.core.config import settings
from app.core.database import get_collection
from app.services.rag import rag_service

logger = logging.getLogger(__name__)


def get_ingested_files() -> Set[str]:
    """Get list of files that have already been ingested into ChromaDB."""
    try:
        collection = get_collection()
        # Get all documents from collection to check metadata
        results = collection.get()
        
        ingested_files = set()
        if results and "metadatas" in results:
            for metadata in results["metadatas"]:
                if "source" in metadata:
                    ingested_files.add(metadata["source"])
        
        return ingested_files
    except Exception as e:
        logger.warning(f"Error getting ingested files: {e}")
        return set()


def load_existing_documents():
    """
    Scan the existing documents folder and automatically ingest any PDF/Excel files
    that haven't been processed yet.
    """
    docs_dir = Path(settings.EXISTING_DOCS_DIR)
    
    if not docs_dir.exists():
        logger.info(f"Documents directory does not exist: {docs_dir}. Creating it...")
        docs_dir.mkdir(parents=True, exist_ok=True)
        return
    
    # Get list of already ingested files
    ingested_files = get_ingested_files()
    logger.info(f"Found {len(ingested_files)} already ingested files in database")
    
    # Find all PDF and Excel files in the documents folder
    all_files = []
    for ext in settings.ALLOWED_EXTENSIONS:
        all_files.extend(docs_dir.glob(f"*{ext}"))
        all_files.extend(docs_dir.glob(f"*{ext.upper()}"))
    
    if not all_files:
        logger.info(f"No documents found in {docs_dir}")
        return
    
    logger.info(f"Found {len(all_files)} document(s) in {docs_dir}")
    
    # Filter out already ingested files
    files_to_ingest = [
        f for f in all_files 
        if f.name not in ingested_files
    ]
    
    if not files_to_ingest:
        logger.info("All documents have already been ingested")
        return
    
    logger.info(f"Processing {len(files_to_ingest)} new document(s)...")
    
    # Process each file
    success_count = 0
    error_count = 0
    
    for file_path in files_to_ingest:
        try:
            logger.info(f"Processing: {file_path.name}")
            result = rag_service.ingest_document(str(file_path))
            success_count += 1
            logger.info(
                f"✓ Successfully ingested {file_path.name} "
                f"({result['chunks_ingested']} chunks)"
            )
        except Exception as e:
            error_count += 1
            logger.error(f"✗ Error processing {file_path.name}: {str(e)}")
    
    logger.info(
        f"Startup document loading complete: "
        f"{success_count} succeeded, {error_count} failed"
    )
