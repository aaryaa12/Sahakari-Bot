"""
Query Understanding Service
Classifies user queries to enable constrained legal retrieval
"""

from typing import Dict, Optional
import logging
import re

logger = logging.getLogger(__name__)


def understand_query(query: str) -> Dict[str, Optional[str]]:
    """
    Analyze user query to determine intent, target act, and topic scope.
    
    Returns:
        {
            "intent_type": str,  # definition/obligation/procedure/permission/penalty/general
            "detected_act": str,  # ETA/COOPERATIVE_ACT/UNKNOWN
            "topic_scope": str,  # topic label (membership, bylaws, authentication, etc.)
            "section_number": str,  # if asking for specific section
            "chapter_number": int  # if asking for specific chapter
        }
    """
    
    query_lower = query.lower()
    
    # Extract section/chapter if present
    section_num = _extract_section_number(query_lower)
    chapter_num = _extract_chapter_number(query_lower)
    
    # Detect target act
    detected_act = _detect_act(query_lower)
    
    # Detect intent type
    intent_type = _detect_intent_type(query_lower)
    
    # Detect topic scope
    topic_scope = _detect_topic_scope(query_lower, detected_act)
    
    return {
        "intent_type": intent_type,
        "detected_act": detected_act,
        "topic_scope": topic_scope,
        "section_number": section_num,
        "chapter_number": chapter_num
    }


def _extract_section_number(query: str) -> Optional[str]:
    """Extract section number from query."""
    patterns = [
        r'section\s+(\d+)',
        r'sec\.\s*(\d+)',
        r'sec\s+(\d+)',
        r'दफा\s+([०-९\d]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query)
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


def _extract_chapter_number(query: str) -> Optional[int]:
    """Extract chapter number from query."""
    patterns = [
        r'chapter\s+(\d+)',
        r'chapter\s+([ivxlc]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            chapter_str = match.group(1)
            
            # If Roman numeral
            if not chapter_str.isdigit():
                roman_values = {'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100}
                result = 0
                prev = 0
                for char in reversed(chapter_str):
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


def _detect_act(query: str) -> str:
    """
    Detect which act the user is asking about.
    Returns: ETA, COOPERATIVE_ACT, or UNKNOWN
    """
    
    # Direct mentions (highest priority)
    if 'eta' in query or 'electronic transaction act' in query:
        return "ETA"
    
    if 'cooperative act' in query or 'cooperatives act' in query:
        return "COOPERATIVE_ACT"
    
    if 'bopa' in query or 'banking offence' in query:
        return "BANKING"
    
    # Topic-based routing (only if not asking about specific sections)
    if 'section' not in query and 'chapter' not in query:
        # Cooperative topics
        coop_keywords = [
            "register", "registration", "formation", "board", "member",
            "committee", "loan", "audit", "bylaws", "byelaws", "share",
            "dividend", "fund", "cooperative", "general meeting"
        ]
        
        # ETA topics
        eta_keywords = [
            "digital signature", "electronic document", "electronic record",
            "cyber", "hacking", "breach", "unauthorized access",
            "authentication", "encryption", "hash", "certifying authority"
        ]
        
        coop_count = sum(1 for kw in coop_keywords if kw in query)
        eta_count = sum(1 for kw in eta_keywords if kw in query)
        
        if coop_count > eta_count and coop_count > 0:
            return "COOPERATIVE_ACT"
        elif eta_count > 0:
            return "ETA"
    
    return "UNKNOWN"


def _detect_intent_type(query: str) -> str:
    """
    Detect what kind of legal information the user wants.
    Returns: definition/obligation/procedure/permission/penalty/general
    """
    
    # Definition queries
    if any(word in query for word in [
        'what is', 'what are', 'meaning of', 'define', 'definition',
        'explain', 'means', 'refer to'
    ]):
        return "definition"
    
    # Penalty queries
    if any(word in query for word in [
        'penalty', 'fine', 'punishment', 'imprisonment', 'jail',
        'consequences', 'liable', 'punishable'
    ]):
        return "penalty"
    
    # Obligation queries (must/required/mandatory)
    if any(word in query for word in [
        'must', 'required', 'mandatory', 'obligation', 'duty',
        'have to', 'need to', 'responsible for'
    ]):
        return "obligation"
    
    # Permission queries (can/may/allowed)
    if any(word in query for word in [
        'can ', 'may ', 'allowed', 'permitted', 'eligible',
        'entitled to', 'right to'
    ]):
        return "permission"
    
    # Procedure queries (how to)
    if any(word in query for word in [
        'how to', 'how do', 'process', 'procedure', 'steps',
        'register', 'apply', 'submit', 'file'
    ]):
        return "procedure"
    
    # Default: general
    return "general"


def _detect_topic_scope(query: str, detected_act: str) -> str:
    """
    Detect the topic/domain of the query.
    Returns: topic label like "membership", "registration", "authentication", etc.
    """
    
    # Common topics across acts
    if any(word in query for word in ['register', 'registration', 'form']):
        return "registration"
    
    if any(word in query for word in ['member', 'membership', 'eligibility']):
        return "membership"
    
    if any(word in query for word in ['penalty', 'fine', 'punishment', 'offense', 'offence']):
        return "offence"
    
    # Cooperative-specific topics
    if detected_act == "COOPERATIVE_ACT":
        if any(word in query for word in ['board', 'committee', 'election', 'meeting']):
            return "governance"
        
        if any(word in query for word in ['bylaw', 'byelaw', 'internal procedure', 'rule']):
            return "governance"
        
        if any(word in query for word in ['fund', 'capital', 'share', 'dividend', 'loan']):
            return "finance"
        
        if any(word in query for word in ['audit', 'auditor', 'financial statement']):
            return "audit"
        
        if any(word in query for word in ['dissolution', 'liquidation', 'winding']):
            return "dissolution"
    
    # ETA-specific topics
    if detected_act == "ETA":
        if any(word in query for word in ['digital signature', 'signature', 'sign']):
            return "digital_signature"
        
        if any(word in query for word in ['electronic record', 'electronic document', 'data message']):
            return "electronic_record"
        
        if any(word in query for word in ['authentication', 'certifying authority', 'controller']):
            return "authentication"
        
        if any(word in query for word in ['hacking', 'unauthorized access', 'cyber', 'breach']):
            return "cybercrime"
        
        if any(word in query for word in ['data protection', 'privacy', 'confidential']):
            return "data_protection"
    
    return "general"
