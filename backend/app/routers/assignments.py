from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from app.db import get_db
from app.deps import get_current_user, require_role
from app.models.user import User
from app.models.class_ import Class
from app.models.assignment import Assignment
from app.models.question import Question
from app.schemas.assignments import AssignmentCreate, AssignmentOut, StudentAssignmentOut

router = APIRouter(prefix="/assignments", tags=["assignments"])
Teacher = Annotated[User, Depends(require_role("teacher"))]

@router.post("/class/{class_id}", response_model=AssignmentOut, status_code=201)
def create(class_id: int, payload: AssignmentCreate, current: Teacher, db: Annotated[Session, Depends(get_db)]):
    if not db.query(Class).filter_by(id=class_id, teacher_id=current.id).first():
        raise HTTPException(404, "Class not found")
    total = payload.total_marks if payload.total_marks is not None else sum(q.marks for q in payload.questions)
    item = Assignment(class_id=class_id, title=payload.title.strip(), description=payload.description, deadline=payload.deadline, total_marks=total, pass_mark_percent=payload.pass_mark_percent)
    item.questions = [Question(**q.model_dump()) for q in payload.questions]
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.get("/class/{class_id}", response_model=None)
def list_for_class(class_id: int, db: Annotated[Session, Depends(get_db)], current: User = Depends(get_current_user)):
    query = db.query(Assignment).options(selectinload(Assignment.questions)).join(Class).filter(Assignment.class_id == class_id)
    if current.role == "teacher":
        query = query.filter(Class.teacher_id == current.id)
    else:
        from app.models.enrollment import Enrollment
        query = query.join(Enrollment, Enrollment.class_id == Class.id).filter(Enrollment.student_id == current.id)
    rows = query.order_by(Assignment.created_at.desc()).all()
    if current.role == "student":
        return [{"id": a.id, "class_id": a.class_id, "title": a.title, "description": a.description,
                 "total_marks": a.total_marks, "pass_mark_percent": a.pass_mark_percent,
                 "deadline": a.deadline,
                 "questions": [{"id": q.id, "type": q.type, "text": q.text, "marks": q.marks, "options": q.options}
                                for q in a.questions]} for a in rows]
    return rows

@router.get("/{assignment_id}", response_model=None)
def get_one(assignment_id: int, db: Annotated[Session, Depends(get_db)], current: User = Depends(get_current_user)):
    row = db.query(Assignment).options(selectinload(Assignment.questions)).join(Class).filter(Assignment.id == assignment_id).first()
    if not row:
        raise HTTPException(404, "Assignment not found")
    if current.role == "teacher":
        if row.class_.teacher_id != current.id:
            raise HTTPException(403, "Class ownership required")
        return row
    from app.models.enrollment import Enrollment
    if not db.query(Enrollment).filter_by(class_id=row.class_id, student_id=current.id).first():
        raise HTTPException(403, "You are not enrolled in this class")
    return {
        "id": row.id, "class_id": row.class_id, "title": row.title,
        "description": row.description, "total_marks": row.total_marks,
        "pass_mark_percent": row.pass_mark_percent, "deadline": row.deadline,
        "questions": [{"id": q.id, "type": q.type, "text": q.text, "marks": q.marks,
                       "options": q.options} for q in row.questions]
    }
