"""
Test Structured Legal RAG Components
Verifies query understanding and classification logic
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.services.query_understanding import understand_query
from app.services.legal_classifier import legal_classifier


def test_query_understanding():
    """Test query understanding component."""
    
    print("="*80)
    print("TEST 1: QUERY UNDERSTANDING")
    print("="*80)
    print()
    
    test_cases = [
        ("What is Section 18 of ETA?", "Section query"),
        ("What are byelaws and internal procedures?", "Bylaws query"),
        ("What is the penalty for unauthorized access?", "Penalty query"),
        ("How to register a cooperative?", "Registration query"),
        ("What are membership requirements?", "Membership query"),
        ("Tell me about Chapter 3", "Chapter query"),
        ("What does digital signature mean?", "Definition query"),
    ]
    
    for query, description in test_cases:
        print(f"Query: {query}")
        print(f"Description: {description}")
        
        result = understand_query(query)
        
        print(f"Result:")
        print(f"  Intent Type: {result['intent_type']}")
        print(f"  Detected Act: {result['detected_act']}")
        print(f"  Topic Scope: {result['topic_scope']}")
        print(f"  Section: {result['section_number']}")
        print(f"  Chapter: {result['chapter_number']}")
        print()
        print("-"*80)
        print()


def test_legal_classification():
    """Test legal classifier component."""
    
    print("="*80)
    print("TEST 2: LEGAL CLASSIFICATION")
    print("="*80)
    print()
    
    test_cases = [
        {
            "text": "No person shall operate a Cooperative Organization without getting it Registered under this Act.",
            "section_number": "12",
            "section_title": "Registration of Cooperative",
            "act_name": "Cooperatives Act 2017"
        },
        {
            "text": "If any person commits an offence of unauthorized access, they shall be liable to imprisonment up to 3 years or fine up to Rs. 100,000.",
            "section_number": "41",
            "section_title": "Penalty for Unauthorized Access",
            "act_name": "Electronic Transaction Act 2063"
        },
        {
            "text": "The term 'electronic record' means data or information that has been created, generated, sent, communicated, received, or stored by electronic means.",
            "section_number": "2",
            "section_title": "Definitions",
            "act_name": "Electronic Transaction Act 2063"
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test Case {i}:")
        print(f"  Section: {test_case['section_number']}")
        print(f"  Title: {test_case['section_title']}")
        print(f"  Act: {test_case['act_name']}")
        print(f"  Text: {test_case['text'][:100]}...")
        print()
        
        try:
            result = legal_classifier.classify_section(
                section_text=test_case["text"],
                section_number=test_case["section_number"],
                section_title=test_case["section_title"],
                act_name=test_case["act_name"]
            )
            
            print(f"  Classification:")
            print(f"    Legal Type: {result['legal_type']}")
            print(f"    Legal Scope: {result['legal_scope']}")
            print(f"  ✅ Classification successful")
        
        except Exception as e:
            print(f"  ❌ Classification failed: {e}")
        
        print()
        print("-"*80)
        print()


def test_filter_logic():
    """Test filter matching logic."""
    
    print("="*80)
    print("TEST 3: FILTER MATCHING LOGIC")
    print("="*80)
    print()
    
    from app.services.constrained_retrieval import _scope_matches
    
    test_cases = [
        ("membership", "membership", True),
        ("membership", "member", True),
        ("registration", "register", True),
        ("governance", "bylaws", True),
        ("finance", "audit", False),
        ("penalty", "offence", True),
        ("cybercrime", "unauthorized_access", True),
    ]
    
    for query_scope, chunk_scope, expected in test_cases:
        result = _scope_matches(query_scope, chunk_scope)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{query_scope}' vs '{chunk_scope}': {result} (expected: {expected})")
    
    print()


if __name__ == "__main__":
    print("\n")
    print("*"*80)
    print("STRUCTURED LEGAL RAG - COMPONENT TESTING")
    print("*"*80)
    print("\n")
    
    test_query_understanding()
    test_legal_classification()
    test_filter_logic()
    
    print("\n")
    print("="*80)
    print("TESTING COMPLETE")
    print("="*80)
    print()
    print("Next step: Run reingest_with_classification.py to add metadata to documents")
    print()
