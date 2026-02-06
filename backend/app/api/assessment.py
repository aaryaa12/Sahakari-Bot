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


def render_pdf(assessment: dict) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 0.75 * inch
    y = height - margin

    def draw_line(text: str, bold: bool = False, size: int = 11):
        nonlocal y
        if y < margin:
            c.showPage()
            y = height - margin
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawString(margin, y, text)
        y -= 16

    summary = assessment.get("summary", {})
    draw_line("Sahakari Bot - Cybersecurity Compliance Assessment Report", bold=True, size=14)
    draw_line(f"Assessment ID: {assessment['id']}")
    draw_line(f"User ID: {assessment['user_id']}")
    draw_line(f"Created: {assessment['created_at']}")
    draw_line(f"Completed: {assessment.get('completed_at', '')}")
    draw_line("")
    draw_line("Overall Results", bold=True)
    draw_line(f"Total Score: {summary.get('total_score', 0)} / {summary.get('max_score', 0)}")
    draw_line(f"Score Percent: {summary.get('score_percent', 0)}%")
    draw_line(f"Risk Level: {summary.get('risk_level', 'N/A')}")
    draw_line("")
    draw_line("Section Scores", bold=True)

    for section_id, scores in summary.get("section_scores", {}).items():
        draw_line(f"Section {section_id}: {scores['score']} / {scores['max_score']}")

    draw_line("")
    draw_line("Recommendations", bold=True)
    recommendations = summary.get("recommendations", [])
    if not recommendations:
        draw_line("No recommendations. All controls are marked as Yes.")
    else:
        for rec in recommendations:
            draw_line(f"{rec['question_id']} - {rec['question']}", bold=True)
            draw_line(f"Answer: {rec['answer'].title()}")
            draw_line(f"Recommendation: {rec['recommendation']}")
            draw_line(f"References: {', '.join(rec['references'])}")
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

    pdf_bytes = render_pdf(assessment)
    filename = f"assessment-report-{assessment_id}.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
