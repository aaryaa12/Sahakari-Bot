"""
Legal Classifier Service
Classifies legal sections by type and scope using lightweight LLM classification
"""

from typing import Dict, Optional
import logging
import re
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from app.core.config import settings

logger = logging.getLogger(__name__)


class LegalClassifier:
    """Classifies legal text into types and scopes for structured retrieval."""
    
    def __init__(self):
        self.llm = None  # Lazy initialization
        self._base_url = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')
    
    def _get_llm(self):
        """Lazy initialization of Ollama LLM."""
        if self.llm is None:
            # Use fast, lightweight model for classification
            self.llm = ChatOllama(
                model="llama3.2:1b",  # Fastest model for classification
                temperature=0.0,  # Deterministic
                base_url=self._base_url,
                timeout=30.0
            )
        return self.llm
    
    def classify_section(
        self, 
        section_text: str, 
        section_number: str,
        section_title: str,
        act_name: str
    ) -> Dict[str, str]:
        """
        Classify a legal section by type and scope.
        
        Returns:
            {
                "legal_type": str,  # definition/obligation/permission/restriction/procedure/penalty/authority
                "legal_scope": str  # topic label (membership/governance/registration/etc.)
            }
        """
        # Quick rule-based classification first (for speed)
        rule_based = self._rule_based_classify(section_text, section_title, section_number, act_name)
        
        if rule_based["confidence"] == "high":
            return {
                "legal_type": rule_based["legal_type"],
                "legal_scope": rule_based["legal_scope"]
            }
        
        # Fall back to LLM classification for ambiguous cases
        try:
            llm_result = self._llm_classify(section_text, section_title, act_name)
            return llm_result
        except Exception as e:
            logger.warning(f"LLM classification failed for Section {section_number}: {e}")
            # Return rule-based result as fallback
            return {
                "legal_type": rule_based["legal_type"],
                "legal_scope": rule_based["legal_scope"]
            }
    
    def _rule_based_classify(
        self, 
        section_text: str,
        section_title: str,
        section_number: str,
        act_name: str
    ) -> Dict:
        """Fast rule-based classification using keywords."""
        text_lower = section_text.lower()
        title_lower = section_title.lower()
        combined = f"{title_lower} {text_lower[:500]}"  # First 500 chars
        
        # LEGAL TYPE DETECTION
        legal_type = "procedure"  # Default
        confidence = "medium"
        
        # Definition (highest priority)
        if any(keyword in title_lower for keyword in ['definition', 'meaning', 'interpretation']):
            legal_type = "definition"
            confidence = "high"
        
        # Penalty
        elif any(keyword in combined for keyword in [
            'penalty', 'fine', 'punishment', 'imprisonment', 'jail', 
            'offense', 'offence', 'liable to'
        ]):
            legal_type = "penalty"
            confidence = "high"
        
        # Obligation (must/shall/required)
        elif any(keyword in text_lower[:300] for keyword in [
            'shall ', 'must ', 'required to', 'obliged to', 'duty to',
            'responsible for', 'liable to provide'
        ]):
            legal_type = "obligation"
            confidence = "medium"
        
        # Permission (may/can/entitled)
        elif any(keyword in text_lower[:300] for keyword in [
            'may ', 'can ', 'entitled to', 'has the right', 'permitted to'
        ]):
            legal_type = "permission"
            confidence = "medium"
        
        # Restriction (shall not/prohibited/forbidden)
        elif any(keyword in text_lower[:300] for keyword in [
            'shall not', 'must not', 'prohibited', 'forbidden', 'restricted',
            'no person shall', 'not allowed'
        ]):
            legal_type = "restriction"
            confidence = "high"
        
        # Authority (power to/authority to)
        elif any(keyword in combined for keyword in [
            'authority to', 'power to', 'may approve', 'may reject',
            'controller may', 'registrar may', 'government may'
        ]):
            legal_type = "authority"
            confidence = "medium"
        
        # LEGAL SCOPE DETECTION
        legal_scope = "general"  # Default
        
        # Cooperative Act specific scopes
        if "cooperative" in act_name.lower():
            coop_scopes = {
                "registration": ["register", "registration", "formation"],
                "membership": ["member", "membership", "eligibility"],
                "governance": ["board", "committee", "meeting", "election", "bylaws", "byelaws"],
                "finance": ["fund", "capital", "share", "dividend", "deposit", "loan"],
                "audit": ["audit", "auditor", "financial statement", "accounting"],
                "dissolution": ["dissolution", "liquidation", "winding up"],
                "offence": ["offense", "offence", "penalty", "fine"]
            }
            
            for scope, keywords in coop_scopes.items():
                if any(kw in combined for kw in keywords):
                    legal_scope = scope
                    break
        
        # ETA specific scopes
        elif "electronic" in act_name.lower() or "eta" in act_name.lower():
            eta_scopes = {
                "digital_signature": ["digital signature", "signature", "certification"],
                "electronic_record": ["electronic record", "electronic document", "data message"],
                "authentication": ["authentication", "certifying authority", "controller"],
                "cybercrime": ["unauthorized access", "hacking", "cyber", "offense", "offence"],
                "data_protection": ["data", "information", "confidential", "privacy"],
                "compliance": ["compliance", "requirement", "standard"]
            }
            
            for scope, keywords in eta_scopes.items():
                if any(kw in combined for kw in keywords):
                    legal_scope = scope
                    break
        
        return {
            "legal_type": legal_type,
            "legal_scope": legal_scope,
            "confidence": confidence
        }
    
    def _llm_classify(
        self,
        section_text: str,
        section_title: str,
        act_name: str
    ) -> Dict:
        """LLM-based classification for ambiguous cases."""
        
        # Truncate text for efficiency
        truncated_text = section_text[:800]  # First 800 chars
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You classify legal sections. Respond ONLY with two words separated by a comma.

LEGAL TYPE (choose one): definition, obligation, permission, restriction, procedure, penalty, authority

LEGAL SCOPE (1-2 words): topic like "membership", "registration", "digital_signature", "authentication", "penalty", "governance", "finance", "audit", etc.

Format: legal_type, legal_scope

Example 1: "obligation, registration"
Example 2: "penalty, unauthorized_access"
Example 3: "definition, electronic_record"
"""),
            ("human", """Act: {act_name}
Section Title: {section_title}
Text: {section_text}

Classify:""")
        ])
        
        try:
            llm = self._get_llm()
            messages = prompt.format_messages(
                act_name=act_name,
                section_title=section_title,
                section_text=truncated_text
            )
            
            response = llm.invoke(messages)
            result = response.content.strip().lower()
            
            # Parse response
            parts = [p.strip() for p in result.split(',')]
            if len(parts) >= 2:
                legal_type = parts[0]
                legal_scope = parts[1]
                
                # Validate legal_type
                valid_types = ["definition", "obligation", "permission", "restriction", 
                             "procedure", "penalty", "authority"]
                if legal_type not in valid_types:
                    legal_type = "procedure"  # Default fallback
                
                return {
                    "legal_type": legal_type,
                    "legal_scope": legal_scope
                }
            else:
                raise ValueError(f"Invalid LLM response format: {result}")
        
        except Exception as e:
            logger.error(f"LLM classification error: {e}")
            # Fallback to rule-based
            rule_result = self._rule_based_classify(section_text, section_title, "", act_name)
            return {
                "legal_type": rule_result["legal_type"],
                "legal_scope": rule_result["legal_scope"]
            }


# Global classifier instance
legal_classifier = LegalClassifier()
