"""
Legal Documents Re-ingestion Script
Clears collection and re-ingests all PDFs with section-aware chunking
"""

import sys
from pathlib import Path
import os

# Disable telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"

sys.path.append(str(Path(__file__).parent))

from app.core.database import get_collection
from app.services.rag import rag_service
from app.services.documents import document_service
import hashlib

DATA_DIR = Path(__file__).parent.parent / "data" / "documents"

def clear_collection():
    """Clear all documents from collection."""
    collection = get_collection()
    count = collection.count()
    
    if count == 0:
        print("✅ Collection already empty")
        return
    
    print(f"🗑️  Clearing {count} existing documents...")
    
    try:
        # Get all IDs
        results = collection.get(limit=count)
        if results and results.get("ids"):
            ids = results["ids"]
            # Delete in batches
            batch_size = 100
            for i in range(0, len(ids), batch_size):
                batch = ids[i:i+batch_size]
                collection.delete(ids=batch)
                print(f"   Deleted {min(i+batch_size, len(ids))}/{len(ids)} documents")
        
        print(f"✅ Collection cleared")
    except Exception as e:
        print(f"❌ Error clearing collection: {e}")
        raise

def ingest_pdf(pdf_path: Path):
    """Ingest a single PDF with section-aware chunking."""
    print(f"\n📄 Processing: {pdf_path.name}")
    
    try:
        # Calculate file hash for deduplication
        with open(pdf_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        
        # Ingest into RAG system (pass file path, not chunks)
        # ingest_document will handle extraction internally
        result = rag_service.ingest_document(str(pdf_path), file_hash=file_hash)
        
        if result.get("status") == "success":
            chunks_count = result.get("chunks_ingested", 0)
            print(f"   ✅ Ingested {chunks_count} chunks")
            
            # Try to extract section info for display
            try:
                chunks = document_service.extract_text_from_pdf(str(pdf_path))
                section_chunks = [c for c in chunks if c.get("metadata", {}).get("has_section_structure")]
                if section_chunks:
                    section_nums = set()
                    for chunk in section_chunks:
                        section_num = chunk.get("metadata", {}).get("section_number")
                        if section_num:
                            section_nums.add(section_num)
                    print(f"   📋 Sections: {', '.join(sorted(section_nums, key=lambda x: int(x) if x.isdigit() else 999))}")
            except:
                pass  # Section display is optional
            
            return True
        else:
            print(f"   ❌ Ingestion failed: {result}")
            return False
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main re-ingestion workflow."""
    print("\n" + "="*70)
    print("🔄 LEGAL DOCUMENTS RE-INGESTION")
    print("="*70 + "\n")
    
    if not DATA_DIR.exists():
        print(f"❌ Data directory not found: {DATA_DIR}")
        return
    
    # Find all PDFs
    pdf_files = list(DATA_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {DATA_DIR}")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF file(s):")
    for pdf in pdf_files:
        print(f"   - {pdf.name}")
    
    # Step 1: Clear existing collection
    print("\n" + "-"*70)
    print("STEP 1: Clearing existing collection")
    print("-"*70)
    clear_collection()
    
    # Step 2: Ingest each PDF
    print("\n" + "-"*70)
    print("STEP 2: Ingesting PDFs with section-aware chunking")
    print("-"*70)
    
    success_count = 0
    for pdf_path in sorted(pdf_files):
        if ingest_pdf(pdf_path):
            success_count += 1
    
    # Step 3: Verify results
    print("\n" + "-"*70)
    print("STEP 3: Verification")
    print("-"*70)
    
    collection = get_collection()
    final_count = collection.count()
    
    print(f"\n📊 RESULTS:")
    print(f"   PDFs processed: {len(pdf_files)}")
    print(f"   PDFs successful: {success_count}")
    print(f"   Total chunks in DB: {final_count}")
    
    if success_count == len(pdf_files) and final_count > 0:
        print("\n✅ Re-ingestion completed successfully!")
        print("\nNext steps:")
        print("   1. Run: python verify_sections.py")
        print("   2. Run: python eval_legal_qa.py")
        print("   3. Run: python test_behavioral_contract.py")
    else:
        print("\n⚠️  Re-ingestion completed with issues")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
