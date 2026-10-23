from io import BytesIO
from fpdf import FPDF


def _pdf_text(value: object) -> str:
    # Helvetica is always available; replace unsupported Unicode rather than
    # turning an approved result download into a 500 response.
    return str(value or "").encode("latin-1", "replace").decode("latin-1")


def build_feedback_pdf(submission, student_name: str, assignment_title: str) -> bytes:
    """Build a release-only PDF with wrapping and Unicode-safe fallback text."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "GradeLens Student Feedback Report", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 7, _pdf_text(f"Student: {student_name}\nAssignment: {assignment_title}\nSubmission: {submission.id}"))
    pdf.ln(4)
    total = 0
    for index, answer in enumerate(submission.answers, 1):
        score = answer.teacher_score if answer.teacher_score is not None else answer.ai_score
        total += score or 0
        question = getattr(answer, "question", None)
        text = getattr(question, "text", "Question")
        feedback = answer.teacher_feedback or answer.ai_feedback or "No explanation provided."
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 7, _pdf_text(f"Question {index}: {text}"))
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(0, 6, _pdf_text(f"Score: {score if score is not None else '-'}\nFeedback: {feedback}"))
        pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, _pdf_text(f"Total score: {total}"), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output(dest="S"))
