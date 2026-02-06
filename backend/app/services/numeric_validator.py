"""
Numeric Sanity Validator for Legal Penalties
Ensures written amounts match numeric amounts in legal text
"""

import re
from typing import Optional, Dict

# Nepali number words mapping
NEPALI_NUMBERS = {
    # Basic numbers
    "शून्य": 0, "एक": 1, "दुई": 2, "तीन": 3, "चार": 4, "पाँच": 5,
    "छ": 6, "सात": 7, "आठ": 8, "नौ": 9, "दश": 10,
    
    # Tens
    "बीस": 20, "तीस": 30, "चालीस": 40, "पचास": 50,
    "साठी": 60, "सत्तरी": 70, "अस्सी": 80, "नब्बे": 90,
    
    # Large numbers
    "सय": 100, "हजार": 1000, "लाख": 100000, "करोड": 10000000
}

# English number words mapping
ENGLISH_NUMBERS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
    "hundred": 100, "thousand": 1000, "lakh": 100000, "lakhs": 100000,
    "million": 1000000, "crore": 10000000, "crores": 10000000
}


def extract_numeric_amounts(text: str) -> Dict[str, list]:
    """
    Extract both written and numeric amounts from text.
    Returns dict with 'written' and 'numeric' lists.
    """
    # Pattern for written amounts (English)
    # e.g., "Two Hundred Thousand Rupees"
    written_pattern = r'(?:[Tt]wo|[Tt]hree|[Ff]our|[Ff]ive|[Ss]ix|[Ss]even|[Ee]ight|[Nn]ine|[Tt]en|[Ff]ifty|[Hh]undred|[Tt]housand|[Ll]akh|[Mm]illion|[Cc]rore)\s+(?:[Hh]undred|[Tt]housand|[Ll]akh|[Mm]illion|[Cc]rore)?\s*(?:[Rr]upees?|NPR|Rs\.?)?'
    
    # Pattern for numeric amounts
    # e.g., "200,000", "(NPR 200,000)", "Rs. 2,00,000"
    numeric_pattern = r'(?:NPR|Rs\.?|रु\.?)?\s*(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)'
    
    written_amounts = re.findall(written_pattern, text, re.IGNORECASE)
    numeric_matches = re.findall(numeric_pattern, text)
    
    # Clean numeric amounts (remove commas)
    numeric_amounts = [int(n.replace(',', '').split('.')[0]) for n in numeric_matches]
    
    return {
        "written": written_amounts,
        "numeric": numeric_amounts
    }


def parse_written_amount(text: str) -> Optional[int]:
    """
    Parse written amount to numeric value.
    e.g., "Two Hundred Thousand" -> 200000
    """
    text_lower = text.lower()
    
    # Try simple lookup first
    if text_lower in ENGLISH_NUMBERS:
        return ENGLISH_NUMBERS[text_lower]
    
    # Parse compound amounts (e.g., "two hundred thousand")
    words = text_lower.split()
    total = 0
    current = 0
    
    for word in words:
        if word in ["rupees", "rupee", "rs", "npr", "रु"]:
            continue
        
        if word in ENGLISH_NUMBERS:
            value = ENGLISH_NUMBERS[word]
            
            if value >= 100:
                # Multiplier word
                if current == 0:
                    current = 1
                current *= value
                if value >= 1000:
                    total += current
                    current = 0
            else:
                current += value
    
    return total + current if total + current > 0 else None


def validate_amounts(text: str) -> Dict:
    """
    Validate that written amounts match numeric amounts in text.
    Returns validation result with suggestions.
    """
    amounts = extract_numeric_amounts(text)
    
    if not amounts["written"] and not amounts["numeric"]:
        return {
            "valid": True,
            "reason": "No amounts found",
            "mismatches": []
        }
    
    if not amounts["written"]:
        return {
            "valid": True,
            "reason": "Only numeric amounts present",
            "numeric_amounts": amounts["numeric"]
        }
    
    if not amounts["numeric"]:
        return {
            "valid": True,
            "reason": "Only written amounts present",
            "written_amounts": amounts["written"]
        }
    
    # Check for mismatches
    mismatches = []
    
    for written in amounts["written"]:
        parsed = parse_written_amount(written)
        if parsed and parsed not in amounts["numeric"]:
            mismatches.append({
                "written": written,
                "parsed_value": parsed,
                "expected_numeric": amounts["numeric"]
            })
    
    if mismatches:
        return {
            "valid": False,
            "reason": "Written and numeric amounts do not match",
            "mismatches": mismatches,
            "suggestion": "Remove numeric parenthesis or verify amounts"
        }
    
    return {
        "valid": True,
        "reason": "Amounts match",
        "written": amounts["written"],
        "numeric": amounts["numeric"]
    }


def sanitize_penalty_response(response: str) -> str:
    """
    Clean up penalty response to avoid numeric mismatches.
    Removes numeric parentheses if they don't match written amounts.
    """
    validation = validate_amounts(response)
    
    if not validation["valid"]:
        # Remove numeric parentheses that don't match
        # Pattern: (NPR 2,000,000) or (Rs. 200,000)
        response = re.sub(r'\((?:NPR|Rs\.?|रु\.?)?\s*\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?\)', '', response)
        response = re.sub(r'\s+', ' ', response).strip()  # Clean up extra spaces
    
    return response


# Testing
if __name__ == "__main__":
    test_cases = [
        "Penalty of Two Hundred Thousand Rupees (NPR 200,000)",  # Valid
        "Penalty of Two Hundred Thousand Rupees (NPR 2,000,000)",  # Invalid - mismatch
        "Fine up to Rs. 50,000",  # Numeric only
        "Penalty of Five Lakh Rupees",  # Written only
        "Imprisonment for two years or fine up to Two Hundred Thousand (200,000)",  # Valid
    ]
    
    for test in test_cases:
        print(f"\nTest: {test}")
        result = validate_amounts(test)
        print(f"Valid: {result['valid']}")
        print(f"Reason: {result['reason']}")
        
        if not result["valid"]:
            sanitized = sanitize_penalty_response(test)
            print(f"Sanitized: {sanitized}")
