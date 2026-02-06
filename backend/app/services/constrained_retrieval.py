"""
Constrained Legal Retrieval
Implements structured legal database lookup: Filter by legal structure → Semantic search
"""

from typing import List, Dict, Optional
import logging
from app.core.database import get_collection
from app.services.embeddings import embedding_service
from app.services.query_understanding import understand_query

logger = logging.getLogger(__name__)


def constrained_retrieve(query: str, top_k: int = 4) -> Dict:
    """
    Constrained legal retrieval with structure-first filtering.
    
    Strategy:
    1. Understand query (intent, act, topic, section/chapter)
    2. Build metadata filters based on query understanding
    3. Apply filters to narrow search space
    4. Perform semantic search within filtered subset
    5. Return top-k results
    
    Returns:
        {
            "contexts": List[str],
            "citations": List[Dict],
            "retrieval_method": str,
            "filters_applied": Dict
        }
    """
    
    collection = get_collection()
    count = collection.count()
    
    if count == 0:
        return {
            "contexts": [],
            "citations": [],
            "retrieval_method": "empty_collection",
            "filters_applied": {}
        }
    
    # STEP 1: Understand query
    query_intent = understand_query(query)
    logger.info(f"Query understanding: {query_intent}")
    
    section_num = query_intent["section_number"]
    chapter_num = query_intent["chapter_number"]
    detected_act = query_intent["detected_act"]
    intent_type = query_intent["intent_type"]
    topic_scope = query_intent["topic_scope"]
    
    # STEP 2: Handle specific section/chapter queries (highest priority - exact match)
    if section_num:
        return _retrieve_by_section(
            section_num, detected_act, top_k, collection
        )
    
    if chapter_num:
        return _retrieve_by_chapter(
            chapter_num, detected_act, top_k, collection
        )
    
    # STEP 3: Constrained semantic search with filters
    return _constrained_semantic_search(
        query=query,
        detected_act=detected_act,
        intent_type=intent_type,
        topic_scope=topic_scope,
        top_k=top_k,
        collection=collection
    )


def _retrieve_by_section(
    section_num: str,
    detected_act: str,
    top_k: int,
    collection
) -> Dict:
    """Retrieve exact section (deterministic)."""
    
    logger.info(f"Section query: Section {section_num} from {detected_act}")
    
    try:
        # Build where clause
        where_clause = {"section_number": section_num}
        
        # Get all matching sections
        results = collection.get(
            where=where_clause,
            limit=20  # Get multiple, filter in Python
        )
        
        if not results or not results.get("documents"):
            return {
                "contexts": [],
                "citations": [],
                "retrieval_method": "section_not_found",
                "filters_applied": {"section_number": section_num}
            }
        
        # Filter by act in Python
        contexts = []
        citations = []
        
        for i, doc in enumerate(results["documents"]):
            metadata = results["metadatas"][i] if results.get("metadatas") else {}
            act_name = metadata.get("act_name", "")
            
            # Apply act filter if specified
            if detected_act != "UNKNOWN":
                act_keywords = {
                    "ETA": ["Electronic", "Transaction"],
                    "COOPERATIVE_ACT": ["Cooperative"],
                    "BANKING": ["Banking"]
                }
                
                keywords = act_keywords.get(detected_act, [])
                if not any(kw in act_name for kw in keywords):
                    continue
            
            contexts.append(doc)
            citations.append({
                "source": act_name,
                "page": f"Section {metadata.get('section_number', 'N/A')}",
                "excerpt": doc[:200] + "..." if len(doc) > 200 else doc,
                "relevance_score": 1.0,
                "match_type": "exact_section",
                "legal_type": metadata.get("legal_type", "unknown"),
                "legal_scope": metadata.get("legal_scope", "unknown")
            })
            
            if len(contexts) >= top_k:
                break
        
        return {
            "contexts": contexts,
            "citations": citations,
            "retrieval_method": "exact_section_match",
            "filters_applied": {"section_number": section_num, "act": detected_act}
        }
    
    except Exception as e:
        logger.error(f"Section retrieval error: {e}")
        return {
            "contexts": [],
            "citations": [],
            "retrieval_method": "section_query_failed",
            "filters_applied": {}
        }


def _retrieve_by_chapter(
    chapter_num: int,
    detected_act: str,
    top_k: int,
    collection
) -> Dict:
    """Retrieve all sections in a chapter."""
    
    logger.info(f"Chapter query: Chapter {chapter_num} from {detected_act}")
    
    try:
        # Get all documents (ChromaDB has limited where clause support)
        results = collection.get(
            limit=500  # Get more for filtering
        )
        
        if not results or not results.get("documents"):
            return {
                "contexts": [],
                "citations": [],
                "retrieval_method": "chapter_not_found",
                "filters_applied": {"chapter_number": chapter_num}
            }
        
        # Filter by chapter and act in Python
        contexts = []
        citations = []
        
        for i, doc in enumerate(results["documents"]):
            metadata = results["metadatas"][i] if results.get("metadatas") else {}
            
            # Check chapter number
            if metadata.get("chapter_number") != chapter_num:
                continue
            
            # Check act if specified
            act_name = metadata.get("act_name", "")
            if detected_act != "UNKNOWN":
                act_keywords = {
                    "ETA": ["Electronic", "Transaction"],
                    "COOPERATIVE_ACT": ["Cooperative"],
                    "BANKING": ["Banking"]
                }
                
                keywords = act_keywords.get(detected_act, [])
                if not any(kw in act_name for kw in keywords):
                    continue
            
            contexts.append(doc)
            citations.append({
                "source": act_name,
                "page": f"Chapter {chapter_num}, Section {metadata.get('section_number', 'N/A')}",
                "excerpt": doc[:200] + "..." if len(doc) > 200 else doc,
                "relevance_score": 1.0,
                "match_type": "chapter_match",
                "legal_type": metadata.get("legal_type", "unknown"),
                "legal_scope": metadata.get("legal_scope", "unknown")
            })
            
            if len(contexts) >= top_k * 2:  # Get more for chapters
                break
        
        return {
            "contexts": contexts[:top_k * 2],  # Allow more results for chapters
            "citations": citations[:top_k * 2],
            "retrieval_method": "chapter_match",
            "filters_applied": {"chapter_number": chapter_num, "act": detected_act}
        }
    
    except Exception as e:
        logger.error(f"Chapter retrieval error: {e}")
        return {
            "contexts": [],
            "citations": [],
            "retrieval_method": "chapter_query_failed",
            "filters_applied": {}
        }


def _constrained_semantic_search(
    query: str,
    detected_act: str,
    intent_type: str,
    topic_scope: str,
    top_k: int,
    collection
) -> Dict:
    """
    Semantic search with legal structure constraints.
    
    Filters applied:
    1. Act name (if detected)
    2. Legal type (if clear intent)
    3. Legal scope (if specific topic)
    """
    
    logger.info(f"Constrained search: act={detected_act}, intent={intent_type}, scope={topic_scope}")
    
    # Build filter description
    filters = {}
    
    # Map detected act to keywords
    act_keywords = {
        "ETA": ["Electronic", "Transaction"],
        "COOPERATIVE_ACT": ["Cooperative"],
        "BANKING": ["Banking"]
    }
    
    if detected_act != "UNKNOWN":
        filters["act"] = detected_act
    
    if intent_type != "general":
        filters["intent_type"] = intent_type
    
    if topic_scope != "general":
        filters["topic_scope"] = topic_scope
    
    try:
        # Get query embedding
        query_embedding = embedding_service.embed_text(query)
        
        # CRITICAL: Do semantic search on ALL documents first
        # Then filter in Python (ChromaDB where clause is unreliable)
        search_k = min(top_k * 5, 50)  # Get more for filtering
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=search_k
        )
        
        if not results or not results.get("documents") or len(results["documents"][0]) == 0:
            return {
                "contexts": [],
                "citations": [],
                "retrieval_method": "no_semantic_results",
                "filters_applied": filters
            }
        
        # STEP: Filter results in Python by legal structure
        contexts = []
        citations = []
        
        for i, doc in enumerate(results["documents"][0]):
            if len(contexts) >= top_k:
                break
            
            metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
            distance = results["distances"][0][i] if results.get("distances") else None
            
            # Calculate similarity
            similarity_score = 1 - (distance / 2.0) if distance is not None else 0.5
            
            # Filter by similarity threshold
            if similarity_score < 0.25:
                continue
            
            # FILTER 1: Act name (strict)
            if detected_act != "UNKNOWN":
                act_name = metadata.get("act_name", "")
                keywords = act_keywords.get(detected_act, [])
                if not any(kw in act_name for kw in keywords):
                    logger.debug(f"Filtered out {act_name} (want {detected_act})")
                    continue
            
            # FILTER 2: Legal type (if clear intent)
            if intent_type in ["penalty", "obligation", "permission", "restriction", "definition"]:
                chunk_legal_type = metadata.get("legal_type", "")
                if intent_type == "penalty" and chunk_legal_type != "penalty":
                    continue
                if intent_type == "definition" and chunk_legal_type != "definition":
                    continue
                # For obligation/permission/restriction, be more lenient (include procedure too)
            
            # FILTER 3: Legal scope (soft match - scope keywords)
            if topic_scope != "general":
                chunk_scope = metadata.get("legal_scope", "")
                # Check if scopes are related (fuzzy matching)
                if not _scope_matches(topic_scope, chunk_scope):
                    # Don't skip, but lower score
                    similarity_score *= 0.8
            
            contexts.append(doc)
            citations.append({
                "source": metadata.get("act_name", "Unknown"),
                "page": f"Section {metadata.get('section_number', 'N/A')}",
                "excerpt": doc[:200] + "..." if len(doc) > 200 else doc,
                "relevance_score": round(similarity_score, 3),
                "match_type": "constrained_semantic",
                "legal_type": metadata.get("legal_type", "unknown"),
                "legal_scope": metadata.get("legal_scope", "unknown")
            })
        
        return {
            "contexts": contexts,
            "citations": citations,
            "retrieval_method": "constrained_semantic_search",
            "filters_applied": filters
        }
    
    except Exception as e:
        logger.error(f"Constrained search error: {e}")
        return {
            "contexts": [],
            "citations": [],
            "retrieval_method": "search_failed",
            "filters_applied": filters
        }


def _scope_matches(query_scope: str, chunk_scope: str) -> bool:
    """Check if scopes are related (fuzzy matching)."""
    if query_scope == chunk_scope:
        return True
    
    # Fuzzy matching - check for partial overlap
    query_words = set(query_scope.replace("_", " ").split())
    chunk_words = set(chunk_scope.replace("_", " ").split())
    
    # If any words overlap, consider it a match
    if query_words & chunk_words:
        return True
    
    # Synonym matching
    synonyms = {
        "membership": ["member", "eligibility"],
        "governance": ["board", "committee", "bylaws", "byelaws"],
        "finance": ["fund", "capital", "share", "loan"],
        "registration": ["register", "formation"],
        "offence": ["penalty", "punishment", "fine"],
        "cybercrime": ["unauthorized_access", "hacking"],
        "authentication": ["digital_signature", "certification"]
    }
    
    for key, values in synonyms.items():
        if query_scope in values and (chunk_scope == key or chunk_scope in values):
            return True
        if chunk_scope in values and (query_scope == key or query_scope in values):
            return True
    
    return False
