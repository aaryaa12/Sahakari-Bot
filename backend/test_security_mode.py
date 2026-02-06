"""
Test Security Advisory Mode
Verifies that security questions route correctly and legal pipeline is unchanged
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.services.intent_router import detect_intent
from app.services.security_advisor import security_advisor
from app.services.rag import rag_service


def test_intent_routing():
    """Test that questions route to correct modes."""
    
    print("="*80)
    print("TEST 1: INTENT ROUTING")
    print("="*80)
    print()
    
    test_cases = [
        ("How to protect from insider risks?", "SECURITY"),
        ("What security measures should I implement?", "SECURITY"),
        ("How to prevent fraud in cooperative?", "SECURITY"),
        ("What is Section 18 of ETA?", "LEGAL"),
        ("What are the requirements for registration?", "LEGAL"),
        ("Tell me about byelaws", "LEGAL"),
        ("How to conduct board meetings?", "COOP"),
        ("Hello, how are you?", "GENERAL"),
    ]
    
    passed = 0
    failed = 0
    
    for query, expected in test_cases:
        result = detect_intent(query)
        status = "[PASS]" if result == expected else "[FAIL]"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} '{query[:40]}...'")
        print(f"   Expected: {expected}, Got: {result}")
        print()
    
    print(f"Results: {passed} passed, {failed} failed")
    print()


def test_security_advisor():
    """Test security advisor module directly."""
    
    print("="*80)
    print("TEST 2: SECURITY ADVISOR MODULE")
    print("="*80)
    print()
    
    query = "How can I protect my cooperative from insider risks?"
    print(f"Query: {query}")
    print()
    
    try:
        result = security_advisor.get_security_advice(query)
        
        print("Response:")
        print("-"*80)
        print(result["answer"][:500] + "..." if len(result["answer"]) > 500 else result["answer"])
        print("-"*80)
        print()
        print(f"Citations: {len(result['citations'])}")
        print(f"Sources: {result['sources_count']}")
        print()
        
        # Verify it's NOT using legal format
        answer_lower = result["answer"].lower()
        has_legal_format = all([
            "1) legal meaning" in answer_lower,
            "2) legal effect" in answer_lower,
            "5) evidence" in answer_lower
        ])
        
        if has_legal_format:
            print("[ERROR] Security advisor is using legal format!")
        else:
            print("[PASS] Security advisor NOT using legal format")
        
        # Verify it has practical guidance
        has_practical = any(word in answer_lower for word in [
            "access control", "segregation", "monitoring", "audit", "mfa"
        ])
        
        if has_practical:
            print("[PASS] Contains practical security guidance")
        else:
            print("[ERROR] Missing practical security guidance")
        
        # Verify framework references
        has_framework_refs = any(word in result["answer"] for word in [
            "NIST", "ISO 27001", "PR.AC", "A.9", "A.12"
        ])
        
        if has_framework_refs:
            print("[PASS] Contains framework control references")
        else:
            print("[WARNING] Missing framework control references")
        
        print()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print()


def test_legal_mode_unchanged():
    """Test that legal mode still works correctly."""
    
    print("="*80)
    print("TEST 3: LEGAL MODE UNCHANGED")
    print("="*80)
    print()
    
    query = "What is Section 18 of ETA?"
    print(f"Query: {query}")
    print()
    
    try:
        result = rag_service.query(query)
        
        print("Response Preview:")
        print("-"*80)
        print(result["answer"][:500] + "..." if len(result["answer"]) > 500 else result["answer"])
        print("-"*80)
        print()
        print(f"Citations: {len(result['citations'])}")
        print(f"Sources: {result['sources_count']}")
        print()
        
        # Verify legal format is STILL used
        answer_lower = result["answer"].lower()
        has_legal_format = any([
            "legal meaning" in answer_lower,
            "legal effect" in answer_lower,
            "evidence" in answer_lower
        ])
        
        if has_legal_format:
            print("[PASS] Legal mode using structured format")
        else:
            print("[WARNING] Legal format may be missing (check if Section 18 exists)")
        
        # Verify Act label is present
        if "electronic transaction act" in answer_lower and "section 18" in answer_lower:
            print("[PASS] Act + Section label present")
        else:
            print("[WARNING] Act/Section label may be missing")
        
        print()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print()


def test_end_to_end():
    """Test end-to-end query flow."""
    
    print("="*80)
    print("TEST 4: END-TO-END QUERY FLOW")
    print("="*80)
    print()
    
    # Test security question through full pipeline
    query = "What firewall should I use for my cooperative?"
    print(f"Query: {query}")
    print()
    
    try:
        result = rag_service.query(query)
        
        print("Response Preview:")
        print("-"*80)
        print(result["answer"][:300] + "..." if len(result["answer"]) > 300 else result["answer"])
        print("-"*80)
        print()
        
        # Should NOT have citations (security mode)
        if len(result["citations"]) == 0:
            print("[PASS] Security mode has no legal citations")
        else:
            print("[ERROR] Security mode should not have citations")
        
        # Should contain practical advice
        if any(word in result["answer"].lower() for word in ["firewall", "security", "network"]):
            print("[PASS] Contains security guidance")
        else:
            print("[ERROR] Missing security guidance")
        
        print()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print()


if __name__ == "__main__":
    print("\n")
    print("*"*80)
    print("SECURITY ADVISORY MODE - VERIFICATION TESTS")
    print("*"*80)
    print("\n")
    
    test_intent_routing()
    test_security_advisor()
    test_legal_mode_unchanged()
    test_end_to_end()
    
    print("\n")
    print("="*80)
    print("TESTING COMPLETE")
    print("="*80)
    print()
    print("Summary:")
    print("- Intent routing: Verifies SECURITY questions route correctly")
    print("- Security advisor: Verifies module works independently")
    print("- Legal mode: Verifies legal pipeline is unchanged")
    print("- End-to-end: Verifies full query flow")
    print()
    print("If all tests pass, the implementation is working correctly!")
    print()
