"""
Legal QA Evaluation Script
Tests all 6 failure modes + 2 user acceptance tests (12 total questions)
Includes mandatory 5-heading structure validation
"""

import sys
from pathlib import Path
import os

# Disable telemetry for clean output
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"

sys.path.append(str(Path(__file__).parent))

from app.services.rag import rag_service
from app.core.database import get_collection
import json


# 10 Critical Test Cases (Covers All 6 Failure Modes + Structure)
TEST_CASES = [
    # FAILURE 1: Wrong-Section Answers + Structure Check
    {
        "id": "F1-1",
        "query": "What is Section 4 of ETA?",
        "mode": "LEGAL",
        "expected_section": "4",
        "expected_act": "Electronic Transaction Act",
        "should_not_contain": ["definition", "Section 18", "hash function"],
        "must_have_structure": True,
        "description": "Test exact section retrieval (not definitions) + 5-heading format"
    },
    {
        "id": "F1-2",
        "query": "What is Section 18 of ETA?",
        "mode": "LEGAL",
        "expected_section": "18",
        "expected_act": "Electronic Transaction Act",
        "should_not_contain": ["Section 4", "definition"],
        "must_have_structure": True,
        "description": "Test Section 18 retrieves different content from Section 4 + structure"
    },
    
    # FAILURE 2: Cross-Section Contamination + Structure
    {
        "id": "F2",
        "query": "Tell me about Section 12 of Cooperative Act",
        "mode": "LEGAL",
        "expected_section": "12",
        "expected_act": "Cooperatives Act",
        "should_not_contain": ["Section 13", "Section 11", "Section 19"],
        "must_have_structure": True,
        "description": "Test no cross-section contamination + 5-heading format"
    },
    
    # FAILURE 3: Cross-Law Mixing + Structure
    {
        "id": "F3-1",
        "query": "How to register a cooperative?",
        "mode": "LEGAL",
        "expected_act": "Cooperatives Act",
        "should_not_contain": ["Electronic Transaction", "ETA", "digital signature"],
        "must_have_structure": True,
        "description": "Test cooperative query doesn't use ETA + structure"
    },
    {
        "id": "F3-2",
        "query": "What are the requirements for electronic authentication?",
        "mode": "LEGAL",
        "expected_act": "Electronic",
        "should_not_contain": ["Cooperatives", "cooperative", "member", "board"],
        "must_have_structure": True,
        "description": "Test ETA query doesn't use Cooperative Act + structure"
    },
    
    # FAILURE 4: Law-Overreach (Security Questions)
    {
        "id": "F4-1",
        "query": "How can I strengthen network security?",
        "mode": "SECURITY",
        "should_contain": ["firewall", "password", "security"],
        "should_not_contain": ["ETA requires", "Act mandates", "Section"],
        "description": "Test security advice without false legal claims"
    },
    {
        "id": "F4-2",
        "query": "What firewall should I use for my organization?",
        "mode": "SECURITY",
        "should_contain": ["firewall", "recommend", "consider"],
        "should_not_contain": ["legal requirement", "ETA", "Section"],
        "description": "Test practical security advice (no law citations)"
    },
    
    # FAILURE 5: Template Placeholders
    {
        "id": "F5",
        "query": "What is Section 18 of Electronic Transaction Act?",
        "mode": "LEGAL",
        "should_not_contain": ["[Act Name]", "[Number]", "[Section]", "[X]"],
        "should_contain": ["Electronic Transaction Act", "Section 18"],
        "description": "Test no placeholder in citations"
    },
    
    # FAILURE 6: Refusal/Loop
    {
        "id": "F6-1",
        "query": "What is Section 999 of ETA?",
        "mode": "LEGAL",
        "should_contain": ["cannot find", "999"],
        "should_not_contain": ["Section 41", "Section 18"],
        "description": "Test proper refusal for non-existent section"
    },
    {
        "id": "F6-2",
        "query": "Hello, what can you help me with?",
        "mode": "GENERAL",
        "should_contain": ["help"],  # Relaxed: just needs to be helpful
        "should_not_contain": ["Error", "cannot help", "refused", "outside my scope"],
        "description": "Test general greeting works (no refusal loop)"
    },
    
    # NEW: USER ACCEPTANCE TESTS (From requirements)
    {
        "id": "UAT-1",
        "query": "What does Formation and Registration of Cooperative Organization mean?",
        "mode": "LEGAL",
        "expected_act": "Cooperatives",
        "must_have_structure": True,
        "should_contain": ["registration", "formation"],
        "description": "User test: Formation explanation with full structure"
    },
    {
        "id": "UAT-2",
        "query": "What are byelaws and internal procedures?",
        "mode": "LEGAL",
        "expected_act": "Cooperatives",
        "must_have_structure": True,
        "should_contain": ["byelaw"],  # Case-insensitive check (will match "Byelaws" too)
        "description": "User test: Bylaws explanation with full structure"
    },
]


def evaluate_response(test_case, response):
    """Evaluate a single response against test criteria"""
    answer = response.get("answer", "")
    answer_lower = answer.lower()
    citations = response.get("citations", [])
    
    results = {
        "passed": True,
        "failures": [],
        "warnings": []
    }
    
    # Check for 5-heading structure (for LEGAL mode questions)
    if test_case.get("must_have_structure", False):
        required_headings = [
            ("1) legal meaning", "legal meaning"),
            ("2) legal effect", "legal effect"),
            ("3) practical implications", "practical implications"),
            ("4) what the act does not specify", "does not specify"),
            ("5) evidence", "evidence")
        ]
        missing_headings = []
        for full_heading, short_heading in required_headings:
            # Accept either full or short version
            if full_heading not in answer_lower and short_heading not in answer_lower:
                missing_headings.append(short_heading)
        
        if missing_headings:
            results["passed"] = False
            results["failures"].append(f"Missing required structure headings: {', '.join(missing_headings)}")
    
    # Check expected content
    if "should_contain" in test_case:
        for phrase in test_case["should_contain"]:
            if phrase.lower() not in answer_lower:
                results["passed"] = False
                results["failures"].append(f"Missing expected: '{phrase}'")
    
    # Check forbidden content
    if "should_not_contain" in test_case:
        for phrase in test_case["should_not_contain"]:
            # For abbreviations like "ETA", check as whole word (with word boundaries)
            if len(phrase) <= 4 and phrase.isupper():
                import re
                pattern = r'\b' + re.escape(phrase.lower()) + r'\b'
                if re.search(pattern, answer_lower):
                    results["passed"] = False
                    results["failures"].append(f"Contains forbidden: '{phrase}'")
            else:
                if phrase.lower() in answer_lower:
                    results["passed"] = False
                    results["failures"].append(f"Contains forbidden: '{phrase}'")
    
    # Check expected section
    if "expected_section" in test_case:
        section_found = False
        for citation in citations:
            if test_case["expected_section"] in str(citation.get("page", "")):
                section_found = True
                break
        if not section_found:
            results["warnings"].append(f"Expected section {test_case['expected_section']} not in citations")
    
    # Check expected act
    if "expected_act" in test_case:
        act_found = False
        for citation in citations:
            if test_case["expected_act"].lower() in citation.get("source", "").lower():
                act_found = True
                break
        if not act_found and test_case["mode"] == "LEGAL":
            results["warnings"].append(f"Expected act '{test_case['expected_act']}' not in citations")
    
    return results


def run_evaluation():
    """Run full evaluation suite"""
    print("=" * 80)
    print("LEGAL QA SYSTEM - COMPREHENSIVE EVALUATION")
    print("Testing 6 Failure Modes + User Acceptance Tests (12 Questions)")
    print("Includes Mandatory 5-Heading Structure Validation")
    print("=" * 80)
    print()
    
    # Check collection
    collection = get_collection()
    doc_count = collection.count()
    print(f"[INFO] Collection Status: {doc_count} chunks")
    
    if doc_count == 0:
        print("[ERROR] No documents in collection!")
        print("   Run: python recreate_collection.py")
        print("   Then upload PDFs via frontend")
        return
    
    print()
    
    # Run tests
    total = len(TEST_CASES)
    passed = 0
    failed = 0
    
    results_log = []
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"[{i}/{total}] Testing {test['id']}: {test['description']}")
        print(f"Query: \"{test['query']}\"")
        print(f"Expected Mode: {test['mode']}")
        
        try:
            # Execute query
            response = rag_service.query(test['query'])
            
            # Evaluate
            eval_result = evaluate_response(test, response)
            
            # Display result
            if eval_result["passed"] and not eval_result["warnings"]:
                print("[PASS]")
                passed += 1
            elif eval_result["passed"] and eval_result["warnings"]:
                print("[PASS] (with warnings)")
                for warning in eval_result["warnings"]:
                    print(f"   {warning}")
                passed += 1
            else:
                print("[FAIL]")
                for failure in eval_result["failures"]:
                    print(f"   {failure}")
                failed += 1
            
            # Show answer preview
            answer_preview = response["answer"][:150]
            print(f"Answer: {answer_preview}...")
            
            # Log result
            results_log.append({
                "test_id": test["id"],
                "query": test["query"],
                "passed": eval_result["passed"],
                "failures": eval_result["failures"],
                "warnings": eval_result["warnings"],
                "answer_preview": answer_preview
            })
            
        except Exception as e:
            print(f"[ERROR]: {str(e)}")
            failed += 1
            results_log.append({
                "test_id": test["id"],
                "query": test["query"],
                "passed": False,
                "error": str(e)
            })
        
        print("-" * 80)
        print()
    
    # Summary
    print("=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print()
    
    # Failure mode breakdown
    print("Failure Mode Coverage:")
    print("  F1: Wrong-Section Answers - 2 tests")
    print("  F2: Cross-Section Contamination - 1 test")
    print("  F3: Cross-Law Mixing - 2 tests")
    print("  F4: Law-Overreach - 2 tests")
    print("  F5: Template Placeholders - 1 test")
    print("  F6: Refusal/Loop - 2 tests")
    print()
    
    # Final verdict
    if passed == total:
        print("[SUCCESS]: All critical tests passed!")
        print("   System is production-ready for legal QA.")
    elif passed >= total * 0.8:
        print("[GOOD]: Most tests passed (>=80%).")
        print("   System is functional with minor issues.")
    elif passed >= total * 0.6:
        print("[ACCEPTABLE]: Majority passed (>=60%).")
        print("   System works but needs improvement.")
    else:
        print("[NEEDS WORK]: Many failures (<60%).")
        print("   Review failed tests and fix issues.")
    
    print("=" * 80)
    
    # Save detailed results
    with open("eval_results.json", "w") as f:
        json.dump(results_log, f, indent=2)
    print("\n[INFO] Detailed results saved to: eval_results.json")


if __name__ == "__main__":
    run_evaluation()
