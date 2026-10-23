"""Create clearly-marked demo data. Run from the repository root with backend deps installed."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.db import SessionLocal
from app.models.user import User
from app.models.class_ import Class
from app.models.assignment import Assignment
from app.models.question import Question
from app.models.enrollment import Enrollment
from app.services.auth_service import hash_password

DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "DemoOnly-ChangeMe-123!")
db = SessionLocal()
try:
    teacher = db.query(User).filter_by(email="teacher@gradelens.com").first()
    if not teacher:
        teacher = User(name="Demo Teacher", email="teacher@gradelens.com", role="teacher", password_hash=hash_password(DEMO_PASSWORD))
        db.add(teacher); db.flush()
    student = db.query(User).filter_by(email="student@gradelens.com").first()
    if not student:
        student = User(name="Demo Student", email="student@gradelens.com", role="student", password_hash=hash_password(DEMO_PASSWORD))
        db.add(student); db.flush()
    classroom = db.query(Class).filter_by(join_code="DEMO11").first()
    if not classroom:
        classroom = Class(name="Demo Rubrics", subject="Education", join_code="DEMO11", teacher_id=teacher.id)
        db.add(classroom); db.flush()
    if not db.query(Enrollment).filter_by(class_id=classroom.id, student_id=student.id).first():
        db.add(Enrollment(class_id=classroom.id, student_id=student.id))
    assignment = db.query(Assignment).filter_by(class_id=classroom.id, title="Welcome assignment").first()
    if not assignment:
        assignment = Assignment(class_id=classroom.id, title="Welcome assignment", description="Demo-only assignment", total_marks=10, pass_mark_percent=50)
        assignment.questions = [Question(type="written", text="Explain one benefit of rubric-based feedback.", marks=10, rubric="Accuracy and clarity", sample_answer="Rubrics make expectations explicit.")]
        db.add(assignment)
    db.commit()
    print("Demo data ready. Credentials are demo-only; change DEMO_PASSWORD before any real use.")
finally:
    db.close()
