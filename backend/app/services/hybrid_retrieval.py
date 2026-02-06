"""
Hybrid Retrieval System V2 - Simplified and Robust
Works with ChromaDB's actual operator support limitations
"""

from typing import List, Dict, Optional, Tuple
import logging
import re
from app.core.database import get_collection
from app.services.embeddings import embedding_service

logger = logging.getLogger(__name__)


def extract_section_number(query: str) -> Optional[str]:
    """Extract section number from query."""
    patterns = [
        r'section\s+(\d+)',
        r'sec\.\s*(\d+)',
        r'दफा\s+([०-९\d]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query.lower())
        if match:
            section_num = match.group(1)
            # Convert Nepali digits if needed
            nepali_to_english = {
                '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
                '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
            }
            for nep, eng in nepali_to_english.items():
                section_num = section_num.replace(nep, eng)
            return section_num
    
    return None


def extract_chapter_number(query: str) -> Optional[int]:
    """Extract chapter number from query."""
    patterns = [
        r'chapter\s+(\d+)',
        r'chapter\s+([ivxlc]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query.lower())
        if match:
            chapter_str = match.group(1)
            
            # If Roman numeral
            if not chapter_str.isdigit():
                roman_values = {'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100}
                result = 0
                prev = 0
                for char in reversed(chapter_str.lower()):
                    val = roman_values.get(char, 0)
                    if val < prev:
                        result -= val
                    else:
                        result += val
                    prev = val
                return result
            else:
                return int(chapter_str)
    
    return None


def identify_target_act(query: str) -> Optional[str]:
    """
    Identify which act the user is asking about.
    Returns the key part of the act name for reliable matching.
    """
    q = query.lower()
    
    # PRIORITY 1: Direct exact mentions (highest confidence)
    if 'eta' in q or 'electronic transaction act' in q:
        return "Electronic Transaction"
    
    if 'cooperative act' in q or 'cooperatives act' in q:
        return "Cooperatives"
    
    if 'banking offence' in q or 'bopa' in q:
        return "Banking"
    
    # PRIORITY 2: Nepali keywords
    if 'सहकारी' in q or 'सहकारी ऐन' in q:
        return "Cooperatives"
    
    if 'इलेक्ट्रोनिक' in q:
        return "Electronic Transaction"
    
    # PRIORITY 3: Topic-based routing (lower confidence)
    # Only apply if NOT asking about sections (to avoid confusion)
    if 'section' not in q and 'दफा' not in q:
        cooperative_topics = [
            "register", "registration", "formation", "board member",
            "loan", "audit", "fund management", "share", "dividend",
            "committee", "general meeting"
        ]
        
        eta_topics = [
            "digital signature", "electronic document", "electronic record",
            "cyber", "hacking", "breach", "unauthorized access", 
            "authentication", "encryption", "hash"
        ]
        
        if any(topic in q for topic in cooperative_topics):
            return "Cooperatives"
        
        if any(topic in q for topic in eta_topics):
            return "Electronic Transaction"
    
    return None


def hybrid_retrieve(query: str, top_k: int = 3) -> Dict:
    """
    Hybrid retrieval with section and chapter support.
    
    Strategy:
    1. Check for chapter query first
    2. Check for section query
    3. Fall back to semantic search
    """
    
    collection = get_collection()
    count = collection.count()
    
    if count == 0:
        return {
            "contexts": [],
            "citations": [],
            "retrieval_method": "empty_collection"
        }
    
    # Step 1: Extract query type and target act
    chapter_num = extract_chapter_number(query)
    section_num = extract_section_number(query)
    target_act = identify_target_act(query)
    
    contexts = []
    citations = []
    
    # Step 2: Handle chapter query (retrieve all sections in that chapter)
    if chapter_num:
        logger.info(f"Chapter query: Chapter {chapter_num} of {target_act or 'any act'}")
        
        try:
            # Get all documents
            results = collection.get(
                limit=count,
                include=["documents", "metadatas"]
            )
            
            if results and results.get("documents"):
                for i, doc in enumerate(results["documents"]):
                    metadata = results["metadatas"][i] if results.get("metadatas") else {}
                    
                    # Filter by chapter and act
                    chunk_chapter = metadata.get("chapter_number")
                    act_name = metadata.get("act_name", "")
                    
                    if chunk_chapter == chapter_num:
                        if target_act and not any(keyword in act_name for keyword in target_act.split()):
                            continue
                        
                        contexts.append(doc)
                        citations.append({
                            "source": act_name,
                            "page": f"Chapter {chapter_num}, Section {metadata.get('section_number', 'N/A')}",
                            "excerpt": doc[:200] + "..." if len(doc) > 200 else doc,
                            "relevance_score": 1.0,
                            "match_type": "chapter"
                        })
                
                if contexts:
                    logger.info(f"Found {len(contexts)} sections in Chapter {chapter_num}")
                    return {
                        "contexts": contexts,
                        "citations": citations,
                        "retrieval_method": f"chapter_{chapter_num}_match"
                    }
        except Exception as e:
            logger.error(f"Chapter query failed: {e}")
    
    # Step 3: Try exact section match (using Python-side filtering)
    if section_num:
        logger.info(f"Section query: Section {section_num}, filtering for: {target_act or 'any act'}")
        
        try:
            # Get all documents with this section number (no complex where clause)
            results = collection.get(
                where={"section_number": section_num},  # Simple, single condition
                limit=10  # Get more, filter in Python
            )
            
            if results and results.get("documents"):
                # Filter by act name in Python (more reliable)
                for i, doc in enumerate(results["documents"]):
                    metadata = results["metadatas"][i] if results.get("metadatas") else {}
                    act_name = metadata.get("act_name", "")
                    
                    # If we have a target act, apply strict filtering
                    if target_act:
                        # Check if act name contains the target keywords
                        if not any(keyword in act_name for keyword in target_act.split()):
                            logger.debug(f"Skipping {act_name} (looking for {target_act})")
                            continue
                    
                    contexts.append(doc)
                    citations.append({
                        "source": act_name,
                        "page": f"Section {metadata.get('section_number', 'N/A')}",
                        "excerpt": doc[:200] + "..." if len(doc) > 200 else doc,
                        "relevance_score": 1.0,
                        "match_type": "exact"
                    })
                    
                    if len(contexts) >= top_k:
                        break
                
                if contexts:
                    logger.info(f"✅ Found {len(contexts)} exact section matches after filtering")
                    return {
                        "contexts": contexts,
                        "citations": citations,
                        "retrieval_method": "exact_metadata_match"
                    }
                else:
                    logger.warning(f"⚠️ Section {section_num} exists but in wrong act (looking for {target_act})")
        
        except Exception as e:
            logger.warning(f"Exact match failed: {e}, falling back to semantic search")
    
    # Step 3: Semantic search (no complex where clause, filter in Python)
    logger.info(f"Using semantic search{f', filtering for: {target_act}' if target_act else ''}")
    
    try:
        query_embedding = embedding_service.embed_text(query)
        
        # Get more results than needed (we'll filter in Python)
        search_k = min(top_k * 3, count, 20)
        
        # Simple semantic search with NO where clause (most reliable)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=search_k
        )
        
        if results and results.get("documents") and len(results["documents"][0]) > 0:
            for i, doc in enumerate(results["documents"][0]):
                if len(contexts) >= top_k:
                    break
                
                metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                distance = results["distances"][0][i] if results.get("distances") else None
                
                # Calculate similarity
                similarity_score = 1 - (distance / 2.0) if distance is not None else 0.5
                
                # Filter by similarity threshold
                if similarity_score < 0.3:
                    continue
                
                # Filter by act in Python (strict keyword matching)
                chunk_act = metadata.get("act_name", "")
                if target_act:
                    if not any(keyword in chunk_act for keyword in target_act.split()):
                        logger.debug(f"Skipping {chunk_act} (looking for {target_act})")
                        continue
                
                contexts.append(doc)
                citations.append({
                    "source": chunk_act or "Unknown",
                    "page": f"Section {metadata.get('section_number', 'N/A')}",
                    "excerpt": doc[:200] + "..." if len(doc) > 200 else doc,
                    "relevance_score": round(similarity_score, 3),
                    "match_type": "semantic"
                })
    
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        # Return whatever we have
        pass
    
    return {
        "contexts": contexts,
        "citations": citations,
        "retrieval_method": f"semantic_search{f' (filtered to {target_act})' if target_act else ''}"
    }
