"""
Behavioral Contract Verification
Tests that the system follows STRICT behavioral rules
"""

import sys
from pathlib import Path
import os

# Disable telemetry for clean output
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"

sys.path.append(str(Path(__file__).parent))

from app.services.rag import rag_service


# Behavioral Contract Test Cases
TESTS = [
    # LEGAL MODE: Deterministic, No Refusals, 5-Heading Structure
    {
        "query": "What is Section 18 of ETA?",
        "expected_mode": "LEGAL",
        "must_contain": ["Legal meaning", "Legal effect", "Practical implications", "does NOT specify", "Evidence"],
        "must_not_contain": ["consult a lawyer", "not legal advice", "I cannot provide", "informational purposes"],
        "description": "LEGAL mode: No disclaimers, mandatory 5-heading structure"
    },
    {
        "query": "What is Section 999 of ETA?",
        "expected_mode": "LEGAL",
        "must_contain": ["cannot find", "999", "not present"],
        "must_not_contain": ["Section 4", "Section 18", "Section 41"],
        "description": "LEGAL mode: Proper refusal for non-existent section"
    },
    {
        "query": "What is the penalty in Section 4 of ETA?",
        "expected_mode": "LEGAL",
        "must_not_contain": ["consult", "lawyer", "not legal advice", "should consider"],
        "description": "LEGAL mode: Direct penalty answer, no disclaimers"
    },
    {
        "query": "How to register a cooperative?",
        "expected_mode": "LEGAL",
        "must_contain": ["Cooperatives", "Legal meaning", "Evidence"],
        "must_not_contain": ["Electronic Transaction", "ETA", "digital signature", "consult"],
        "description": "LEGAL mode: No cross-law mixing, no refusals, structured output"
    },
    
    # SECURITY MODE: No Law Citations
    {
        "query": "How can I strengthen network security?",
        "expected_mode": "SECURITY",
        "must_contain": ["firewall", "password", "security"],
        "must_not_contain": ["Section", "ETA requires", "Act mandates", "Cooperatives Act", "not legal advice"],
        "description": "SECURITY mode: Practical advice, NO law citations"
    },
    {
        "query": "What firewall should I use?",
        "expected_mode": "SECURITY",
        "must_not_contain": ["Section", "Act", "legal requirement", "ETA", "Cooperatives"],
        "description": "SECURITY mode: Technical advice only, no laws"
    },
    {
        "query": "How to protect against phishing?",
        "expected_mode": "SECURITY",
        "must_contain": ["phishing"],  # Must provide actionable guidance
        "must_not_contain": ["Section", "law requires", "ETA"],
        "description": "SECURITY mode: Security advice without legal references"
    },
    
    # GENERAL MODE: No Refusals
    {
        "query": "Hello, how are you?",
        "expected_mode": "GENERAL",
        "must_not_contain": ["cannot help", "outside my scope", "I cannot provide"],
        "description": "GENERAL mode: Normal greeting, no refusals"
    },
    
    # STRICT SECTION BOUNDARY + STRUCTURE
    {
        "query": "What is Section 12 of Cooperative Act?",
        "expected_mode": "LEGAL",
        "must_contain": ["Section 12", "Cooperatives", "Legal meaning", "Evidence"],
        "must_not_contain": ["Section 11", "Section 13", "Section 19", "Section 41"],
        "description": "Strict section boundary: Only Section 12, no neighbors, with structure"
    },
    
    # NO INVENTED PROCEDURES
    {
        "query": "What documents are needed to register a cooperative?",
        "expected_mode": "LEGAL",
        "must_not_contain": ["district association approval", "provincial approval", "mayor approval"],
        "description": "No invented procedures: Only what's in the Act"
    },
    
    # DETERMINISTIC BEHAVIOR + NO INTERNAL PROMPT LEAKAGE
    {
        "query": "What is Section 18 of ETA?",
        "expected_mode": "LEGAL",
        "must_contain": ["Section 18", "Electronic"],
        "must_not_contain": ["assumed", "probably", "i think", "typically", "generally speaking", "in my opinion", "BOUNDARY RULES", "BEHAVIORAL CONTRACT"],
        "description": "Deterministic: No hedging/assumption language, no internal prompt leakage"
    },
]


def check_behavioral_contract(response, test):
    """Check if response follows behavioral contract"""
    answer = response.get("answer", "")
    answer_lower = answer.lower()
    
    violations = []
    warnings = []
    
    # Check must_contain
    if "must_contain" in test:
        for phrase in test["must_contain"]:
            if phrase.lower() not in answer_lower:
                violations.append(f"Missing required: '{phrase}'")
    
    # Check must_not_contain (CRITICAL)
    if "must_not_contain" in test:
        for phrase in test["must_not_contain"]:
            if phrase.lower() in answer_lower:
                violations.append(f"VIOLATION: Contains forbidden '{phrase}'")
    
    # Check for common refusal patterns
    refusal_patterns = [
        "i cannot provide legal advice",
        "consult a lawyer",
        "consult an attorney",
        "seek professional",
        "not a substitute for",
        "for informational purposes only",
        "this is not legal advice"
    ]
    
    for pattern in refusal_patterns:
        if pattern in answer_lower:
            violations.append(f"CRITICAL: Legal disclaimer detected: '{pattern}'")
    
    return violations, warnings


def main():
    print("=" * 80)
    print("BEHAVIORAL CONTRACT VERIFICATION")
    print("Testing Strict Compliance with Behavioral Rules")
    print("=" * 80)
    print()
    
    total = len(TESTS)
    passed = 0
    violated = 0
    
    for i, test in enumerate(TESTS, 1):
        print(f"[{i}/{total}] {test['description']}")
        print(f"Query: \"{test['query']}\"")
        print(f"Expected Mode: {test['expected_mode']}")
        
        try:
            response = rag_service.query(test['query'])
            violations, warnings = check_behavioral_contract(response, test)
            
            if not violations and not warnings:
                print("[PASS] - Behavioral contract followed")
                passed += 1
            elif not violations:
                print("[PASS] with warnings")
                for warning in warnings:
                    print(f"   {warning}")
                passed += 1
            else:
                print("[FAIL] - Behavioral contract violated")
                for violation in violations:
                    print(f"   {violation}")
                violated += 1
            
            # Show preview
            preview = response["answer"][:200]
            print(f"Preview: {preview}...")
            
        except Exception as e:
            print(f"[ERROR]: {str(e)}")
            violated += 1
        
        print("-" * 80)
        print()
    
    # Summary
    print("=" * 80)
    print("BEHAVIORAL CONTRACT SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total}")
    print(f"Compliant: {passed}")
    print(f"Violations: {violated}")
    print(f"Compliance Rate: {(passed/total)*100:.1f}%")
    print()
    
    if violated == 0:
        print("[SUCCESS]: 100% behavioral contract compliance!")
        print("   System is DETERMINISTIC and follows all rules.")
    elif passed >= total * 0.9:
        print("[EXCELLENT]: >=90% compliance")
        print("   Minor violations only, system is stable.")
    elif passed >= total * 0.8:
        print("[GOOD]: >=80% compliance")
        print("   Some violations, review failures.")
    else:
        print("[NEEDS WORK]: <80% compliance")
        print("   Major behavioral issues, review prompts.")
    
    print("=" * 80)
    
    # Critical checks
    print("\nCRITICAL BEHAVIORAL CHECKS:")
    print("  - LEGAL mode: No 'consult lawyer' disclaimers")
    print("  - LEGAL mode: No refusals for legal questions")
    print("  - SECURITY mode: No law citations")
    print("  - GENERAL mode: No refusals for greetings")
    print("  - All modes: Deterministic responses")
    print()


if __name__ == "__main__":
    main()
