"""
Startup service to automatically load existing documents on application start.
"""
import logging
from pathlib import Path
from typing import Set, Dict, Tuple
from app.core.config import settings
from app.core.database import get_collection
from app.services.rag import rag_service
import hashlib

logger = logging.getLogger(__name__)


def get_file_hash(file_path: Path) -> str:
    """Calculate MD5 hash of file for change detection."""
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logger.warning(f"Error calculating hash for {file_path}: {e}")
        return ""


def get_ingested_files() -> Tuple[Set[str], Dict[str, str]]:
    """
    Get list of files that have already been ingested into ChromaDB.
    Returns: (set of filenames, dict of filename -> hash)
    """
    try:
        collection = get_collection()
        # Get all documents from collection to check metadata
        results = collection.get()
        
        ingested_files = set()
        file_hashes = {}
        
        if results and "metadatas" in results:
            for metadata in results["metadatas"]:
                if "source" in metadata:
                    filename = metadata["source"]
                    ingested_files.add(filename)
                    # Store hash if available in metadata
                    if "file_hash" in metadata:
                        file_hashes[filename] = metadata["file_hash"]
        
        return ingested_files, file_hashes
    except Exception as e:
        logger.warning(f"Error getting ingested files: {e}")
        return set(), {}


def remove_file_from_database(filename: str):
    """Remove all chunks for a specific file from the database."""
    try:
        collection = get_collection()
        # Get all documents
        results = collection.get()
        
        if results and "ids" in results and "metadatas" in results:
            ids_to_delete = []
            for i, metadata in enumerate(results["metadatas"]):
                if metadata.get("source") == filename:
                    ids_to_delete.append(results["ids"][i])
            
            if ids_to_delete:
                collection.delete(ids=ids_to_delete)
                logger.info(f"Removed {len(ids_to_delete)} chunks for {filename}")
    except Exception as e:
        logger.warning(f"Error removing file {filename} from database: {e}")


def load_existing_documents(force_reload: bool = False):
    """
    Scan the existing documents folder and automatically ingest any documents
    that haven't been processed yet or have been changed.
    
    Args:
        force_reload: If True, reprocess all files even if already ingested
    """
    docs_dir = Path(settings.DOCUMENTS_DIR)
    
    if not docs_dir.exists():
        logger.info(f"Documents directory does not exist: {docs_dir}. Creating it...")
        docs_dir.mkdir(parents=True, exist_ok=True)
        return
    
    # Get list of already ingested files and their hashes
    ingested_files, file_hashes = get_ingested_files()
    logger.info(f"Found {len(ingested_files)} already ingested files in database")
    
    # Find all supported files in the documents folder
    all_files = []
    for ext in settings.ALLOWED_EXTENSIONS:
        all_files.extend(docs_dir.glob(f"*{ext}"))
        all_files.extend(docs_dir.glob(f"*{ext.upper()}"))
    
    if not all_files:
        logger.info(f"No documents found in {docs_dir}")
        return
    
    logger.info(f"Found {len(all_files)} document(s) in {docs_dir}")
    
    # Determine which files need processing
    files_to_ingest = []
    files_to_reprocess = []
    
    for file_path in all_files:
        current_hash = get_file_hash(file_path)
        stored_hash = file_hashes.get(file_path.name, "")
        
        if force_reload:
            # Remove old data if forcing reload
            if file_path.name in ingested_files:
                remove_file_from_database(file_path.name)
            files_to_ingest.append((file_path, current_hash))
        elif file_path.name not in ingested_files:
            # New file
            files_to_ingest.append((file_path, current_hash))
        elif current_hash and stored_hash and current_hash != stored_hash:
            # File has changed
            logger.info(f"File {file_path.name} has been modified, reprocessing...")
            remove_file_from_database(file_path.name)
            files_to_ingest.append((file_path, current_hash))
            files_to_reprocess.append(file_path.name)
    
    if not files_to_ingest:
        logger.info("All documents are up to date")
        return
    
    if files_to_reprocess:
        logger.info(f"Reprocessing {len(files_to_reprocess)} modified file(s): {', '.join(files_to_reprocess)}")
    
    logger.info(f"Processing {len(files_to_ingest)} document(s)...")
    
    # Process each file
    success_count = 0
    error_count = 0
    
    for file_path, file_hash in files_to_ingest:
        try:
            logger.info(f"Processing: {file_path.name} ({file_path.suffix.upper()})")
            result = rag_service.ingest_document(str(file_path), file_hash=file_hash)
            success_count += 1
            logger.info(
                f"✓ Successfully ingested {file_path.name} "
                f"({result['chunks_ingested']} chunks)"
            )
        except Exception as e:
            error_count += 1
            logger.error(f"✗ Error processing {file_path.name}: {str(e)}")
    
    logger.info(
        f"Document loading complete: "
        f"{success_count} succeeded, {error_count} failed"
    )
