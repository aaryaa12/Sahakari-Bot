"""
Intent Router - Simple keyword-based question classification
No AI needed - fast and deterministic
"""

def detect_intent(question: str) -> str:
    """
    Classify question into one of four modes:
    - LEGAL: Law sections, penalties, regulations
    - SECURITY: Cybersecurity protection advice
    - COOP: Cooperative operational guidance
    - GENERAL: Normal conversation
    """
    q = question.lower()

    # PRIORITY 1: Check for explicit legal references (highest priority)
    explicit_legal = ["section", "chapter", "act", "penalty for", "fine for", 
                     "punishment for", "legal consequence", "regulation", "clause"]
    
    if any(k in q for k in explicit_legal):
        return "LEGAL"

    # PRIORITY 2: Security/protection questions (even with "insider", "risk", etc.)
    security_keywords = [
        "protect", "security", "secure", "firewall", "password", "attack",
        "hack", "breach", "malware", "network", "phishing",
        "encryption", "backup", "antivirus", "vulnerability",
        "cyber", "threat", "ransomware", "authentication",
        "mfa", "2fa", "vpn", "patch", "update", "insider risk",
        "insider threat", "data protection", "access control",
        "prevent", "safeguard", "defend", "monitor"
    ]
    
    if any(k in q for k in security_keywords):
        return "SECURITY"

    # PRIORITY 3: Specific legal terms that require legal interpretation
    legal_terms = ["bylaw", "byelaw", "statute", "provision", "legal requirement",
                   "legal obligation", "register", "registration", "compliance",
                   "authorized", "unauthorized", "prohibited", "liability", "violation"]
    
    if any(k in q for k in legal_terms):
        return "LEGAL"
    
    # PRIORITY 4: Cooperative operational guidance (general management)
    cooperative_keywords = [
        "member", "committee", "loan", "meeting", "audit",
        "board", "share", "dividend", "savings", "deposit",
        "transaction", "account", "ledger", "financial", "governance",
        "management", "cooperative", "election", "voting"
    ]
    
    if any(k in q for k in cooperative_keywords):
        return "COOP"
    
    # Default: General conversation
    return "GENERAL"
