"""
Re-ingest Legal Documents with Classification
Adds legal_type and legal_scope metadata to all chunks
"""

import sys
import os
import logging

# Disable telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.core.database import get_collection
from app.services.rag import rag_service


def clear_collection():
    """Clear the existing collection."""
    collection = get_collection()
    count = collection.count()
    
    if count > 0:
        logger.info(f"Clearing {count} existing chunks...")
        # Get all IDs and delete
        all_data = collection.get()
        if all_data and all_data.get("ids"):
            collection.delete(ids=all_data["ids"])
            logger.info(f"✅ Cleared {len(all_data['ids'])} chunks")
    else:
        logger.info("Collection is already empty")


def reingest_documents():
    """Re-ingest all PDF documents with legal classification."""
    
    # Document directory
    docs_dir = Path(__file__).parent.parent / "data" / "documents"
    
    if not docs_dir.exists():
        logger.error(f"Documents directory not found: {docs_dir}")
        return
    
    # Find all PDF files
    pdf_files = list(docs_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.error(f"No PDF files found in {docs_dir}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to ingest")
    
    for idx, pdf_path in enumerate(pdf_files, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"[{idx}/{len(pdf_files)}] Processing: {pdf_path.name}")
        logger.info(f"{'='*80}")
        
        try:
            # Ingest document (will automatically classify sections)
            result = rag_service.ingest_document(str(pdf_path))
            
            logger.info(f"✅ Successfully ingested {pdf_path.name}")
            logger.info(f"   Chunks created: {result.get('chunks_ingested', 0)}")
            
        except Exception as e:
            logger.error(f"❌ Failed to ingest {pdf_path.name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Verify final count
    collection = get_collection()
    final_count = collection.count()
    logger.info(f"\n{'='*80}")
    logger.info(f"Re-ingestion complete!")
    logger.info(f"Total chunks in database: {final_count}")
    logger.info(f"{'='*80}")


def verify_classification():
    """Verify that classification metadata exists."""
    collection = get_collection()
    
    logger.info("\nVerifying classification metadata...")
    
    # Get a sample of documents
    sample = collection.get(limit=5, include=["metadatas"])
    
    if sample and sample.get("metadatas"):
        logger.info("\nSample metadata:")
        for i, metadata in enumerate(sample["metadatas"][:3], 1):
            logger.info(f"\n[Chunk {i}]")
            logger.info(f"  Act: {metadata.get('act_name', 'N/A')}")
            logger.info(f"  Section: {metadata.get('section_number', 'N/A')}")
            logger.info(f"  Legal Type: {metadata.get('legal_type', 'MISSING')}")
            logger.info(f"  Legal Scope: {metadata.get('legal_scope', 'MISSING')}")
            
            if not metadata.get("legal_type"):
                logger.warning("  ⚠️  Legal classification metadata is MISSING!")
    else:
        logger.warning("No metadata found in collection")


if __name__ == "__main__":
    print("="*80)
    print("STRUCTURED LEGAL RAG - Document Re-ingestion with Classification")
    print("="*80)
    print()
    
    print("This script will:")
    print("1. Clear existing collection")
    print("2. Re-ingest all PDF documents")
    print("3. Classify each section with legal_type and legal_scope")
    print("4. Verify classification metadata")
    print()
    
    response = input("Proceed? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        print("\nStarting re-ingestion...\n")
        
        # Step 1: Clear collection
        clear_collection()
        
        # Step 2: Re-ingest with classification
        reingest_documents()
        
        # Step 3: Verify
        verify_classification()
        
        print("\n✅ Re-ingestion complete! New metadata includes legal_type and legal_scope.")
        print("You can now test the structured retrieval system.")
    else:
        print("Aborted.")
