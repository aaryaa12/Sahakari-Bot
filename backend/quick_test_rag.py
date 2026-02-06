"""
Quick RAG Pipeline Test Script
Tests all modes with sample questions
"""

import sys
import time
from app.services.rag import rag_service
from app.services.intent_router import detect_intent

def print_separator():
    print("\n" + "="*80 + "\n")

def print_response(question, response, intent):
    print(f"QUESTION: {question}")
    print(f"DETECTED INTENT: {intent}")
    print(f"\nRESPONSE:")
    print("-" * 80)
    
    # Print first 500 characters of answer
    answer = response.get("answer", "No answer")
    if len(answer) > 500:
        print(answer[:500] + "...\n[Response truncated for readability]")
    else:
        print(answer)
    
    print("-" * 80)
    print(f"Citations: {len(response.get('citations', []))}")
    print(f"Sources: {response.get('sources_count', 0)}")
    
    # Check for framework references in security mode
    if intent == "SECURITY":
        has_framework_refs = any(word in answer for word in ["NIST", "ISO 27001", "PR.AC", "A.9", "A.12"])
        print(f"Framework References: {'YES' if has_framework_refs else 'NO'}")
    
    # Check for legal format in legal mode
    if intent == "LEGAL":
        has_legal_format = "Legal meaning" in answer and "Evidence" in answer
        print(f"5-Heading Format: {'YES' if has_legal_format else 'NO'}")
    
    print_separator()

def test_questions():
    """Test all RAG modes with sample questions."""
    
    # Test questions organized by mode
    test_cases = [
        # LEGAL MODE - Cooperative Act
        {
            "mode": "LEGAL MODE - Cooperative Act",
            "questions": [
                "What does Formation and Registration of Cooperative Organization mean?",
                "What are byelaws and internal procedures?",
                "What happens if unauthorized loans are given?",
            ]
        },
        
        # LEGAL MODE - Electronic Transaction Act
        {
            "mode": "LEGAL MODE - Electronic Transaction Act",
            "questions": [
                "What is Section 4 of ETA?",
                "What is Section 18 of ETA?",
                "What are the penalties for unauthorized access?",
            ]
        },
        
        # SECURITY MODE
        {
            "mode": "SECURITY MODE",
            "questions": [
                "How can I protect my cooperative from insider risks?",
                "What firewall should I use for my cooperative?",
                "How to protect against phishing attacks?",
            ]
        },
        
        # COOP MODE
        {
            "mode": "COOP MODE",
            "questions": [
                "How to conduct board meetings?",
            ]
        },
        
        # GENERAL MODE
        {
            "mode": "GENERAL MODE",
            "questions": [
                "Hello, how are you?",
            ]
        }
    ]
    
    print("\n")
    print("*" * 80)
    print("RAG PIPELINE - QUICK TEST")
    print("*" * 80)
    print()
    
    total_questions = sum(len(tc["questions"]) for tc in test_cases)
    current_question = 0
    
    for test_case in test_cases:
        print("\n" + "#" * 80)
        print(f"# {test_case['mode']}")
        print("#" * 80)
        print()
        
        for question in test_case["questions"]:
            current_question += 1
            print(f"\n[{current_question}/{total_questions}]")
            
            # Detect intent
            intent = detect_intent(question)
            
            # Query RAG
            start_time = time.time()
            try:
                response = rag_service.query(question)
                elapsed = time.time() - start_time
                
                print_response(question, response, intent)
                print(f"Response time: {elapsed:.2f}s")
                
            except Exception as e:
                print(f"ERROR: {str(e)}")
                print_separator()
            
            # Small delay between queries
            time.sleep(0.5)
    
    print("\n" + "*" * 80)
    print("TESTING COMPLETE")
    print("*" * 80)
    print(f"\nTotal questions tested: {total_questions}")
    print("\nReview the responses above to verify:")
    print("  - Correct intent routing")
    print("  - Appropriate format (5-heading for legal, framework IDs for security)")
    print("  - No cross-contamination (legal vs security citations)")
    print()

def test_single_question():
    """Test a single custom question."""
    
    if len(sys.argv) < 2:
        print("\nUsage: python quick_test_rag.py \"Your question here\"")
        print("   Or: python quick_test_rag.py  (to run full test suite)\n")
        return
    
    question = " ".join(sys.argv[1:])
    
    print("\n" + "*" * 80)
    print("RAG PIPELINE - SINGLE QUESTION TEST")
    print("*" * 80)
    print()
    
    # Detect intent
    intent = detect_intent(question)
    
    # Query RAG
    start_time = time.time()
    try:
        response = rag_service.query(question)
        elapsed = time.time() - start_time
        
        print_response(question, response, intent)
        print(f"Response time: {elapsed:.2f}s")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
    
    print()

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            # Single question mode
            test_single_question()
        else:
            # Full test suite
            test_questions()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\nFATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
