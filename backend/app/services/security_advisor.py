"""
Security Advisory Module
Provides cybersecurity and risk management guidance WITHOUT using legal RAG pipeline
Completely separate from legal document interpretation

Includes international security framework controls (NIST, ISO 27001)
Stored as structured knowledge base - NOT in vector database
"""

from typing import Dict, List, Optional, Any
import logging
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from app.core.config import settings

logger = logging.getLogger(__name__)


# ============================================================================
# SECURITY CONTROLS KNOWLEDGE BASE
# International frameworks (NIST CSF, ISO 27001) - separate from legal docs
# ============================================================================

SECURITY_CONTROLS = [
    # ===== ACCESS CONTROL =====
    {
        "framework": "NIST CSF",
        "control_id": "PR.AC-4",
        "control_name": "Access Permissions and Authorizations",
        "purpose": "Manage access permissions based on least privilege and separation of duties",
        "recommendation_text": "Implement role-based access control (RBAC) with least privilege principle. Review and update access permissions quarterly. Require approval for privileged access."
    },
    {
        "framework": "ISO 27001",
        "control_id": "A.9.2.3",
        "control_name": "Management of Privileged Access Rights",
        "purpose": "Restrict and control privileged access rights",
        "recommendation_text": "Allocate privileged access rights on a need-to-use basis. Implement approval process for privileged access. Review privileged accounts regularly."
    },
    {
        "framework": "NIST CSF",
        "control_id": "PR.AC-1",
        "control_name": "Identity and Access Management",
        "purpose": "Manage identities and credentials for authorized devices, users, and processes",
        "recommendation_text": "Use unique user IDs for each person. Implement strong password policies (12+ characters, complexity). Disable inactive accounts after 90 days."
    },
    {
        "framework": "ISO 27001",
        "control_id": "A.9.4.2",
        "control_name": "Secure Log-on Procedures",
        "purpose": "Protect against unauthorized access through secure authentication",
        "recommendation_text": "Implement multi-factor authentication (MFA) for all remote access and privileged accounts. Use session timeouts (15 minutes inactivity)."
    },
    
    # ===== LOGGING & MONITORING =====
    {
        "framework": "NIST CSF",
        "control_id": "DE.CM-1",
        "control_name": "Network Monitoring",
        "purpose": "Monitor networks to detect potential cybersecurity events",
        "recommendation_text": "Enable logging on all critical systems. Monitor for suspicious activities (failed login attempts, privilege escalation, unusual data access). Review logs weekly."
    },
    {
        "framework": "ISO 27001",
        "control_id": "A.12.4.1",
        "control_name": "Event Logging",
        "purpose": "Record events and generate evidence",
        "recommendation_text": "Log user activities, exceptions, faults, and security events. Include: user ID, date/time, type of event, success/failure. Retain logs for at least 90 days."
    },
    {
        "framework": "NIST CSF",
        "control_id": "DE.AE-3",
        "control_name": "Event Data Analysis",
        "purpose": "Aggregate and analyze event data to identify anomalies",
        "recommendation_text": "Implement Security Information and Event Management (SIEM) or centralized log analysis. Set up alerts for critical events (admin access, financial transactions >$10K)."
    },
    
    # ===== SEGREGATION OF DUTIES =====
    {
        "framework": "ISO 27001",
        "control_id": "A.6.1.2",
        "control_name": "Segregation of Duties",
        "purpose": "Reduce opportunities for unauthorized or unintentional modification",
        "recommendation_text": "Separate duties for transaction initiation, approval, and recording. Implement maker-checker controls for financial transactions. No single person should control entire process."
    },
    {
        "framework": "NIST CSF",
        "control_id": "PR.AC-5",
        "control_name": "Network Segregation",
        "purpose": "Protect assets through network segmentation",
        "recommendation_text": "Segment financial systems from general network. Use VLANs or firewalls to separate critical systems. Restrict access between segments."
    },
    
    # ===== AWARENESS TRAINING =====
    {
        "framework": "NIST CSF",
        "control_id": "PR.AT-1",
        "control_name": "Security Awareness Training",
        "purpose": "Ensure users are informed and trained on security awareness",
        "recommendation_text": "Conduct security awareness training annually for all staff. Include: phishing recognition, password security, social engineering, incident reporting. Test with simulated phishing campaigns quarterly."
    },
    {
        "framework": "ISO 27001",
        "control_id": "A.7.2.2",
        "control_name": "Information Security Awareness",
        "purpose": "Ensure employees are aware of security responsibilities",
        "recommendation_text": "Provide security awareness training during onboarding and annually. Cover: acceptable use, clean desk policy, incident reporting procedures, data classification."
    },
    
    # ===== EMAIL SECURITY =====
    {
        "framework": "NIST CSF",
        "control_id": "PR.PT-4",
        "control_name": "Communications and Control Networks",
        "purpose": "Protect the confidentiality and integrity of communications",
        "recommendation_text": "Implement email filtering (anti-spam, anti-malware). Block suspicious attachments (.exe, .zip from external sources). Use email authentication (SPF, DKIM, DMARC)."
    },
    
    # ===== FIREWALL & NETWORK SECURITY =====
    {
        "framework": "NIST CSF",
        "control_id": "PR.AC-3",
        "control_name": "Remote Access Management",
        "purpose": "Manage remote access to information systems",
        "recommendation_text": "Require VPN for all remote access. Implement firewall rules to allow only necessary traffic. Use next-generation firewall with IPS/IDS capabilities."
    },
    {
        "framework": "ISO 27001",
        "control_id": "A.13.1.3",
        "control_name": "Segregation in Networks",
        "purpose": "Segregate information services, users, and information systems",
        "recommendation_text": "Deploy perimeter firewall and internal firewalls. Configure default-deny rules. Implement DMZ for public-facing services. Review firewall rules quarterly."
    },
    
    # ===== PATCH MANAGEMENT =====
    {
        "framework": "NIST CSF",
        "control_id": "PR.IP-12",
        "control_name": "Vulnerability Management",
        "purpose": "Manage vulnerabilities in information systems",
        "recommendation_text": "Apply security patches within 30 days of release (critical patches within 7 days). Maintain inventory of all systems and software. Scan for vulnerabilities monthly."
    },
    {
        "framework": "ISO 27001",
        "control_id": "A.12.6.1",
        "control_name": "Management of Technical Vulnerabilities",
        "purpose": "Prevent exploitation of technical vulnerabilities",
        "recommendation_text": "Subscribe to security advisories. Test patches in non-production environment. Schedule maintenance windows for patch deployment. Document patching activities."
    },
    
    # ===== ENCRYPTION & DATA PROTECTION =====
    {
        "framework": "NIST CSF",
        "control_id": "PR.DS-1",
        "control_name": "Data at Rest Protection",
        "purpose": "Protect data at rest using encryption",
        "recommendation_text": "Encrypt sensitive data at rest (AES-256). Encrypt database files, backups, and removable media. Use full-disk encryption for laptops. Manage encryption keys securely."
    },
    {
        "framework": "ISO 27001",
        "control_id": "A.10.1.1",
        "control_name": "Cryptographic Controls",
        "purpose": "Ensure proper use of cryptography to protect information",
        "recommendation_text": "Use strong encryption algorithms (AES-256, RSA-2048+). Encrypt data in transit (TLS 1.2+). Implement key management procedures. Rotate encryption keys annually."
    },
    {
        "framework": "NIST CSF",
        "control_id": "PR.DS-2",
        "control_name": "Data in Transit Protection",
        "purpose": "Protect data in transit using encryption",
        "recommendation_text": "Use TLS 1.2 or higher for all web traffic. Encrypt email containing sensitive information. Use VPN for remote access. Disable insecure protocols (SSLv3, TLS 1.0)."
    },
    
    # ===== BACKUP & RECOVERY =====
    {
        "framework": "NIST CSF",
        "control_id": "PR.IP-4",
        "control_name": "Backup and Recovery",
        "purpose": "Ensure backups are created and tested regularly",
        "recommendation_text": "Perform daily incremental backups and weekly full backups. Store backups offsite or in cloud. Test backup restoration quarterly. Encrypt backup data. Follow 3-2-1 rule (3 copies, 2 media types, 1 offsite)."
    },
    {
        "framework": "ISO 27001",
        "control_id": "A.12.3.1",
        "control_name": "Information Backup",
        "purpose": "Protect against loss of data",
        "recommendation_text": "Define backup requirements for each system. Automate backup processes. Verify backup integrity monthly. Document recovery time objectives (RTO) and recovery point objectives (RPO)."
    },
    
    # ===== ACCESS RESTRICTION =====
    {
        "framework": "ISO 27001",
        "control_id": "A.9.1.2",
        "control_name": "Access to Networks and Services",
        "purpose": "Ensure users only have access to authorized networks and services",
        "recommendation_text": "Implement network access control (NAC). Authenticate devices before allowing network access. Use 802.1X for wired/wireless networks. Segment guest network from corporate network."
    },
    
    # ===== INCIDENT RESPONSE =====
    {
        "framework": "NIST CSF",
        "control_id": "RS.RP-1",
        "control_name": "Response Plan",
        "purpose": "Execute response plans during or after a cybersecurity incident",
        "recommendation_text": "Develop incident response plan with defined roles and procedures. Establish incident response team. Conduct tabletop exercises annually. Include communication plan and escalation procedures."
    },
    {
        "framework": "ISO 27001",
        "control_id": "A.16.1.5",
        "control_name": "Response to Information Security Incidents",
        "purpose": "Respond to information security incidents",
        "recommendation_text": "Define incident severity levels. Establish reporting procedures (who, when, how). Document incident handling procedures. Conduct post-incident reviews to identify improvements."
    },
    
    # ===== BACKGROUND CHECKS =====
    {
        "framework": "ISO 27001",
        "control_id": "A.7.1.1",
        "control_name": "Screening",
        "purpose": "Verify backgrounds of candidates for employment",
        "recommendation_text": "Conduct background checks for positions with access to sensitive data or financial systems. Verify employment history, education, and references. Check criminal records where legally permitted. Document verification process."
    },
]


# ============================================================================
# TOPIC TO CONTROLS MAPPING
# Maps security topics to relevant framework controls
# ============================================================================

TOPIC_CONTROLS_MAP = {
    "insider_threat": [
        "PR.AC-4", "A.9.2.3", "PR.AC-1", "DE.CM-1", "A.12.4.1", "A.6.1.2", "A.7.1.1"
    ],
    "insider_risk": [
        "PR.AC-4", "A.9.2.3", "PR.AC-1", "DE.CM-1", "A.12.4.1", "A.6.1.2", "A.7.1.1"
    ],
    "access_control": [
        "PR.AC-4", "A.9.2.3", "PR.AC-1", "A.9.4.2", "A.9.1.2"
    ],
    "phishing": [
        "PR.AT-1", "A.7.2.2", "PR.PT-4", "A.9.4.2"
    ],
    "email_security": [
        "PR.PT-4", "PR.AT-1", "A.7.2.2"
    ],
    "network_security": [
        "PR.AC-3", "A.13.1.3", "PR.IP-12", "A.12.6.1", "DE.CM-1"
    ],
    "firewall": [
        "PR.AC-3", "A.13.1.3", "PR.AC-5"
    ],
    "patch_management": [
        "PR.IP-12", "A.12.6.1"
    ],
    "vulnerability": [
        "PR.IP-12", "A.12.6.1"
    ],
    "data_protection": [
        "PR.DS-1", "A.10.1.1", "PR.DS-2", "A.9.1.2"
    ],
    "encryption": [
        "PR.DS-1", "A.10.1.1", "PR.DS-2"
    ],
    "backup": [
        "PR.IP-4", "A.12.3.1"
    ],
    "disaster_recovery": [
        "PR.IP-4", "A.12.3.1"
    ],
    "monitoring": [
        "DE.CM-1", "A.12.4.1", "DE.AE-3"
    ],
    "logging": [
        "DE.CM-1", "A.12.4.1"
    ],
    "awareness_training": [
        "PR.AT-1", "A.7.2.2"
    ],
    "security_training": [
        "PR.AT-1", "A.7.2.2"
    ],
    "incident_response": [
        "RS.RP-1", "A.16.1.5"
    ],
    "segregation_of_duties": [
        "A.6.1.2", "PR.AC-5"
    ],
    "mfa": [
        "A.9.4.2", "PR.AC-1"
    ],
    "authentication": [
        "A.9.4.2", "PR.AC-1", "PR.AC-3"
    ],
    "background_check": [
        "A.7.1.1"
    ],
}


class SecurityAdvisor:
    """
    Provides security and risk management advisory responses.
    Does NOT use legal documents or RAG pipeline.
    Uses international security framework controls (NIST, ISO 27001).
    """
    
    def __init__(self):
        self.llm = None  # Lazy initialization
        self._base_url = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')
        self.controls = SECURITY_CONTROLS
        self.topic_map = TOPIC_CONTROLS_MAP
    
    def _get_llm(self):
        """Lazy initialization of Ollama LLM."""
        if self.llm is None:
            from app.services.rag import rag_service
            self.llm = rag_service._get_llm()  # Reuse RAG service's LLM initialization
        return self.llm
    
    def _detect_topics(self, query: str) -> List[str]:
        """
        Detect security topics in the query.
        
        Returns:
            List of topic keys from TOPIC_CONTROLS_MAP
        """
        query_lower = query.lower()
        detected_topics = []
        
        # Check each topic in the map
        for topic in self.topic_map.keys():
            # Convert underscores to spaces for matching
            topic_phrase = topic.replace("_", " ")
            
            if topic_phrase in query_lower:
                detected_topics.append(topic)
        
        # If no specific topics detected, infer from general keywords
        if not detected_topics:
            if any(word in query_lower for word in ["insider", "internal threat", "employee risk"]):
                detected_topics.append("insider_risk")
            
            if any(word in query_lower for word in ["phish", "email attack", "spam"]):
                detected_topics.append("phishing")
            
            if any(word in query_lower for word in ["firewall", "network protect", "perimeter"]):
                detected_topics.append("network_security")
            
            if any(word in query_lower for word in ["encrypt", "data security", "sensitive data"]):
                detected_topics.append("data_protection")
            
            if any(word in query_lower for word in ["backup", "restore", "recovery"]):
                detected_topics.append("backup")
            
            if any(word in query_lower for word in ["train", "awareness", "educate"]):
                detected_topics.append("awareness_training")
            
            if any(word in query_lower for word in ["monitor", "log", "detect"]):
                detected_topics.append("monitoring")
            
            if any(word in query_lower for word in ["access", "permission", "privilege"]):
                detected_topics.append("access_control")
        
        return detected_topics if detected_topics else ["general_security"]
    
    def _select_controls(self, topics: List[str]) -> List[Dict]:
        """
        Select relevant controls based on detected topics.
        
        Returns:
            List of control dictionaries
        """
        control_ids = set()
        
        # Collect all control IDs for detected topics
        for topic in topics:
            if topic in self.topic_map:
                control_ids.update(self.topic_map[topic])
        
        # If no specific controls, return top general controls
        if not control_ids:
            control_ids = {"PR.AC-1", "A.9.2.3", "DE.CM-1", "PR.AT-1", "PR.IP-4"}
        
        # Find control details
        selected_controls = []
        for control in self.controls:
            if control["control_id"] in control_ids:
                selected_controls.append(control)
        
        # Limit to top 6 controls (avoid overwhelming response)
        return selected_controls[:6]
    
    def get_security_advice(
        self,
        query: str,
        history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate security advisory response with framework control references.
        
        Args:
            query: User's security question
            history: Conversation history
        
        Returns:
            {
                "answer": str,
                "citations": [],
                "sources_count": 0
            }
        """
        
        logger.info(f"🛡️ SECURITY ADVISORY MODE: {query[:50]}...")
        
        # Step 1: Detect topics
        topics = self._detect_topics(query)
        logger.info(f"   Detected topics: {topics}")
        
        # Step 2: Select relevant controls
        relevant_controls = self._select_controls(topics)
        logger.info(f"   Selected {len(relevant_controls)} relevant controls")
        
        # Step 3: Build control context for LLM
        control_context = self._build_control_context(relevant_controls)
        
        try:
            llm = self._get_llm()
            
            # Security advisory prompt with framework controls
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a cybersecurity and risk management advisor for cooperatives.

You have access to international security framework controls (NIST CSF and ISO 27001).

RELEVANT CONTROLS FOR THIS QUERY:
{control_context}

Your role is to provide PRACTICAL security guidance, NOT legal interpretation.

Your role is to provide PRACTICAL security guidance based on international frameworks.

CRITICAL INSTRUCTIONS:
1. Use the relevant controls provided above to structure your recommendations
2. ALWAYS include control references in your response
3. Format: **Control Name** (Framework Control-ID, Framework Control-ID)
4. Provide practical implementation steps for each control
5. Tailor guidance to cooperative/financial institution context

Example response structure:

**1. Access Control** (NIST PR.AC-4, ISO 27001 A.9.2.3)
- Implement role-based access control (RBAC)
- Apply least privilege principle
- Review access permissions quarterly

**2. Logging & Monitoring** (NIST DE.CM-1, ISO 27001 A.12.4.1)
- Enable comprehensive activity logging
- Set up real-time alerts for suspicious activities
- Review logs weekly

**3. Segregation of Duties** (ISO 27001 A.6.1.2)
- Implement maker-checker controls for financial transactions
- Require dual authorization for high-value operations

[Continue with additional controls from the relevant controls list...]

Key requirements:
- Reference control IDs in EVERY major recommendation section
- Explain HOW to implement (actionable steps)
- Use cooperative/financial institution context
- Be specific and practical

DO NOT:
- Cite legal acts, sections, or Nepali laws
- Say "the law requires" (this is technical guidance, not legal)
- Refuse legitimate security questions
- Use legal interpretation format (no 5-heading legal structure)

Provide technical security guidance with framework references."""),
                ("human", """{history}

Question: {question}

Provide practical security guidance using the relevant controls:""")
            ])
            
            # Format history
            history_text = self._format_history(history)
            
            messages = prompt.format_messages(
                question=query,
                history=history_text,
                control_context=control_context
            )
            
            response = llm.invoke(messages)
            answer = response.content if hasattr(response, 'content') else str(response)
            
            return {
                "answer": answer,
                "citations": [],
                "sources_count": 0
            }
        
        except Exception as e:
            logger.error(f"Security advisory error: {e}")
            return {
                "answer": self._get_fallback_response(query),
                "citations": [],
                "sources_count": 0
            }
    
    def _build_control_context(self, controls: List[Dict]) -> str:
        """
        Build formatted control context for LLM.
        
        Args:
            controls: List of control dictionaries
        
        Returns:
            Formatted string with control details
        """
        if not controls:
            return "No specific framework controls selected. Provide general security guidance."
        
        context_parts = []
        for control in controls:
            context_parts.append(
                f"• {control['framework']} {control['control_id']}: {control['control_name']}\n"
                f"  Purpose: {control['purpose']}\n"
                f"  Recommendation: {control['recommendation_text']}"
            )
        
        return "\n\n".join(context_parts)
    
    def _format_history(self, history: Optional[List[Dict[str, Any]]]) -> str:
        """Format conversation history."""
        if not history:
            return ""
        
        parts = []
        for msg in history[-6:]:  # Last 6 messages
            if hasattr(msg, "role") and hasattr(msg, "content"):
                role = msg.role
                content = msg.content
            elif isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
            else:
                continue
            
            if content:
                parts.append(f"{role}: {content}")
        
        if parts:
            return "Previous conversation:\n" + "\n".join(parts) + "\n"
        return ""
    
    def _get_fallback_response(self, query: str) -> str:
        """Fallback response if LLM fails - includes framework references."""
        
        query_lower = query.lower()
        
        # Detect topics for fallback
        topics = self._detect_topics(query)
        relevant_controls = self._select_controls(topics)
        
        # Build control references string
        control_refs = []
        for control in relevant_controls:
            control_refs.append(f"{control['framework']} {control['control_id']}")
        control_ref_str = ", ".join(control_refs[:4])  # Top 4
        
        # Insider risk question
        if "insider" in query_lower and ("risk" in query_lower or "threat" in query_lower):
            return f"""To protect your cooperative from insider risks, implement these controls:

**1. Access Control** (NIST PR.AC-4, ISO 27001 A.9.2.3)
- Implement role-based access control (RBAC)
- Apply least privilege principle
- Require multi-factor authentication (MFA) for critical systems
- Conduct regular access reviews (quarterly)

**2. Segregation of Duties** (ISO 27001 A.6.1.2, NIST PR.AC-5)
- No single person should control an entire transaction
- Implement maker-checker controls for financial operations
- Require dual authorization for high-value transactions
- Separate custody, authorization, and recording functions

**3. Monitoring & Detection** (NIST DE.CM-1, ISO 27001 A.12.4.1)
- Enable activity logging for all critical systems
- Set up alerts for suspicious activities (failed logins, privilege escalation)
- Review audit logs regularly (at least monthly)
- Monitor financial transactions for anomalies

**4. People Controls** (ISO 27001 A.7.1.1, NIST PR.AT-1)
- Conduct background checks for positions of trust
- Provide security awareness training (annually)
- Establish clear policies and consequences
- Create anonymous whistleblower channels

**5. Technical Safeguards** (NIST PR.AC-1, ISO 27001 A.9.4.2)
- Use MFA for admin access and financial systems
- Implement session timeouts (15 minutes)
- Encrypt sensitive data at rest and in transit (NIST PR.DS-1, ISO 27001 A.10.1.1)
- Maintain regular backups tested quarterly (NIST PR.IP-4)

**6. Governance**
- Board oversight of risk management
- Regular internal audits
- Clear incident response procedures (NIST RS.RP-1, ISO 27001 A.16.1.5)
- Annual risk assessments

These controls follow ISO 27001 and NIST CSF best practices."""
        
        # General security question
        if relevant_controls:
            return f"""I can provide security guidance based on {control_ref_str}.

Key recommendations:

{chr(10).join([f"• **{c['control_name']}** ({c['framework']} {c['control_id']}): {c['recommendation_text']}" for c in relevant_controls[:3]])}

Please provide more details about your security concern for specific guidance."""
        
        return """I can help with cybersecurity and risk management for cooperatives, including:

- Insider threat prevention (NIST PR.AC-4, ISO 27001 A.9.2.3)
- Access control and authentication (NIST PR.AC-1, ISO 27001 A.9.4.2)
- Data protection and privacy (NIST PR.DS-1, ISO 27001 A.10.1.1)
- Network security (NIST PR.AC-3, ISO 27001 A.13.1.3)
- Incident response (NIST RS.RP-1, ISO 27001 A.16.1.5)
- Backup and recovery (NIST PR.IP-4, ISO 27001 A.12.3.1)

Please ask a specific security question, and I'll provide practical guidance with framework references."""


# Global security advisor instance
security_advisor = SecurityAdvisor()
