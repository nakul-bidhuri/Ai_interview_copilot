from io import BytesIO
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


def generate_interview_pdf(
    session_id: str,
    candidate_name: str,
    target_role: str,
    target_company: str,
    experience_level: str,
    grace_years: int,
    overall_score: float,
    scores: Dict[str, Any],
    feedback: Dict[str, Any],
    transcript: List[Dict[str, Any]]
) -> str:
    """
    Generates a beautifully styled PDF performance report and saves it to reports/.
    Returns the absolute path to the generated PDF.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    pdf_filename = f"Interview_Report_{candidate_name.replace(' ', '_')}_{session_id[:8]}.pdf"
    pdf_path = REPORTS_DIR / pdf_filename

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#0072ff"),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#555555"),
        spaceAfter=12
    )
    heading2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#222222")
    )
    bullet_style = ParagraphStyle(
        "BulletText",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#333333"),
        leftIndent=12
    )
    callout_style = ParagraphStyle(
        "CalloutText",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    story = []

    # 1. Header
    story.append(Paragraph("🎯 AI Interview Copilot Pro", title_style))
    story.append(Paragraph(f"Comprehensive Candidate Evaluation & Coaching Report | Generated {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0072ff"), spaceAfter=12))

    # 2. Metadata Table
    meta_data = [
        [
            Paragraph(f"<b>Candidate:</b> {candidate_name}", body_style),
            Paragraph(f"<b>Target Role:</b> {target_role}", body_style)
        ],
        [
            Paragraph(f"<b>Target Company:</b> {target_company or 'Tech Industry'}", body_style),
            Paragraph(f"<b>Experience:</b> {experience_level}", body_style)
        ],
        [
            Paragraph(f"<b>Grace / Gap Years:</b> {grace_years} year(s)", body_style),
            Paragraph(f"<b>Overall Score:</b> <b><font color='#0072ff' size='12'>{overall_score} / 10</font></b>", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # 3. Score Breakdown Table
    story.append(Paragraph("📊 Skill Competency Breakdown", heading2_style))
    score_rows = [["Competency Category", "Score (out of 10)", "Assessment"]]
    assessment_map = {
        "technical_depth": "Knowledge of architecture, coding, and design tradeoffs",
        "communication_clarity": "Structure, articulation, and conciseness",
        "confidence_delivery": "Poise, voice modulation, and calmness under pressure",
        "problem_solving": "Analytical breakdown of complex problems and edge cases",
        "star_method_alignment": "Effective use of Situation-Task-Action-Result format"
    }

    for key, label in [
        ("technical_depth", "Technical Depth"),
        ("communication_clarity", "Communication Clarity"),
        ("confidence_delivery", "Confidence & Delivery"),
        ("problem_solving", "Problem Solving & Logic"),
        ("star_method_alignment", "STAR Behavioral Alignment")
    ]:
        val = scores.get(key, 8.0)
        score_rows.append([label, f"{val:.1f} / 10", assessment_map.get(key, "General performance")])

    score_table = Table(score_rows, colWidths=[160, 110, 270])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0072ff")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 14))

    # 4. Key Strengths & Critical Improvement Areas
    story.append(Paragraph("💪 Top Strengths", heading2_style))
    for s in feedback.get("top_strengths", ["Demonstrated foundational domain knowledge."]):
        story.append(Paragraph(f"• {s}", bullet_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("🎯 Critical Areas for Improvement", heading2_style))
    for imp in feedback.get("critical_areas_for_improvement", ["Practice quantifying results in projects."]):
        story.append(Paragraph(f"• {imp}", bullet_style))
    story.append(Spacer(1, 12))

    # 5. Grace Years / Career Gap Masterclass
    if grace_years > 0 or "grace_years_coaching" in feedback:
        story.append(Paragraph("⏳ Grace & Gap Years Strategy Masterclass", heading2_style))
        gy_info = feedback.get("grace_years_coaching", {})
        if isinstance(gy_info, dict):
            power_stmt = gy_info.get("power_statement", "Frame this period around focused learning.")
            story.append(Paragraph(f"<b>Recommended Interview Script / Power Statement:</b>", body_style))
            story.append(Paragraph(f"<i>\"{power_stmt}\"</i>", callout_style))
        story.append(Spacer(1, 10))

    # 6. Question-by-Question Deep Review & Model Answers
    reviews = feedback.get("questions_review", [])
    if reviews:
        story.append(Paragraph("📝 Question Reviews & Pro Model Answers", heading2_style))
        for idx, rev in enumerate(reviews, 1):
            q_text = rev.get("question", f"Question {idx}")
            score_val = rev.get("score", 8.0)
            fb_text = rev.get("feedback", "Good attempt.")
            model_ans = rev.get("model_answer", "")

            q_flowables = [
                Paragraph(f"<b>Q{idx}: {q_text}</b> (Score: {score_val}/10)", ParagraphStyle("QTitle", parent=body_style, fontName="Helvetica-Bold", textColor=colors.HexColor("#0072ff"))),
                Paragraph(f"<b>Interviewer Critique:</b> {fb_text}", body_style),
                Paragraph(f"<b>How to Answer Like a Pro:</b> <i>{model_ans}</i>", callout_style),
                Spacer(1, 6)
            ]
            story.append(KeepTogether(q_flowables))

    # 7. Actionable Next Steps
    actions = feedback.get("actionable_next_steps", [])
    if actions:
        story.append(Paragraph("🚀 Final Actionable Next Steps", heading2_style))
        for act in actions:
            story.append(Paragraph(f"✔ {act}", bullet_style))

    doc.build(story)
    return str(pdf_path)


def get_pdf_bytes(pdf_path_str: str) -> bytes:
    """Reads PDF file into bytes for Streamlit download button."""
    with open(pdf_path_str, "rb") as f:
        return f.read()
