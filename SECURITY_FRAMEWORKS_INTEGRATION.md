# Security Frameworks Integration

## Overview

The Security Advisory Mode now includes **international security framework controls** from:
- **NIST Cybersecurity Framework (CSF)**
- **ISO 27001:2013**

These controls are stored as a **structured knowledge base** within the security advisor module, completely separate from the legal RAG database.

## Architecture

```
User Query
    ↓
Intent Detection
    ↓
SECURITY MODE?
    ↓ YES
Topic Detection → Control Selection → Advisory Generation
    ↓
Response with Framework References
(NIST PR.AC-4, ISO 27001 A.9.2.3)
```

**CRITICAL**: Framework controls are NOT ingested into ChromaDB. They remain in-memory Python data structures.

---

## Implementation Details

### 1. Control Knowledge Base

Located in: `backend/app/services/security_advisor.py`

Each control entry contains:

```python
{
    "framework": "NIST CSF" | "ISO 27001",
    "control_id": "PR.AC-4",
    "control_name": "Access Permissions and Authorizations",
    "purpose": "Manage access permissions based on least privilege",
    "recommendation_text": "Implement role-based access control..."
}
```

**Total Controls**: 25+ controls covering:
- Access Control (NIST PR.AC-1, PR.AC-4, ISO A.9.2.3, A.9.4.2)
- Logging & Monitoring (NIST DE.CM-1, DE.AE-3, ISO A.12.4.1)
- Segregation of Duties (ISO A.6.1.2, NIST PR.AC-5)
- Awareness Training (NIST PR.AT-1, ISO A.7.2.2)
- Email Security (NIST PR.PT-4)
- Network Security (NIST PR.AC-3, ISO A.13.1.3)
- Patch Management (NIST PR.IP-12, ISO A.12.6.1)
- Encryption (NIST PR.DS-1, PR.DS-2, ISO A.10.1.1)
- Backup & Recovery (NIST PR.IP-4, ISO A.12.3.1)
- Incident Response (NIST RS.RP-1, ISO A.16.1.5)
- Background Checks (ISO A.7.1.1)

### 2. Topic-to-Controls Mapping

```python
TOPIC_CONTROLS_MAP = {
    "insider_threat": ["PR.AC-4", "A.9.2.3", "DE.CM-1", "A.12.4.1", "A.6.1.2"],
    "phishing": ["PR.AT-1", "A.7.2.2", "PR.PT-4"],
    "network_security": ["PR.AC-3", "A.13.1.3", "PR.IP-12"],
    "data_protection": ["PR.DS-1", "A.10.1.1", "PR.DS-2"],
    "backup": ["PR.IP-4", "A.12.3.1"],
    ...
}
```

### 3. Query Processing Flow

#### Step 1: Topic Detection
```python
def _detect_topics(self, query: str) -> List[str]:
    """
    Detects security topics from query text
    Returns: ["insider_risk", "access_control"]
    """
```

**Example**:
- Query: "How to protect from insider risks?"
- Detected topics: `["insider_risk", "insider_threat"]`

#### Step 2: Control Selection
```python
def _select_controls(self, topics: List[str]) -> List[Dict]:
    """
    Selects relevant controls based on topics
    Returns top 6 controls
    """
```

**Example**:
- Topics: `["insider_risk"]`
- Selected controls:
  - NIST PR.AC-4 (Access Permissions)
  - ISO 27001 A.9.2.3 (Privileged Access)
  - NIST DE.CM-1 (Network Monitoring)
  - ISO 27001 A.12.4.1 (Event Logging)
  - ISO 27001 A.6.1.2 (Segregation of Duties)

#### Step 3: Context Building
```python
def _build_control_context(self, controls: List[Dict]) -> str:
    """
    Formats controls for LLM prompt
    """
```

**Output format**:
```
• NIST CSF PR.AC-4: Access Permissions and Authorizations
  Purpose: Manage access permissions based on least privilege
  Recommendation: Implement RBAC with least privilege...

• ISO 27001 A.9.2.3: Management of Privileged Access Rights
  Purpose: Restrict and control privileged access rights
  Recommendation: Allocate privileged access on need-to-use basis...
```

#### Step 4: Advisory Generation

The LLM receives:
1. Relevant controls with full details
2. User query
3. System prompt requiring control references

**Response format**:
```
**1. Access Control** (NIST PR.AC-4, ISO 27001 A.9.2.3)
- Implement role-based access control (RBAC)
- Apply least privilege principle
- Review access permissions quarterly

**2. Logging & Monitoring** (NIST DE.CM-1, ISO 27001 A.12.4.1)
- Enable activity logging for all critical systems
- Set up alerts for suspicious activities
- Review logs weekly
```

---

## Example Queries and Responses

### Query: "How to protect my cooperative from insider risks?"

**Detected Topics**: `insider_risk`, `insider_threat`

**Selected Controls**:
- NIST PR.AC-4, ISO 27001 A.9.2.3 (Access Control)
- NIST DE.CM-1, ISO 27001 A.12.4.1 (Monitoring)
- ISO 27001 A.6.1.2 (Segregation of Duties)
- ISO 27001 A.7.1.1 (Background Checks)

**Response Includes**:
```
**1. Access Control** (NIST PR.AC-4, ISO 27001 A.9.2.3)
- Implement role-based access control (RBAC)
- Use least privilege principle
- Review access quarterly

**2. Segregation of Duties** (ISO 27001 A.6.1.2)
- Implement maker-checker controls
- Require dual authorization for high-value transactions
- Separate custody, authorization, and recording

**3. Monitoring & Detection** (NIST DE.CM-1, ISO 27001 A.12.4.1)
- Enable comprehensive logging
- Set up real-time alerts
- Review audit logs monthly
```

### Query: "What firewall should I use?"

**Detected Topics**: `network_security`, `firewall`

**Selected Controls**:
- NIST PR.AC-3 (Remote Access Management)
- ISO 27001 A.13.1.3 (Network Segregation)
- NIST PR.AC-5 (Network Segregation)

**Response Includes**:
```
**Network Security** (NIST PR.AC-3, ISO 27001 A.13.1.3)
- Deploy perimeter firewall and internal firewalls
- Configure default-deny rules
- Implement DMZ for public-facing services
- Use next-generation firewall with IPS/IDS
```

---

## Critical Design Decisions

### ✅ DO

1. **Store controls in Python code** (not database)
   - Fast access (no vector search needed)
   - Easy to update and maintain
   - Version controlled

2. **Map topics to specific controls**
   - Ensures relevant recommendations
   - Prevents generic advice

3. **Always include control references**
   - Provides credibility
   - Enables auditability
   - Follows compliance best practices

4. **Keep separate from legal RAG**
   - No ChromaDB ingestion
   - No legal document contamination
   - Clear separation of concerns

### ❌ DO NOT

1. **DO NOT ingest into ChromaDB**
   - Would mix technical guidance with legal text
   - Would require re-embedding on updates
   - Would slow down retrieval

2. **DO NOT cite legal sections in security mode**
   - NIST/ISO controls, not Nepali law
   - No "Cooperative Act Section X"
   - No legal interpretation format

3. **DO NOT use legal RAG pipeline**
   - Security advisor is completely independent
   - No metadata filtering
   - No constrained retrieval

---

## Testing

Run verification tests:

```bash
cd backend
python test_security_mode.py
```

**Expected Results**:
- ✅ Intent routing: 8/8 passed
- ✅ Security advisor includes framework references
- ✅ Legal mode unchanged
- ✅ No citation bleeding between modes

---

## Maintenance

### Adding New Controls

1. Add control to `SECURITY_CONTROLS` in `security_advisor.py`:

```python
{
    "framework": "ISO 27001",
    "control_id": "A.8.2.1",
    "control_name": "Classification of Information",
    "purpose": "Ensure information receives appropriate protection",
    "recommendation_text": "Classify data as Public, Internal, Confidential, Restricted..."
}
```

2. Add to topic mapping:

```python
TOPIC_CONTROLS_MAP = {
    "data_classification": ["A.8.2.1"],
    ...
}
```

3. Test with relevant query.

### Updating Existing Controls

Simply edit the control entry in `SECURITY_CONTROLS`. Changes are immediate (no re-ingestion).

---

## Comparison: Legal vs Security Mode

| Aspect | Legal Mode | Security Mode |
|--------|-----------|---------------|
| **Source** | Nepali legal PDFs | NIST CSF, ISO 27001 |
| **Storage** | ChromaDB (vector DB) | Python code |
| **Retrieval** | Metadata filtering + semantic search | Topic detection → control mapping |
| **Format** | 5-heading legal structure | Practical steps with control IDs |
| **Citations** | Act + Section numbers | Framework + Control IDs |
| **Intent** | LEGAL | SECURITY |
| **Pipeline** | RAG (retrieve → generate) | Direct advisory (no retrieval) |

---

## Benefits

1. **Credibility**: Responses backed by international standards
2. **Auditability**: Control IDs enable compliance verification
3. **Specificity**: Targeted recommendations (not generic)
4. **Maintainability**: Easy to update without re-ingestion
5. **Performance**: No vector search latency
6. **Separation**: Legal and technical guidance stay distinct

---

## Future Enhancements

### Potential Additions

1. **More frameworks**:
   - CIS Controls v8
   - PCI DSS (for payment systems)
   - COBIT (for governance)

2. **Risk level mapping**:
   - HIGH risk → stricter controls
   - MEDIUM risk → standard controls
   - LOW risk → basic controls

3. **Industry-specific controls**:
   - Financial institutions (Basel III)
   - Healthcare (HIPAA)
   - Government (NIST 800-53)

4. **Control maturity assessment**:
   - Current state vs desired state
   - Implementation roadmap

---

## Conclusion

The Security Advisory Mode now provides **evidence-based, framework-aligned cybersecurity guidance** while maintaining complete separation from the legal RAG pipeline.

**Key Principle**: Security frameworks are knowledge, not documents. They should be structured and accessible, not buried in vector embeddings.

✅ **Implementation Status**: Complete and tested
✅ **Legal Mode**: Unchanged
✅ **Zero Interference**: Security and legal modes are isolated
✅ **Framework References**: Always included in responses
