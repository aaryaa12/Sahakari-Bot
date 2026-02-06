# Test Questions for RAG Pipelines

This document contains test questions organized by mode to help you evaluate the Sahakari Bot.

---

## LEGAL MODE Questions

### Cooperative Act 2074 - Registration & Formation

1. **What does Formation and Registration of Cooperative Organization mean?**
2. **What are the requirements for registering a cooperative?**
3. **What documents are needed for cooperative registration?**
4. **What is Section 12 of the Cooperative Act?**
5. **Who can be a member of a cooperative?**
6. **What are the membership eligibility criteria?**

### Cooperative Act 2074 - Governance

7. **What are byelaws and internal procedures?**
8. **Tell me about byelaws**
9. **What is the role of the board of directors?**
10. **How should board meetings be conducted according to the Act?**
11. **What are the powers of the general assembly?**
12. **What is Section 27 about?**

### Cooperative Act 2074 - Financial Management

13. **What happens if unauthorized loans are given?**
14. **What are the penalties for financial misconduct?**
15. **What are the audit requirements for cooperatives?**
16. **What is the role of the auditor?**
17. **Can cooperatives invest in shares?**

### Cooperative Act 2074 - Penalties & Offenses

18. **What are the penalties under the Cooperative Act?**
19. **What happens if someone violates the cooperative bylaws?**
20. **What is Section 93 of the Cooperative Act?**
21. **What are offences under the Act?**

### Electronic Transaction Act 2063 - Digital Signatures

22. **What is Section 4 of ETA?**
23. **What is an electronic signature?**
24. **How does digital signature work under ETA?**
25. **What is the legal validity of electronic signatures?**
26. **What is a certification service provider?**

### Electronic Transaction Act 2063 - Security & Cybercrime

27. **What is Section 18 of ETA?**
28. **What are the penalties for unauthorized access?**
29. **What does ETA say about data protection?**
30. **What are cybercrime penalties in Nepal?**
31. **What is unauthorized access under ETA?**
32. **What happens if someone hacks a cooperative's system?**

### Electronic Transaction Act 2063 - Electronic Records

33. **What are the requirements for electronic records?**
34. **How long must electronic records be kept?**
35. **What is Section 15 of ETA about?**
36. **Are electronic contracts legally valid?**

### Cross-Law Questions (Testing Act Isolation)

37. **What are the legal requirements for data security in cooperatives?**
38. **What laws govern electronic transactions in cooperatives?**
39. **What are the legal penalties for cybercrime affecting cooperatives?**

---

## SECURITY MODE Questions

### Insider Threat Protection

40. **How can I protect my cooperative from insider risks?**
41. **How to protect from insider threats?**
42. **What controls prevent insider fraud?**
43. **How to monitor employee activities?**
44. **What background checks should we do?**

### Access Control & Authentication

45. **How to implement access control?**
46. **What is role-based access control (RBAC)?**
47. **How to implement multi-factor authentication?**
48. **What password policy should we use?**
49. **How often should we review user access?**

### Phishing & Email Security

50. **How to protect against phishing attacks?**
51. **What email security measures should I implement?**
52. **How to train staff on phishing?**
53. **What email filtering should we use?**

### Network Security & Firewall

54. **What firewall should I use for my cooperative?**
55. **How to secure our network?**
56. **What firewall rules should we configure?**
57. **How to implement network segmentation?**

### Data Protection & Encryption

58. **How to protect member data?**
59. **What encryption should we use?**
60. **How to encrypt sensitive data?**
61. **How to secure data at rest?**
62. **How to secure data in transit?**

### Backup & Disaster Recovery

63. **What backup strategy should we use?**
64. **How often should we backup data?**
65. **How to test backup restoration?**
66. **What is the 3-2-1 backup rule?**

### Monitoring & Logging

67. **What should we log and monitor?**
68. **How to detect suspicious activities?**
69. **How long should we keep logs?**
70. **What events should trigger alerts?**

### Security Training & Awareness

71. **What security training should staff receive?**
72. **How often should we conduct security training?**
73. **What topics should security training cover?**

### Incident Response

74. **How to respond to security incidents?**
75. **What is an incident response plan?**
76. **How to handle a data breach?**

### Vulnerability & Patch Management

77. **How to manage software patches?**
78. **How often should we patch systems?**
79. **How to scan for vulnerabilities?**

### General Security

80. **What security measures should I implement?**
81. **How to prevent fraud in cooperative?**
82. **What are best practices for cooperative security?**

---

## COOP MODE Questions (Operational Guidance)

83. **How to conduct board meetings?**
84. **What are best practices for member meetings?**
85. **How to manage loan portfolios?**
86. **What reports should the board review?**
87. **How to calculate dividends?**
88. **What is the role of a cooperative manager?**

---

## GENERAL MODE Questions

89. **Hello, how are you?**
90. **What can you help me with?**
91. **Tell me about cooperatives in Nepal**
92. **What is the purpose of this chatbot?**

---

## Special Test Cases

### Testing 5-Heading Format (Legal Mode)

93. **What is Section 27 of Cooperative Act?**
   - Should include: Legal meaning, Legal effect, Practical implications, What Act does NOT specify, Evidence

### Testing Framework References (Security Mode)

94. **How to implement segregation of duties?**
   - Should include: ISO 27001 A.6.1.2, NIST PR.AC-5

### Testing Act Isolation (No Cross-Law Mixing)

95. **What are unauthorized loan penalties?**
   - Should ONLY cite Cooperative Act, NOT ETA

96. **What are electronic authentication methods?**
   - Should ONLY cite ETA, NOT Cooperative Act

### Testing Section Retrieval

97. **What is Section 4, Chapter 2 of ETA?**
   - Should retrieve exact section

98. **What is Chapter 3 of Cooperative Act?**
   - Should retrieve correct chapter

### Testing Fallback Responses

99. **What is Section 999 of Cooperative Act?**
   - Should say: "The provided legal documents do not contain a provision addressing this specific matter."

100. **What is the weather today?**
    - Should route to GENERAL mode

---

## Quick Copy-Paste Test Set

### Legal Mode Quick Test (5 questions)

```
What does Formation and Registration of Cooperative Organization mean?
What are byelaws and internal procedures?
What is Section 4 of ETA?
What happens if unauthorized loans are given?
What is Section 18 of ETA?
```

### Security Mode Quick Test (5 questions)

```
How can I protect my cooperative from insider risks?
What firewall should I use for my cooperative?
How to protect against phishing attacks?
What backup strategy should we use?
How to implement multi-factor authentication?
```

### Mixed Mode Test (All 4 modes)

```
What is Section 27 of Cooperative Act?
How to protect from insider threats?
How to conduct board meetings?
Hello, how are you?
```

---

## Expected Response Indicators

### Legal Mode Response Should Have:

- ✅ Act name + Section number (e.g., "Cooperative Act 2074 — Section 27")
- ✅ 5-heading structure:
  1. Legal meaning (plain language)
  2. Legal effect / obligations
  3. Practical implications for a cooperative
  4. What the Act does NOT specify
  5. Evidence (from provided documents)
- ✅ Citations with Act name and section
- ✅ NO framework references (no NIST/ISO)

### Security Mode Response Should Have:

- ✅ Framework control IDs (e.g., "NIST PR.AC-4, ISO 27001 A.9.2.3")
- ✅ Practical implementation steps
- ✅ Specific technical guidance
- ✅ NO legal sections (no Act citations)
- ✅ NO 5-heading legal format

### Coop Mode Response Should Have:

- ✅ Operational guidance
- ✅ Best practices
- ✅ Management procedures
- ✅ NO legal citations
- ✅ NO framework references

---

## Testing Tips

1. **Test one mode at a time** to verify correct routing
2. **Check for cross-contamination**:
   - Legal responses should NOT have NIST/ISO references
   - Security responses should NOT have Act citations
3. **Verify format adherence**:
   - Legal = 5 headings
   - Security = Framework IDs
4. **Test edge cases**:
   - Non-existent sections
   - Ambiguous queries
   - Cross-law questions

---

## How to Test

### Using API (curl)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "YOUR_QUESTION_HERE"}'
```

### Using Frontend

1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm start`
3. Open browser: `http://localhost:3000`
4. Type questions in chat interface

### Using Python Script

```python
import requests

questions = [
    "What is Section 27 of Cooperative Act?",
    "How to protect from insider risks?",
    "How to conduct board meetings?"
]

for q in questions:
    response = requests.post(
        "http://localhost:8000/chat",
        json={"message": q}
    )
    print(f"\nQ: {q}")
    print(f"A: {response.json()['response'][:200]}...")
```

---

## Evaluation Checklist

For each question, verify:

- [ ] Correct mode routing (LEGAL/SECURITY/COOP/GENERAL)
- [ ] Appropriate format (5-heading for legal, framework IDs for security)
- [ ] Correct citations (Act sections for legal, NIST/ISO for security)
- [ ] No cross-contamination (no mixing of citation types)
- [ ] Grounded in source documents (no hallucination)
- [ ] Practical and actionable guidance

---

## Success Criteria

- **Legal Mode**: 5-heading format, Act citations, no framework IDs
- **Security Mode**: Framework control IDs, practical steps, no Act citations
- **Act Isolation**: No cross-law mixing (Cooperative Act ≠ ETA)
- **Section Retrieval**: Exact section returned when requested
- **Fallback**: Appropriate response when content not found

---

## Need More Questions?

Generate custom questions by combining:

**[Topic]** + **[Mode Trigger]**

Examples:
- "What does **[legal term]** mean?" → LEGAL MODE
- "How to implement **[security control]**?" → SECURITY MODE
- "How to conduct **[operational task]**?" → COOP MODE

Happy testing! 🧪
