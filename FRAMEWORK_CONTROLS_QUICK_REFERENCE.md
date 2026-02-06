# Security Framework Controls - Quick Reference

## Topic-to-Controls Mapping

This guide shows which framework controls are recommended for common security topics.

---

## 1. Insider Threat / Insider Risk

**Relevant Controls**:
- **NIST PR.AC-4**: Access Permissions and Authorizations
- **ISO 27001 A.9.2.3**: Management of Privileged Access Rights
- **NIST PR.AC-1**: Identity and Access Management
- **NIST DE.CM-1**: Network Monitoring
- **ISO 27001 A.12.4.1**: Event Logging
- **ISO 27001 A.6.1.2**: Segregation of Duties
- **ISO 27001 A.7.1.1**: Screening (Background Checks)

**Example Query**: "How can I protect my cooperative from insider risks?"

**Expected Response Format**:
```
**1. Access Control** (NIST PR.AC-4, ISO 27001 A.9.2.3)
- Implement role-based access control (RBAC)
- Apply least privilege principle
- Review access permissions quarterly

**2. Segregation of Duties** (ISO 27001 A.6.1.2)
- No single person controls entire transaction
- Implement maker-checker controls
- Require dual authorization for high-value operations

**3. Monitoring & Detection** (NIST DE.CM-1, ISO 27001 A.12.4.1)
- Enable activity logging
- Set up real-time alerts for suspicious activities
- Review audit logs monthly
```

---

## 2. Phishing / Email Security

**Relevant Controls**:
- **NIST PR.AT-1**: Security Awareness Training
- **ISO 27001 A.7.2.2**: Information Security Awareness
- **NIST PR.PT-4**: Communications and Control Networks
- **ISO 27001 A.9.4.2**: Secure Log-on Procedures (MFA)

**Example Query**: "How to protect against phishing attacks?"

**Expected Response Format**:
```
**1. Awareness Training** (NIST PR.AT-1, ISO 27001 A.7.2.2)
- Conduct security awareness training annually
- Include phishing recognition exercises
- Run simulated phishing campaigns quarterly

**2. Email Security** (NIST PR.PT-4)
- Implement email filtering (anti-spam, anti-malware)
- Block suspicious attachments (.exe, .zip from external sources)
- Use email authentication (SPF, DKIM, DMARC)

**3. Multi-Factor Authentication** (ISO 27001 A.9.4.2)
- Implement MFA for email access
- Use session timeouts (15 minutes inactivity)
```

---

## 3. Network Security / Firewall

**Relevant Controls**:
- **NIST PR.AC-3**: Remote Access Management
- **ISO 27001 A.13.1.3**: Segregation in Networks
- **NIST PR.IP-12**: Vulnerability Management
- **ISO 27001 A.12.6.1**: Management of Technical Vulnerabilities
- **NIST DE.CM-1**: Network Monitoring

**Example Query**: "What firewall configuration should I use?"

**Expected Response Format**:
```
**1. Firewall Configuration** (NIST PR.AC-3, ISO 27001 A.13.1.3)
- Deploy perimeter firewall and internal firewalls
- Configure default-deny rules
- Implement DMZ for public-facing services
- Use next-generation firewall with IPS/IDS

**2. Network Segmentation** (ISO 27001 A.13.1.3, NIST PR.AC-5)
- Segment financial systems from general network
- Use VLANs to separate critical systems
- Review firewall rules quarterly
```

---

## 4. Data Protection / Encryption

**Relevant Controls**:
- **NIST PR.DS-1**: Data at Rest Protection
- **ISO 27001 A.10.1.1**: Cryptographic Controls
- **NIST PR.DS-2**: Data in Transit Protection
- **ISO 27001 A.9.1.2**: Access to Networks and Services

**Example Query**: "How to protect sensitive member data?"

**Expected Response Format**:
```
**1. Data at Rest Encryption** (NIST PR.DS-1, ISO 27001 A.10.1.1)
- Encrypt sensitive data at rest (AES-256)
- Encrypt database files and backups
- Use full-disk encryption for laptops
- Manage encryption keys securely

**2. Data in Transit Encryption** (NIST PR.DS-2)
- Use TLS 1.2 or higher for all web traffic
- Encrypt email containing sensitive information
- Use VPN for remote access
- Disable insecure protocols (SSLv3, TLS 1.0)

**3. Access Control** (ISO 27001 A.9.1.2)
- Restrict access to sensitive data based on role
- Implement network access control (NAC)
```

---

## 5. Backup & Disaster Recovery

**Relevant Controls**:
- **NIST PR.IP-4**: Backup and Recovery
- **ISO 27001 A.12.3.1**: Information Backup

**Example Query**: "What backup strategy should I use?"

**Expected Response Format**:
```
**1. Backup Strategy** (NIST PR.IP-4, ISO 27001 A.12.3.1)
- Perform daily incremental backups
- Perform weekly full backups
- Store backups offsite or in cloud
- Test backup restoration quarterly
- Encrypt backup data
- Follow 3-2-1 rule: 3 copies, 2 media types, 1 offsite

**2. Recovery Planning** (NIST PR.IP-4)
- Define Recovery Time Objectives (RTO)
- Define Recovery Point Objectives (RPO)
- Document recovery procedures
- Conduct disaster recovery drills annually
```

---

## 6. Access Control / Authentication

**Relevant Controls**:
- **NIST PR.AC-4**: Access Permissions and Authorizations
- **ISO 27001 A.9.2.3**: Management of Privileged Access Rights
- **NIST PR.AC-1**: Identity and Access Management
- **ISO 27001 A.9.4.2**: Secure Log-on Procedures
- **ISO 27001 A.9.1.2**: Access to Networks and Services

**Example Query**: "How to manage user access?"

**Expected Response Format**:
```
**1. Identity Management** (NIST PR.AC-1)
- Use unique user IDs for each person
- Implement strong password policies (12+ characters)
- Disable inactive accounts after 90 days

**2. Access Authorization** (NIST PR.AC-4, ISO 27001 A.9.2.3)
- Implement role-based access control (RBAC)
- Apply least privilege principle
- Review access permissions quarterly
- Require approval for privileged access

**3. Authentication** (ISO 27001 A.9.4.2)
- Implement multi-factor authentication (MFA)
- Use session timeouts (15 minutes inactivity)
- Lock accounts after 5 failed login attempts
```

---

## 7. Logging & Monitoring

**Relevant Controls**:
- **NIST DE.CM-1**: Network Monitoring
- **ISO 27001 A.12.4.1**: Event Logging
- **NIST DE.AE-3**: Event Data Analysis

**Example Query**: "What should I log and monitor?"

**Expected Response Format**:
```
**1. Event Logging** (ISO 27001 A.12.4.1)
- Log user activities, exceptions, and security events
- Include: user ID, date/time, type of event, success/failure
- Retain logs for at least 90 days
- Protect log files from tampering

**2. Monitoring** (NIST DE.CM-1)
- Monitor for suspicious activities:
  - Failed login attempts
  - Privilege escalation
  - Unusual data access
  - Large file transfers
- Review logs weekly

**3. Event Analysis** (NIST DE.AE-3)
- Implement SIEM or centralized log analysis
- Set up alerts for critical events
- Investigate anomalies within 24 hours
```

---

## 8. Security Awareness Training

**Relevant Controls**:
- **NIST PR.AT-1**: Security Awareness Training
- **ISO 27001 A.7.2.2**: Information Security Awareness

**Example Query**: "What security training should staff receive?"

**Expected Response Format**:
```
**1. Security Awareness Training** (NIST PR.AT-1, ISO 27001 A.7.2.2)
- Conduct training annually for all staff
- Include during onboarding (new employees)
- Cover topics:
  - Phishing recognition
  - Password security
  - Social engineering
  - Clean desk policy
  - Incident reporting procedures
  - Data classification
  - Acceptable use policy

**2. Testing & Reinforcement** (NIST PR.AT-1)
- Test with simulated phishing campaigns quarterly
- Provide additional training for users who fail tests
- Track training completion rates
- Update content based on emerging threats
```

---

## 9. Patch Management / Vulnerability Management

**Relevant Controls**:
- **NIST PR.IP-12**: Vulnerability Management
- **ISO 27001 A.12.6.1**: Management of Technical Vulnerabilities

**Example Query**: "How to manage software patches?"

**Expected Response Format**:
```
**1. Patch Management** (NIST PR.IP-12, ISO 27001 A.12.6.1)
- Apply security patches within 30 days of release
- Apply critical patches within 7 days
- Test patches in non-production environment first
- Schedule maintenance windows for patch deployment
- Document patching activities

**2. Vulnerability Scanning** (NIST PR.IP-12)
- Maintain inventory of all systems and software
- Scan for vulnerabilities monthly
- Subscribe to security advisories
- Prioritize vulnerabilities by severity (CVSS score)
```

---

## 10. Incident Response

**Relevant Controls**:
- **NIST RS.RP-1**: Response Plan
- **ISO 27001 A.16.1.5**: Response to Information Security Incidents

**Example Query**: "How to respond to security incidents?"

**Expected Response Format**:
```
**1. Incident Response Plan** (NIST RS.RP-1, ISO 27001 A.16.1.5)
- Develop incident response plan with defined roles
- Establish incident response team
- Define incident severity levels
- Document handling procedures
- Include communication plan and escalation procedures

**2. Incident Handling** (ISO 27001 A.16.1.5)
- Establish reporting procedures (who, when, how)
- Respond based on severity:
  - Critical: within 1 hour
  - High: within 4 hours
  - Medium: within 24 hours
- Conduct post-incident reviews
- Document lessons learned

**3. Testing** (NIST RS.RP-1)
- Conduct tabletop exercises annually
- Test communication channels
- Review and update plan after incidents
```

---

## Control ID Reference

### NIST Cybersecurity Framework (CSF)

| Control ID | Control Name |
|-----------|--------------|
| PR.AC-1 | Identity and Access Management |
| PR.AC-3 | Remote Access Management |
| PR.AC-4 | Access Permissions and Authorizations |
| PR.AC-5 | Network Segregation |
| PR.AT-1 | Security Awareness Training |
| PR.DS-1 | Data at Rest Protection |
| PR.DS-2 | Data in Transit Protection |
| PR.IP-4 | Backup and Recovery |
| PR.IP-12 | Vulnerability Management |
| PR.PT-4 | Communications and Control Networks |
| DE.CM-1 | Network Monitoring |
| DE.AE-3 | Event Data Analysis |
| RS.RP-1 | Response Plan |

### ISO 27001:2013

| Control ID | Control Name |
|-----------|--------------|
| A.6.1.2 | Segregation of Duties |
| A.7.1.1 | Screening (Background Checks) |
| A.7.2.2 | Information Security Awareness |
| A.9.1.2 | Access to Networks and Services |
| A.9.2.3 | Management of Privileged Access Rights |
| A.9.4.2 | Secure Log-on Procedures |
| A.10.1.1 | Cryptographic Controls |
| A.12.3.1 | Information Backup |
| A.12.4.1 | Event Logging |
| A.12.6.1 | Management of Technical Vulnerabilities |
| A.13.1.3 | Segregation in Networks |
| A.16.1.5 | Response to Information Security Incidents |

---

## Usage Tips

1. **Ask specific questions**: "How to prevent insider threats?" works better than "What is security?"

2. **Topic keywords trigger controls**:
   - "insider" → Access control + Monitoring + Segregation of duties
   - "phishing" → Awareness training + Email filtering
   - "firewall" → Network security + Segmentation
   - "backup" → Backup and recovery controls

3. **Response always includes**:
   - Control IDs (NIST, ISO)
   - Practical implementation steps
   - Cooperative/financial institution context

4. **Security mode does NOT**:
   - Cite legal sections
   - Use legal interpretation format
   - Mix with Nepali law guidance

---

## Testing Your Query

Run interactive test:

```bash
cd backend
python -c "
from app.services.security_advisor import security_advisor

result = security_advisor.get_security_advice(
    'How to protect from insider risks?'
)

print(result['answer'])
"
```

Expected output should include framework references like:
- `(NIST PR.AC-4, ISO 27001 A.9.2.3)`
- `(NIST DE.CM-1, ISO 27001 A.12.4.1)`

---

## Summary

- **25+ controls** from NIST CSF and ISO 27001
- **10+ security topics** mapped to relevant controls
- **Always includes control IDs** in responses
- **Completely separate** from legal RAG database
- **Fast and maintainable** (no re-ingestion needed)
