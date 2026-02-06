import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from app.core.config import PROJECT_ROOT

ASSESSMENTS_FILE = Path(PROJECT_ROOT) / "data" / "assessments.json"

ANSWER_SCORES = {
    "yes": 2,
    "partial": 1,
    "no": 0
}

ANSWER_ALIASES = {
    "y": "yes",
    "yes": "yes",
    "n": "no",
    "no": "no",
    "partial": "partial",
    "partially": "partial",
    "informal": "partial"
}

ASSESSMENT_SECTIONS = [
    {
        "id": "A",
        "title": "Governance, Policy & Legal Compliance",
        "questions": [
            {
                "id": "A1",
                "text": "Do we have formally approved written policies covering information security, data protection, and acceptable IT usage?",
                "references": ["ETA §43", "ISO 27001 A.5", "NIST: Govern"],
                "recommendation": "Approve and publish formal policies for information security, data protection, and acceptable IT use."
            },
            {
                "id": "A2",
                "text": "Has the board or management formally assigned responsibility for information security and cyber risk?",
                "references": ["Cooperative Act §74", "ISO 27001 A.5.3", "NIST: Govern"],
                "recommendation": "Assign a named owner for information security and cyber risk with defined responsibilities."
            },
            {
                "id": "A3",
                "text": "Are members’ personal, financial, and transaction records classified (e.g., confidential, restricted, public)?",
                "references": ["ETA §45", "ISO 27001 A.5.12", "NIST: Identify"],
                "recommendation": "Create a data classification scheme and apply labels to member records."
            },
            {
                "id": "A4",
                "text": "Do we maintain documented compliance with Nepal Rastra Bank or regulator guidance where applicable?",
                "references": ["Cooperative Act 2016", "ISO 27001 A.5", "NIST: Govern"],
                "recommendation": "Maintain documented compliance evidence for regulator guidance relevant to the cooperative."
            },
            {
                "id": "A5",
                "text": "Are IT and security policies reviewed at least annually?",
                "references": ["ISO 27001 Clause 9", "NIST: Govern"],
                "recommendation": "Set an annual review cycle for IT and security policies and record approvals."
            },
            {
                "id": "A6",
                "text": "Do employees sign confidentiality or data protection agreements?",
                "references": ["ETA §47", "ISO 27001 A.6.6", "NIST: Protect"],
                "recommendation": "Ensure all staff sign confidentiality and data protection agreements on onboarding."
            }
        ]
    },
    {
        "id": "B",
        "title": "Asset & Data Management",
        "questions": [
            {
                "id": "B1",
                "text": "Do we maintain an inventory of IT assets (computers, servers, software, databases)?",
                "references": ["ISO 27001 A.5.9", "NIST: Identify"],
                "recommendation": "Maintain an up-to-date asset inventory covering hardware, software, and data stores."
            },
            {
                "id": "B2",
                "text": "Is sensitive cooperative data encrypted when stored and when transmitted?",
                "references": ["ETA §52", "ISO 27001 A.8.24", "NIST: Protect"],
                "recommendation": "Encrypt sensitive data at rest and in transit using approved cryptography."
            },
            {
                "id": "B3",
                "text": "Are backups performed regularly and tested for restoration?",
                "references": ["ISO 27001 A.8.13", "NIST: Protect"],
                "recommendation": "Perform scheduled backups and run periodic restoration tests."
            },
            {
                "id": "B4",
                "text": "Is member data retained only as long as legally required?",
                "references": ["ETA §28", "ISO 27001 A.5.33", "NIST: Govern"],
                "recommendation": "Define retention periods and purge data when it is no longer legally required."
            },
            {
                "id": "B5",
                "text": "Do we restrict copying of sensitive data to USB drives or personal devices?",
                "references": ["ISO 27001 A.8.12", "NIST: Protect"],
                "recommendation": "Restrict or monitor removable media and personal device data transfers."
            }
        ]
    },
    {
        "id": "C",
        "title": "Access Control & Identity Management",
        "questions": [
            {
                "id": "C1",
                "text": "Do all users have unique user IDs (no shared accounts)?",
                "references": ["ISO 27001 A.8.2", "NIST: Protect"],
                "recommendation": "Eliminate shared accounts and enforce unique user IDs."
            },
            {
                "id": "C2",
                "text": "Are strong passwords or multi-factor authentication enforced?",
                "references": ["ISO 27001 A.8.3", "NIST: Protect"],
                "recommendation": "Enforce strong passwords and implement MFA where possible."
            },
            {
                "id": "C3",
                "text": "Is access immediately revoked when staff leave or change roles?",
                "references": ["ISO 27001 A.6.3", "NIST: Protect"],
                "recommendation": "Implement offboarding procedures to remove or adjust access promptly."
            },
            {
                "id": "C4",
                "text": "Are system administrator privileges strictly limited and logged?",
                "references": ["ISO 27001 A.8.15", "NIST: Detect"],
                "recommendation": "Limit admin privileges to essential staff and log all privileged activity."
            },
            {
                "id": "C5",
                "text": "Are member-facing systems (CBS, mobile apps) protected against unauthorized access?",
                "references": ["ETA §45", "ISO 27001 A.8", "NIST: Protect"],
                "recommendation": "Harden member-facing systems with access controls and security testing."
            }
        ]
    },
    {
        "id": "D",
        "title": "Operations & Technical Security",
        "questions": [
            {
                "id": "D1",
                "text": "Are antivirus, firewall, and endpoint protections deployed and updated?",
                "references": ["ISO 27001 A.8.7", "NIST: Protect"],
                "recommendation": "Deploy endpoint protection and ensure signatures and engines are up to date."
            },
            {
                "id": "D2",
                "text": "Are operating systems and applications patched regularly?",
                "references": ["ISO 27001 A.8.8", "NIST: Protect"],
                "recommendation": "Adopt a patch management schedule for OS and application updates."
            },
            {
                "id": "D3",
                "text": "Are logs collected and reviewed for suspicious activity?",
                "references": ["ISO 27001 A.8.15", "NIST: Detect"],
                "recommendation": "Centralize logs and review them for suspicious activity on a routine schedule."
            },
            {
                "id": "D4",
                "text": "Is internet access filtered to prevent phishing and malware?",
                "references": ["ISO 27001 A.8.23", "NIST: Protect"],
                "recommendation": "Apply web filtering, DNS protection, or secure email gateways to reduce phishing."
            },
            {
                "id": "D5",
                "text": "Are third-party vendors (CBS, cloud, IT support) security-assessed?",
                "references": ["ISO 27001 A.5.19", "NIST: Identify"],
                "recommendation": "Assess vendor security and document due diligence for third-party services."
            }
        ]
    },
    {
        "id": "E",
        "title": "Incident Response & Continuity",
        "questions": [
            {
                "id": "E1",
                "text": "Do we have a documented incident response plan?",
                "references": ["ETA §52", "ISO 27001 A.5.25", "NIST: Respond"],
                "recommendation": "Create and approve an incident response plan with clear roles and steps."
            },
            {
                "id": "E2",
                "text": "Are staff trained on how to report security incidents?",
                "references": ["ISO 27001 A.6.3", "NIST: Respond"],
                "recommendation": "Train staff to report incidents and provide a simple reporting channel."
            },
            {
                "id": "E3",
                "text": "Have we conducted incident simulations or tabletop exercises?",
                "references": ["ISO 27001 A.5.26", "NIST: Respond"],
                "recommendation": "Run tabletop exercises to test the incident response plan."
            },
            {
                "id": "E4",
                "text": "Is there a business continuity and disaster recovery plan?",
                "references": ["Cooperative Act §74", "ISO 27001 A.5.29", "NIST: Recover"],
                "recommendation": "Establish a business continuity and disaster recovery plan with recovery targets."
            },
            {
                "id": "E5",
                "text": "Are backups stored offline or off-site?",
                "references": ["ISO 27001 A.8.13", "NIST: Recover"],
                "recommendation": "Maintain offline or off-site backups to reduce ransomware risk."
            }
        ]
    },
    {
        "id": "F",
        "title": "Awareness, Audit & Improvement",
        "questions": [
            {
                "id": "F1",
                "text": "Do staff receive regular cybersecurity awareness training?",
                "references": ["ISO 27001 A.6.3", "NIST: Protect"],
                "recommendation": "Provide regular cybersecurity awareness training for all staff."
            },
            {
                "id": "F2",
                "text": "Have internal or external security audits been conducted in the last 12 months?",
                "references": ["ISO 27001 Clause 9", "NIST: Govern"],
                "recommendation": "Schedule internal or external security audits at least annually."
            },
            {
                "id": "F3",
                "text": "Are audit findings tracked and remediated?",
                "references": ["ISO 27001 Clause 10", "NIST: Improve"],
                "recommendation": "Track audit findings, assign owners, and document remediation progress."
            },
            {
                "id": "F4",
                "text": "Can we demonstrate evidence (policies, logs, reports) for all above controls?",
                "references": ["ISO 27001 Annex A", "NIST: Govern"],
                "recommendation": "Maintain evidence artifacts such as policies, logs, and reports for controls."
            }
        ]
    }
]


def ensure_storage():
    ASSESSMENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not ASSESSMENTS_FILE.exists():
        ASSESSMENTS_FILE.write_text(json.dumps({"assessments": {}}, indent=2))


def load_assessments() -> Dict:
    ensure_storage()
    return json.loads(ASSESSMENTS_FILE.read_text())


def save_assessments(data: Dict):
    ensure_storage()
    ASSESSMENTS_FILE.write_text(json.dumps(data, indent=2, default=str))


def flatten_questions() -> List[Dict]:
    questions = []
    for section in ASSESSMENT_SECTIONS:
        for question in section["questions"]:
            questions.append({
                **question,
                "section_id": section["id"],
                "section_title": section["title"]
            })
    return questions


def parse_answer(raw_answer: str) -> Tuple[str, int]:
    normalized = raw_answer.strip().lower()
    normalized = ANSWER_ALIASES.get(normalized)
    if not normalized:
        raise ValueError("Please answer with Yes, No, or Partial.")
    return normalized, ANSWER_SCORES[normalized]


def get_risk_level(score: int) -> str:
    if score <= 20:
        return "High Risk / Non-Compliant"
    if score <= 40:
        return "Moderate Risk / Needs Improvement"
    if score <= 55:
        return "Good Security Posture"
    return "Strong & Audit-Ready"


def start_assessment(user: Dict) -> Dict:
    data = load_assessments()
    assessment_id = str(uuid4())
    questions = flatten_questions()

    assessment = {
        "id": assessment_id,
        "user_id": user["id"],
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "status": "in_progress",
        "current_index": 0,
        "answers": [],
        "total_questions": len(questions),
        "max_score": len(questions) * 2
    }

    data["assessments"][assessment_id] = assessment
    save_assessments(data)

    first_question = questions[0]
    return {
        "assessment_id": assessment_id,
        "question": first_question["text"],
        "question_id": first_question["id"],
        "section_title": first_question["section_title"],
        "references": first_question["references"],
        "question_index": 1,
        "total_questions": len(questions),
        "instructions": "Answer with Yes, No, or Partial."
    }


def answer_assessment(assessment_id: str, user: Dict, raw_answer: str) -> Dict:
    data = load_assessments()
    assessment = data["assessments"].get(assessment_id)

    if not assessment:
        raise ValueError("Assessment not found.")
    if assessment["user_id"] != user["id"]:
        raise ValueError("Assessment does not belong to this user.")
    if assessment["status"] != "in_progress":
        raise ValueError("Assessment is not active.")

    questions = flatten_questions()
    current_index = assessment["current_index"]
    if current_index >= len(questions):
        raise ValueError("Assessment already completed.")

    answer_value, score = parse_answer(raw_answer)
    current_question = questions[current_index]

    assessment["answers"].append({
        "question_id": current_question["id"],
        "section_id": current_question["section_id"],
        "answer": answer_value,
        "score": score,
        "question": current_question["text"],
        "references": current_question["references"],
        "recommendation": current_question["recommendation"]
    })
    assessment["current_index"] = current_index + 1

    if assessment["current_index"] >= len(questions):
        assessment["status"] = "completed"
        assessment["completed_at"] = datetime.utcnow().isoformat()
        summary = build_summary(assessment)
        assessment["summary"] = summary
        save_assessments(data)
        return {
            "completed": True,
            **summary,
            "assessment_id": assessment_id
        }

    save_assessments(data)
    next_question = questions[assessment["current_index"]]
    return {
        "completed": False,
        "assessment_id": assessment_id,
        "question": next_question["text"],
        "question_id": next_question["id"],
        "section_title": next_question["section_title"],
        "references": next_question["references"],
        "question_index": assessment["current_index"] + 1,
        "total_questions": len(questions)
    }


def cancel_assessment(assessment_id: str, user: Dict) -> Dict:
    data = load_assessments()
    assessment = data["assessments"].get(assessment_id)
    if not assessment:
        raise ValueError("Assessment not found.")
    if assessment["user_id"] != user["id"]:
        raise ValueError("Assessment does not belong to this user.")
    if assessment["status"] != "in_progress":
        raise ValueError("Assessment is not active.")
    assessment["status"] = "cancelled"
    assessment["completed_at"] = datetime.utcnow().isoformat()
    save_assessments(data)
    return {"cancelled": True, "assessment_id": assessment_id}


def build_summary(assessment: Dict) -> Dict:
    total_score = sum(item["score"] for item in assessment["answers"])
    max_score = assessment["max_score"]
    risk_level = get_risk_level(total_score)

    section_scores: Dict[str, Dict[str, int]] = {}
    for item in assessment["answers"]:
        section_id = item["section_id"]
        if section_id not in section_scores:
            section_scores[section_id] = {"score": 0, "max_score": 0}
        section_scores[section_id]["score"] += item["score"]
        section_scores[section_id]["max_score"] += 2

    recommendations = [
        {
            "question_id": item["question_id"],
            "question": item["question"],
            "answer": item["answer"],
            "recommendation": item["recommendation"],
            "references": item["references"]
        }
        for item in assessment["answers"]
        if item["answer"] != "yes"
    ]

    return {
        "total_score": total_score,
        "max_score": max_score,
        "score_percent": round((total_score / max_score) * 100, 1) if max_score else 0,
        "risk_level": risk_level,
        "section_scores": section_scores,
        "recommendations": recommendations
    }


def get_assessment(assessment_id: str, user: Dict) -> Optional[Dict]:
    data = load_assessments()
    assessment = data["assessments"].get(assessment_id)
    if not assessment:
        return None
    if assessment["user_id"] != user["id"]:
        return None
    return assessment
