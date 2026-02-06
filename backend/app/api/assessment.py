from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from app.api.dependencies import get_current_user
from app.models.schemas import (
    AssessmentAnswerRequest,
    AssessmentAnswerResponse,
    AssessmentStartResponse,
    AssessmentCancelResponse,
    AssessmentCancelRequest
)
from app.services.assessment import (
    answer_assessment,
    cancel_assessment,
    get_assessment,
    start_assessment
)

router = APIRouter()


SECTION_NAMES = {
    "A": "Governance, Policy & Legal Compliance",
    "B": "Asset & Data Management",
    "C": "Access Control & Identity Management",
    "D": "Operations & Technical Security",
    "E": "Incident Response & Continuity",
    "F": "Awareness, Audit & Improvement"
}

RISK_ANALYSIS = {
    "A1": {
        "risk": "Without formal policies, staff may not understand security requirements, leading to inconsistent practices and regulatory non-compliance.",
        "impact": "Potential regulatory fines, audit failures, and inability to demonstrate due diligence.",
        "technical": "Develop policies addressing: (1) Information security management, (2) Data classification and handling, (3) Acceptable use of IT resources, (4) Incident reporting. Obtain board approval and communicate to all staff."
    },
    "A2": {
        "risk": "Without assigned ownership, security issues may be ignored or uncoordinated, increasing breach likelihood.",
        "impact": "Delayed incident response, fragmented security controls, and unclear accountability during audits.",
        "technical": "Designate a Chief Information Security Officer (CISO) or equivalent with authority to: establish security controls, approve security budgets, and report directly to the board on cyber risk posture."
    },
    "A3": {
        "risk": "Unclassified data may be mishandled, over-shared, or inadequately protected based on sensitivity.",
        "impact": "Data breaches, member privacy violations, and non-compliance with data protection regulations.",
        "technical": "Implement 4-tier classification: PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED. Apply metadata labels to databases and file systems. Configure access controls and encryption based on classification."
    },
    "A4": {
        "risk": "Missing compliance documentation can result in regulatory penalties and suspension of cooperative operations.",
        "impact": "Fines up to Rs. 100,000, license suspension, and reputational damage.",
        "technical": "Establish compliance register tracking: Nepal Rastra Bank directives, Cooperative Act requirements, and ETA obligations. Maintain evidence repository with quarterly compliance attestation."
    },
    "A5": {
        "risk": "Outdated policies become irrelevant as threats evolve, leaving organization exposed to new attack vectors.",
        "impact": "Policy-control gaps, ineffective security measures, and failed audits.",
        "technical": "Schedule annual policy reviews tied to fiscal year. Document review process: threat landscape analysis, regulatory updates, control effectiveness assessment, and board approval."
    },
    "A6": {
        "risk": "Staff without signed agreements may leak confidential data without legal accountability.",
        "impact": "Member data exposure, intellectual property theft, and limited legal recourse.",
        "technical": "Implement mandatory NDAs covering: (1) Confidentiality obligations during and post-employment, (2) Data protection responsibilities per ETA §47, (3) Breach consequences. Integrate into onboarding checklist."
    },
    "B1": {
        "risk": "Unknown assets cannot be secured, patched, or monitored, creating security blind spots.",
        "impact": "Unpatched vulnerabilities, unauthorized devices on network, and inability to contain breaches.",
        "technical": "Deploy Configuration Management Database (CMDB) tracking: hardware (servers, workstations, network devices), software (OS, applications, licenses), and data repositories. Update quarterly with automated discovery tools."
    },
    "B2": {
        "risk": "Unencrypted data can be intercepted in transit or stolen from storage media.",
        "impact": "Member account takeover, financial fraud, and penalties up to Rs. 50,000 under ETA §52.",
        "technical": "Implement AES-256 for data at rest (database encryption, full-disk encryption). Use TLS 1.2+ for data in transit (web applications, APIs). Deploy Hardware Security Module (HSM) for key management."
    },
    "B3": {
        "risk": "Untested backups may fail during recovery, causing permanent data loss and operational shutdown.",
        "impact": "Business continuity failure, member service disruption lasting days/weeks, and potential cooperative insolvency.",
        "technical": "Implement 3-2-1 backup rule: 3 copies, 2 different media, 1 offsite. Schedule daily incremental + weekly full backups. Conduct quarterly restoration drills measuring Recovery Time Objective (RTO) and Recovery Point Objective (RPO)."
    },
    "B4": {
        "risk": "Excessive retention creates liability and violates ETA §28 data minimization requirements.",
        "impact": "Regulatory penalties, increased breach impact, and member privacy violations.",
        "technical": "Define retention schedules: transaction records (10 years), member accounts (7 years post-closure), logs (1 year). Implement automated purging with audit trails. Document legal basis per ETA §28."
    },
    "B5": {
        "risk": "Uncontrolled removable media enables mass data exfiltration by insiders or lost devices.",
        "impact": "Large-scale member data breach, insider theft, and ransomware infection via USB.",
        "technical": "Deploy Device Control policies: block unauthorized USB via Group Policy or Endpoint Detection and Response (EDR). Require encrypted USB drives for approved use. Monitor file-to-USB operations via Data Loss Prevention (DLP)."
    },
    "C1": {
        "risk": "Shared accounts eliminate accountability, making it impossible to trace malicious actions to individuals.",
        "impact": "Undetectable insider fraud, compromised audit trails, and failed forensics investigations.",
        "technical": "Eliminate all shared credentials. Implement unique usernames per Active Directory/LDAP. Deploy Single Sign-On (SSO) for applications. Enforce unique database accounts with role-based access control (RBAC)."
    },
    "C2": {
        "risk": "Weak passwords are easily cracked, enabling unauthorized access and account takeover.",
        "impact": "Compromised accounts, fraudulent transactions, and lateral movement by attackers.",
        "technical": "Enforce password policy: minimum 12 characters, complexity requirements, 90-day expiration. Deploy Multi-Factor Authentication (MFA) using TOTP apps or hardware tokens for admin accounts and financial systems."
    },
    "C3": {
        "risk": "Orphaned accounts from ex-employees provide persistent backdoor access for fraud or data theft.",
        "impact": "Insider revenge attacks, sustained data exfiltration, and compliance violations.",
        "technical": "Implement automated offboarding workflow: disable AD account immediately upon termination, revoke MFA tokens within 1 hour, remove VPN/email access same day. Conduct quarterly access recertification reviews."
    },
    "C4": {
        "risk": "Unlogged admin activity enables privilege abuse and covers tracks during breaches.",
        "impact": "Undetected configuration changes, data manipulation, and forensically invisible attacks.",
        "technical": "Limit admin rights to designated personnel only. Deploy Privileged Access Management (PAM) solution. Enable audit logging for all privileged commands. Forward logs to SIEM with real-time alerts on suspicious admin actions."
    },
    "C5": {
        "risk": "Vulnerable member-facing systems expose sensitive data and enable account takeover attacks.",
        "impact": "Mass account compromise, fraudulent withdrawals, and complete loss of member trust.",
        "technical": "Harden Core Banking System (CBS) and mobile apps: implement input validation, parameterized queries against SQL injection, session management with secure cookies. Conduct annual penetration testing per OWASP Top 10."
    },
    "D1": {
        "risk": "Absent endpoint protection allows malware, ransomware, and zero-day exploits to execute unchecked.",
        "impact": "Ransomware encryption of all systems, data exfiltration, and operational shutdown.",
        "technical": "Deploy next-generation antivirus (NGAV) or Endpoint Detection and Response (EDR) on all endpoints. Enable automatic signature updates. Configure host-based firewall rules. Implement application whitelisting for critical servers."
    },
    "D2": {
        "risk": "Unpatched systems contain known vulnerabilities actively exploited by attackers.",
        "impact": "Remote code execution, privilege escalation, and complete system compromise.",
        "technical": "Establish patch management cycle: Critical patches within 7 days, High within 30 days. Use Windows Update/WSUS for OS patches. Test patches in staging environment before production deployment. Track patch compliance via vulnerability scanner."
    },
    "D3": {
        "risk": "Without log monitoring, breaches remain undetected for months, maximizing damage.",
        "impact": "Prolonged data exfiltration, undetected fraud, and forensically cold trails.",
        "technical": "Deploy Security Information and Event Management (SIEM) or log aggregation (e.g., ELK Stack). Collect logs from: firewalls, servers, databases, applications. Configure alerts for: failed authentication spikes, privilege escalation, unusual data access patterns. Review logs weekly."
    },
    "D4": {
        "risk": "Unfiltered internet access exposes staff to phishing sites and drive-by malware downloads.",
        "impact": "Credential theft via phishing, malware installation, and business email compromise (BEC).",
        "technical": "Deploy DNS filtering (e.g., Cisco Umbrella, Cloudflare Gateway) blocking malicious domains. Implement secure email gateway (SEG) with anti-phishing and anti-spam filters. Use web proxy with SSL inspection for HTTPS traffic analysis."
    },
    "D5": {
        "risk": "Insecure vendors provide backdoor entry points into cooperative's network and data.",
        "impact": "Supply chain attacks, third-party data breaches affecting cooperative, and regulatory liability.",
        "technical": "Conduct vendor security assessments: require SOC 2 Type II reports or ISO 27001 certification. Include security clauses in contracts mandating: encryption, breach notification (24 hours), audit rights. Limit vendor network access via VPN with MFA."
    },
    "E1": {
        "risk": "Without a response plan, breaches escalate chaotically, multiplying damage and cost.",
        "impact": "Prolonged outages, evidence destruction, regulatory notification failures, and legal penalties.",
        "technical": "Develop incident response plan with phases: (1) Preparation, (2) Detection & Analysis, (3) Containment, Eradication & Recovery, (4) Post-Incident Review. Define roles: Incident Commander, Technical Lead, Legal/Compliance. Document escalation paths and communication templates."
    },
    "E2": {
        "risk": "Untrained staff fail to recognize or report incidents, delaying critical response.",
        "impact": "Late breach detection (average 280 days), maximum data loss, and missed containment window.",
        "technical": "Conduct annual security awareness training covering: phishing recognition, incident indicators (ransomware, data theft, account compromise). Establish reporting hotline and email alias (security@coop.np). Incentivize reporting with no-blame policy."
    },
    "E3": {
        "risk": "Untested plans fail in real crises due to undiscovered gaps and team unfamiliarity.",
        "impact": "Response paralysis, missed containment actions, and coordination failures during actual breach.",
        "technical": "Conduct annual tabletop exercises simulating scenarios: ransomware attack, insider data theft, CBS outage. Include board members and key staff. Document lessons learned and update incident response plan. Consider purple team exercises (red team + blue team)."
    },
    "E4": {
        "risk": "Without BC/DR plans, extended outages bankrupt the cooperative through member withdrawals.",
        "impact": "Member panic and mass withdrawals, liquidity crisis, and operational collapse.",
        "technical": "Develop Business Continuity Plan (BCP) defining: (1) Critical business functions, (2) Recovery Time Objectives (RTO: 4 hours for CBS), (3) Recovery Point Objectives (RPO: 15 minutes data loss max). Establish hot standby sites or cloud DR infrastructure. Test failover annually."
    },
    "E5": {
        "risk": "Online-only backups are encrypted by ransomware, eliminating recovery options.",
        "impact": "Total data loss, ransom payment (no guarantee of recovery), and business closure.",
        "technical": "Implement immutable backups: air-gapped offline storage or cloud storage with object lock. Use LTO tape drives or write-once media. Store offsite copy in physically separate location (different building/city). Test offline restoration quarterly."
    },
    "F1": {
        "risk": "Untrained staff are the weakest link, falling victim to social engineering and phishing.",
        "impact": "90% of breaches start with phishing; untrained users compromise entire security stack.",
        "technical": "Deploy annual mandatory training covering: phishing recognition, password security, physical security, social engineering tactics. Use simulated phishing campaigns quarterly to measure effectiveness. Require training completion for system access."
    },
    "F2": {
        "risk": "Without audits, security gaps accumulate unnoticed until exploited in breaches.",
        "impact": "Blind spots in security posture, non-compliance, and failed regulatory examinations.",
        "technical": "Conduct annual internal audits using ISO 27001 Annex A checklist. Engage external auditors for independent assessment. Scope: policy compliance, access controls, vulnerability assessment, configuration review. Deliver findings to board with remediation timeline."
    },
    "F3": {
        "risk": "Untracked findings remain unfixed, perpetuating known security weaknesses.",
        "impact": "Repeat audit failures, exploited known vulnerabilities, and negligence liability.",
        "technical": "Deploy finding tracking system (e.g., GRC platform or Jira). Assign findings to owners with due dates. Categorize by severity: Critical (30 days), High (60 days), Medium (90 days). Report remediation progress to board monthly."
    },
    "F4": {
        "risk": "Lacking evidence, cooperatives cannot prove compliance during audits or investigations.",
        "impact": "Failed audits, assumed non-compliance, regulatory penalties, and loss of certifications.",
        "technical": "Establish evidence repository: approved policies (version-controlled), access logs (1 year retention), incident reports, training completion records, audit reports, penetration test results. Organize by control framework (ISO 27001, NIST). Implement document retention schedule per ETA §28."
    }
}

def render_pdf(assessment: dict, username: str = None) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 0.75 * inch
    y = height - margin

    def draw_line(text: str, bold: bool = False, size: int = 11, indent: int = 0):
        nonlocal y
        if y < margin + 30:
            c.showPage()
            y = height - margin
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawString(margin + indent, y, text)
        y -= 16

    def draw_wrapped_text(text: str, max_width: int, indent: int = 0, bold: bool = False):
        nonlocal y
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 10)
        words = text.split()
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            if c.stringWidth(test_line, "Helvetica-Bold" if bold else "Helvetica", 10) < max_width:
                line = test_line
            else:
                if y < margin + 30:
                    c.showPage()
                    y = height - margin
                c.drawString(margin + indent, y, line)
                y -= 14
                line = word
        if line:
            if y < margin + 30:
                c.showPage()
                y = height - margin
            c.drawString(margin + indent, y, line)
            y -= 14

    summary = assessment.get("summary", {})
    
    # Header with username
    draw_line("Sahakari Bot - Cybersecurity Compliance Assessment Report", bold=True, size=14)
    draw_line(f"Assessment ID: {assessment['id']}", size=10)
    if username:
        draw_line(f"User: {username}", size=10)
    else:
        draw_line(f"User ID: {assessment['user_id']}", size=10)
    draw_line(f"Created: {assessment['created_at']}", size=10)
    draw_line(f"Completed: {assessment.get('completed_at', '')}", size=10)
    draw_line("")
    
    # Overall Results
    draw_line("Overall Results", bold=True, size=12)
    draw_line(f"Total Score: {summary.get('total_score', 0)} / {summary.get('max_score', 0)}")
    draw_line(f"Score Percent: {summary.get('score_percent', 0)}%")
    draw_line(f"Risk Level: {summary.get('risk_level', 'N/A')}")
    draw_line("")
    
    # Section Scores with names
    draw_line("Section Scores", bold=True, size=12)
    for section_id, scores in summary.get("section_scores", {}).items():
        section_name = SECTION_NAMES.get(section_id, section_id)
        draw_line(f"Section {section_id} - {section_name}:", bold=True)
        draw_line(f"  Score: {scores['score']} / {scores['max_score']}", indent=20)
    draw_line("")
    
    # Recommendations with risk analysis
    draw_line("Detailed Recommendations & Risk Analysis", bold=True, size=12)
    recommendations = summary.get("recommendations", [])
    if not recommendations:
        draw_line("No recommendations. All controls are marked as Yes.")
    else:
        for rec in recommendations:
            q_id = rec['question_id']
            risk_info = RISK_ANALYSIS.get(q_id, {})
            
            draw_line("")
            draw_line(f"{q_id} - {rec['question']}", bold=True, size=11)
            draw_line(f"Current Status: {rec['answer'].title()}", size=10)
            draw_line("")
            
            # Technical Recommendation
            if risk_info.get('technical'):
                draw_line("Technical Recommendation:", bold=True, size=10)
                draw_wrapped_text(risk_info['technical'], width - 2*margin - 20, indent=20)
            else:
                draw_line("Recommendation:", bold=True, size=10)
                draw_wrapped_text(rec['recommendation'], width - 2*margin - 20, indent=20)
            draw_line("")
            
            # Risk if not implemented
            if risk_info.get('risk'):
                draw_line("Risk if not implemented:", bold=True, size=10)
                draw_wrapped_text(risk_info['risk'], width - 2*margin - 20, indent=20)
                draw_line("")
            
            # Business Impact
            if risk_info.get('impact'):
                draw_line("Business Impact:", bold=True, size=10)
                draw_wrapped_text(risk_info['impact'], width - 2*margin - 20, indent=20)
                draw_line("")
            
            # Framework References
            draw_line(f"Framework References: {', '.join(rec['references'])}", size=9)
            draw_line("")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


@router.post("/assessment/start", response_model=AssessmentStartResponse)
async def assessment_start(current_user: dict = Depends(get_current_user)):
    try:
        return start_assessment(current_user)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )


@router.post("/assessment/answer", response_model=AssessmentAnswerResponse)
async def assessment_answer(
    payload: AssessmentAnswerRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        return answer_assessment(payload.assessment_id, current_user, payload.answer)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )


@router.post("/assessment/cancel", response_model=AssessmentCancelResponse)
async def assessment_cancel(
    payload: AssessmentCancelRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        return cancel_assessment(payload.assessment_id, current_user)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )


@router.get("/assessment/report/{assessment_id}")
async def assessment_report(
    assessment_id: str,
    current_user: dict = Depends(get_current_user)
):
    assessment = get_assessment(assessment_id, current_user)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    if assessment.get("status") != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment is not completed yet"
        )

    # Get username from current_user
    username = current_user.get("username", current_user.get("email", f"User {current_user.get('id')}"))
    
    pdf_bytes = render_pdf(assessment, username=username)
    filename = f"assessment-report-{assessment_id}.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
