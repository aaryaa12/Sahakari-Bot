# Security vs Legal Mode - Side-by-Side Comparison

This document shows the clear separation between SECURITY MODE (framework-based guidance) and LEGAL MODE (statutory interpretation).

---

## Example 1: Insider Risk

### Query: "How can I protect my cooperative from insider risks?"

#### SECURITY MODE Response:

```
**1. Access Control** (NIST PR.AC-4, ISO 27001 A.9.2.3)
- Implement role-based access control (RBAC)
- Apply least privilege principle
- Review access permissions quarterly
- Require approval for privileged access

**2. Segregation of Duties** (ISO 27001 A.6.1.2)
- No single person should control an entire transaction
- Implement maker-checker controls for financial operations
- Require dual authorization for high-value transactions (>Rs. 100,000)
- Separate custody, authorization, and recording functions

**3. Monitoring & Detection** (NIST DE.CM-1, ISO 27001 A.12.4.1)
- Enable activity logging for all critical systems
- Set up alerts for suspicious activities:
  * Failed login attempts (>5 in 15 minutes)
  * Privilege escalation attempts
  * Unusual data access patterns
  * Financial transactions outside normal hours
- Review audit logs at least monthly
- Monitor financial transactions for anomalies

**4. People Controls** (ISO 27001 A.7.1.1, NIST PR.AT-1)
- Conduct background checks for positions of trust
- Provide security awareness training annually
- Establish clear policies and consequences
- Create anonymous whistleblower channels

**5. Technical Safeguards**
- Use multi-factor authentication (MFA) for admin access (ISO 27001 A.9.4.2)
- Implement session timeouts (15 minutes inactivity)
- Encrypt sensitive data at rest and in transit (NIST PR.DS-1, PR.DS-2)
- Maintain regular backups tested quarterly (NIST PR.IP-4)

**6. Governance**
- Board oversight of risk management
- Regular internal audits
- Clear incident response procedures (NIST RS.RP-1)
- Annual risk assessments
```

**Citations**: None (no legal sections)
**Framework References**: NIST PR.AC-4, PR.DS-1, DE.CM-1, RS.RP-1, PR.AT-1, ISO 27001 A.9.2.3, A.6.1.2, A.12.4.1, A.7.1.1, A.9.4.2

---

### Query: "What does Section 27 of Cooperative Act say about fraud?"

#### LEGAL MODE Response:

```
**Cooperative Act 2074 — Section 27**

**1) Legal meaning (plain language)**
Section 27 of the Cooperative Act 2074 prohibits any person from providing
unauthorized loans or credit from the funds of a cooperative organization.
This provision aims to protect cooperative assets from misuse and ensure
financial transactions follow proper authorization procedures.

**2) Legal effect / obligations**
- Prohibition: No person may provide loans or credits from cooperative funds
  without proper authorization
- Applicability: Applies to all persons with access to cooperative funds
  (board members, staff, managers)
- Consequence: Violation constitutes an offense under the Act
- Enforcement: Subject to penalty provisions under Section 93

**3) Practical implications for a cooperative (Kathmandu Valley context)**
- Establish formal loan approval process requiring board authorization
- Maintain written loan policies defining:
  * Maximum loan amounts
  * Required documentation
  * Approval authority levels
  * Repayment terms
- Implement maker-checker controls for all financial disbursements
- Record all loan approvals in board meeting minutes
- Conduct quarterly internal audits of loan portfolio
- Segregate duties between loan approval and disbursement

**4. What the Act does NOT specify**
- Does not define specific penalties or fine amounts (see Section 93)
- Does not specify required approval procedures (left to bylaws)
- Does not define "unauthorized" in quantitative terms
- Does not prescribe internal control mechanisms
- Does not specify documentation requirements

**5) Evidence (from provided documents)**
Quote: "No person shall provide loan or credit from the funds of a cooperative
organization without authorization"
Source: Cooperative Act 2074, Section 27, Page 18

Quote: "Any person who violates this provision shall be subject to penalty
as prescribed"
Source: Cooperative Act 2074, Section 27, Page 18
```

**Citations**: Cooperative Act 2074, Section 27
**Framework References**: None (no NIST/ISO)

---

## Example 2: Network Security vs Legal Requirements

### Query: "What firewall should I use for my cooperative?"

#### SECURITY MODE Response:

```
**1. Firewall Configuration** (NIST PR.AC-3, ISO 27001 A.13.1.3)

For financial institutions and cooperatives, I recommend using a
Next-Generation Firewall (NGFW) that provides:

**Core Requirements:**
- Stateful packet inspection
- Intrusion Prevention System (IPS)
- Application-level filtering
- VPN support for remote access
- Centralized logging and reporting

**Configuration Best Practices** (ISO 27001 A.13.1.3):
1. Deploy perimeter firewall at internet connection
2. Deploy internal firewalls to segment network zones
3. Configure default-deny rules (block all, allow specific)
4. Implement DMZ for public-facing services
5. Review firewall rules quarterly
6. Document all rule changes

**Network Segmentation** (NIST PR.AC-5):
- Separate financial systems from general office network
- Use VLANs or physical separation
- Restrict access between segments
- Monitor cross-segment traffic

**2. Access Control** (NIST PR.AC-3)
- Require VPN for all remote access
- Implement multi-factor authentication for VPN
- Use strong encryption (AES-256, IPsec)
- Log all remote access sessions
- Review VPN access quarterly

**3. Monitoring** (NIST DE.CM-1)
- Enable firewall logging
- Set up alerts for:
  * Blocked connection attempts
  * Rule violations
  * Suspicious traffic patterns
- Review logs weekly
- Integrate with SIEM if available
```

**Citations**: None
**Framework References**: NIST PR.AC-3, PR.AC-5, DE.CM-1, ISO 27001 A.13.1.3

---

### Query: "What are the legal requirements for data security?"

#### LEGAL MODE Response:

```
**Electronic Transaction Act 2063 — Chapter on Security (Sections 15-20)**

**1) Legal meaning (plain language)**
The Electronic Transaction Act 2063 establishes legal obligations for organizations
handling electronic data to implement security measures. These provisions require
cooperatives using electronic systems to protect data from unauthorized access,
ensure data integrity, and maintain audit trails.

**2) Legal effect / obligations**
Obligations for cooperatives:
- Must implement security procedures for electronic records (Section 15)
- Must protect against unauthorized access to electronic systems (Section 18)
- Must maintain electronic records for prescribed period (Section 16)
- Must ensure reliability and integrity of electronic signatures (Section 17)
- Must report security breaches as prescribed

Obligations of the regulator:
- Controller may prescribe security standards
- May require security audits
- May inspect electronic systems for compliance

Penalties:
- Unauthorized access: Fine up to Rs. 100,000 or imprisonment up to 3 years
  (Section 47)
- Data breach due to negligence: Fine up to Rs. 50,000 (Section 48)

**3) Practical implications for a cooperative (Kathmandu Valley context)**
- Deploy firewalls and access control systems
- Implement user authentication mechanisms (passwords, MFA)
- Enable activity logging for all electronic transactions
- Conduct annual security audits
- Develop incident response plan
- Train staff on security procedures
- Maintain backup and recovery procedures
- Document all security measures in security policy
- Report security incidents to Controller within prescribed timeframe

**4) What the Act does NOT specify**
- Does not prescribe specific technical standards (firewall models, encryption algorithms)
- Does not define "adequate security" in technical terms
- Does not specify logging retention periods
- Does not mandate specific authentication methods
- Does not require specific certifications (ISO 27001, etc.)
- Implementation details left to Controller's regulations and bylaws

**5) Evidence (from provided documents)**
Quote: "Every person maintaining electronic records shall ensure security of such records"
Source: Electronic Transaction Act 2063, Section 15, Page 12

Quote: "Unauthorized access to electronic system shall be punishable with fine or imprisonment"
Source: Electronic Transaction Act 2063, Section 47, Page 28

Quote: "Organizations shall implement security procedures as prescribed by the Controller"
Source: Electronic Transaction Act 2063, Section 15, Page 12
```

**Citations**: Electronic Transaction Act 2063, Sections 15-20, 47, 48
**Framework References**: None

---

## Example 3: Data Protection

### Query: "How to protect member data?"

#### SECURITY MODE Response:

```
**1. Data Classification** (implied from ISO 27001 A.8.2.1)
Classify member data by sensitivity:
- **Confidential**: Financial records, loan details, personal identification
- **Internal**: Membership lists, general records
- **Public**: Cooperative announcements, general information

**2. Encryption** (NIST PR.DS-1, ISO 27001 A.10.1.1)

**Data at Rest:**
- Encrypt database files (AES-256)
- Encrypt backups before offsite storage
- Use full-disk encryption for laptops and removable media
- Manage encryption keys securely (separate from encrypted data)

**Data in Transit:**
- Use TLS 1.2 or higher for web applications (NIST PR.DS-2)
- Encrypt email containing sensitive information
- Use VPN for remote access
- Disable insecure protocols (FTP, Telnet, HTTP)

**3. Access Control** (NIST PR.AC-4, ISO 27001 A.9.2.3)
- Implement role-based access control
- Limit access to member data to authorized personnel only
- Use least privilege principle
- Review access permissions quarterly
- Disable accounts for separated employees immediately

**4. Backup** (NIST PR.IP-4, ISO 27001 A.12.3.1)
- Daily incremental backups
- Weekly full backups
- Store backups offsite (cloud or separate location)
- Encrypt backup data
- Test restoration quarterly
- Follow 3-2-1 rule: 3 copies, 2 media types, 1 offsite

**5. Physical Security**
- Lock server rooms
- Restrict physical access to data centers
- Use surveillance cameras
- Implement visitor logs
- Secure disposal of old storage media (shred or degauss)
```

**Citations**: None
**Framework References**: NIST PR.DS-1, PR.DS-2, PR.AC-4, PR.IP-4, ISO 27001 A.10.1.1, A.9.2.3, A.12.3.1

---

### Query: "What does the law say about data protection?"

#### LEGAL MODE Response:

```
**Electronic Transaction Act 2063 — Section 15 (Security of Electronic Records)**

**1) Legal meaning (plain language)**
Section 15 of the Electronic Transaction Act 2063 imposes a legal obligation on
every person or organization maintaining electronic records to ensure the security
of those records. This creates a duty to implement reasonable security measures to
protect electronic data from unauthorized access, modification, or destruction.

**2) Legal effect / obligations**
Legal obligations:
- Must ensure security of all electronic records maintained
- Must protect against unauthorized access
- Must implement security procedures
- Must maintain integrity of electronic records
- Breach of this obligation may result in liability

Who must comply:
- All cooperatives using electronic systems
- Board members responsible for governance
- IT staff managing systems
- Any person with access to electronic records

Regulatory authority:
- Controller may prescribe security standards
- Controller may require security audits
- Controller may inspect compliance

**3) Practical implications for a cooperative (Kathmandu Valley context)**
To comply with Section 15:
- Adopt written information security policy
- Implement access control mechanisms:
  * User authentication (passwords)
  * Authorization levels (role-based access)
  * Multi-factor authentication for critical systems
- Deploy technical safeguards:
  * Firewalls
  * Antivirus software
  * Encryption for sensitive data
  * Regular security updates
- Establish administrative controls:
  * Security awareness training
  * Incident response procedures
  * Regular security audits
  * Vendor security assessments
- Maintain audit trails and logs
- Implement backup and recovery procedures
- Document all security measures

**4) What the Act does NOT specify**
- Does not define specific technical standards or controls
- Does not prescribe encryption algorithms or key lengths
- Does not mandate specific certifications (ISO 27001, PCI DSS)
- Does not specify frequency of security audits
- Does not define "adequate security" quantitatively
- Does not require specific budget allocation for security
- Implementation details left to Controller's regulations

**5) Evidence (from provided documents)**
Quote: "Every person maintaining electronic record shall ensure security
of such record and take necessary measures"
Source: Electronic Transaction Act 2063, Section 15, Page 12

Quote: "The Controller may prescribe security procedures and standards
to be followed"
Source: Electronic Transaction Act 2063, Section 15, Page 12
```

**Citations**: Electronic Transaction Act 2063, Section 15
**Framework References**: None

---

## Key Differences Summary

| Aspect | SECURITY MODE | LEGAL MODE |
|--------|---------------|------------|
| **Purpose** | Technical guidance | Legal interpretation |
| **Source** | NIST CSF, ISO 27001 | Cooperative Act, ETA |
| **Storage** | Python dict | ChromaDB vector DB |
| **Retrieval** | Topic mapping | Metadata filtering + semantic search |
| **References** | Framework control IDs | Act name + Section number |
| **Format** | Practical steps with control IDs | 5-heading legal structure |
| **Citations** | (NIST PR.AC-4, ISO 27001 A.9.2.3) | Cooperative Act 2074, Section 27 |
| **Tone** | Prescriptive ("Implement...") | Interpretive ("The law requires...") |
| **Scope** | How to implement | What the law says |
| **Audience** | IT/Security teams | Board/Compliance officers |
| **Output** | Actionable technical steps | Legal obligations and implications |

---

## When to Use Each Mode

### Use SECURITY MODE for:
- ✅ "How to protect from insider risks?"
- ✅ "What firewall should I use?"
- ✅ "How to implement MFA?"
- ✅ "What backup strategy should I follow?"
- ✅ "How to train staff on security?"
- ✅ "How to respond to security incidents?"

### Use LEGAL MODE for:
- ✅ "What is Section 27 of Cooperative Act?"
- ✅ "What are legal requirements for registration?"
- ✅ "What does the law say about data protection?"
- ✅ "What are penalties for unauthorized access?"
- ✅ "What are byelaw requirements?"
- ✅ "What does ETA say about electronic signatures?"

---

## No Cross-Contamination

### Security Mode Will NEVER:
- ❌ Cite legal sections (no "Cooperative Act Section X")
- ❌ Use 5-heading legal format
- ❌ Reference Nepali statutes
- ❌ Call legal RAG pipeline
- ❌ Retrieve from ChromaDB

### Legal Mode Will NEVER:
- ❌ Reference framework controls (no "NIST PR.AC-4")
- ❌ Provide technical implementation steps without legal basis
- ❌ Use international standards as authority
- ❌ Call security advisor module
- ❌ Retrieve from control knowledge base

---

## Architecture Isolation

```
┌─────────────────────────────────────────────────────────────┐
│                        User Query                            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │ Intent Router │  ← Single decision point
         └───────┬───────┘
                 │
         ┌───────┴───────┐
         │               │
         │               │
    LEGAL MODE      SECURITY MODE
         │               │
         │               │
         ▼               ▼
┌─────────────────┐  ┌─────────────────────┐
│  Legal RAG      │  │  Security Advisor   │
│                 │  │                     │
│ • ChromaDB      │  │ • Python dict       │
│ • Metadata      │  │ • Topic detection   │
│   filtering     │  │ • Control selection │
│ • Semantic      │  │ • Framework refs    │
│   search        │  │                     │
│ • 5-heading     │  │ • Practical steps   │
│   format        │  │                     │
│                 │  │                     │
│ Act + Section   │  │ NIST + ISO IDs      │
└─────────────────┘  └─────────────────────┘
         │                       │
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
             ┌───────────────┐
             │   Response    │
             └───────────────┘
```

**CRITICAL**: No shared code path after routing. Complete architectural separation.

---

## Conclusion

**SECURITY MODE** = International best practices (NIST, ISO)
**LEGAL MODE** = Nepali statutory interpretation (Cooperative Act, ETA)

**Both modes coexist** with zero interference, providing comprehensive guidance:
- Technical security teams get framework-based recommendations
- Compliance officers get legal interpretations with statutory citations

**Result**: World-class security advisory + rigorous legal compliance
