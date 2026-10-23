import secrets
import string
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db import get_db
from app.deps import require_role, get_current_user
from app.models.user import User
from app.models.class_ import Class
from app.models.enrollment import Enrollment
from app.schemas.classes import ClassCreate, ClassUpdate, ClassOut, EnrollRequest, EnrollmentOut

router = APIRouter(prefix="/classes", tags=["classes"])
UserDep = Annotated[User, Depends(require_role("teacher"))]
StudentDep = Annotated[User, Depends(require_role("student"))]

def code(db: Session) -> str:
    """Generate a short invite code; database uniqueness is the final guard."""
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(20):
        value = "".join(secrets.choice(alphabet) for _ in range(6))
        if not db.query(Class).filter(Class.join_code == value).first(): return value
    raise HTTPException(503, "Could not generate a class code")

def output(item: Class, count: int = 0) -> ClassOut:
    return ClassOut.model_validate({**item.__dict__, "enrolled_count": count, "invite_link": f"/join/{item.join_code}"})

@router.post("", response_model=ClassOut, status_code=201)
def create(payload: ClassCreate, current: UserDep, db: Annotated[Session, Depends(get_db)]):
    item = Class(teacher_id=current.id, name=payload.name.strip(), subject=payload.subject.strip(), join_code=code(db))
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        # A concurrent request can win the unique join-code race.
        db.rollback()
        raise HTTPException(503, "Could not allocate a unique class code; retry")
    db.refresh(item)
    return output(item)

@router.get("", response_model=list[ClassOut])
def list_classes(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current.role == "teacher":
        rows = db.query(Class, func.count(Enrollment.id)).outerjoin(Enrollment).filter(Class.teacher_id == current.id).group_by(Class.id).all()
        return [output(item, count) for item, count in rows]
    rows = db.query(Class, func.count(Enrollment.id)).join(Enrollment, Enrollment.class_id == Class.id).filter(Enrollment.student_id == current.id).group_by(Class.id).all()
    return [output(item, count) for item, count in rows]

@router.get("/mine", response_model=list[ClassOut])
def teacher_classes(current: UserDep, db: Annotated[Session, Depends(get_db)]):
    rows = db.query(Class, func.count(Enrollment.id)).outerjoin(Enrollment).filter(Class.teacher_id == current.id).group_by(Class.id).order_by(Class.created_at.desc()).all()
    return [output(item, count) for item, count in rows]

@router.patch("/{class_id}", response_model=ClassOut)
def update(class_id: int, payload: ClassUpdate, current: UserDep, db: Annotated[Session, Depends(get_db)]):
    item = db.query(Class).filter(Class.id == class_id, Class.teacher_id == current.id).first()
    if not item: raise HTTPException(404, "Class not found")
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(item, key, value.strip())
    db.commit(); db.refresh(item); return output(item, db.query(Enrollment).filter_by(class_id=item.id).count())

@router.delete("/{class_id}", status_code=204)
def remove(class_id: int, current: UserDep, db: Annotated[Session, Depends(get_db)]):
    item = db.query(Class).filter(Class.id == class_id, Class.teacher_id == current.id).first()
    if not item: raise HTTPException(404, "Class not found")
    db.delete(item); db.commit()

@router.get("/{class_id}/students")
def students(class_id: int, current: UserDep, db: Annotated[Session, Depends(get_db)]):
    item = db.query(Class).filter_by(id=class_id, teacher_id=current.id).first()
    if not item:
        raise HTTPException(404, "Class not found")
    return [{"id": u.id, "name": u.name, "email": u.email} for u in
            db.query(User).join(Enrollment, Enrollment.student_id == User.id).filter(Enrollment.class_id == class_id).all()]

@router.post("/join", response_model=EnrollmentOut, status_code=201)
def join(payload: EnrollRequest, current: StudentDep, db: Annotated[Session, Depends(get_db)]):
    return enroll(payload, current, db)

@router.post("/enroll", response_model=EnrollmentOut, status_code=201)
def enroll(payload: EnrollRequest, current: StudentDep, db: Annotated[Session, Depends(get_db)]):
    item = db.query(Class).filter(Class.join_code == payload.join_code.strip().upper()).first()
    if not item: raise HTTPException(404, "Class code not found")
    if db.query(Enrollment).filter_by(student_id=current.id, class_id=item.id).first(): raise HTTPException(409, "Already enrolled")
    enrollment = Enrollment(student_id=current.id, class_id=item.id); db.add(enrollment); db.commit(); db.refresh(enrollment)
    return {"id": enrollment.id, "class_id": item.id, "student_id": current.id, "joined_at": enrollment.joined_at, "class_name": item.name, "subject": item.subject, "join_code": item.join_code}

@router.get("/enrolled", response_model=list[EnrollmentOut])
def enrolled(current: StudentDep, db: Annotated[Session, Depends(get_db)]):
    rows = db.query(Enrollment, Class).join(Class, Class.id == Enrollment.class_id).filter(Enrollment.student_id == current.id).order_by(Enrollment.joined_at.desc()).all()
    return [{"id": e.id, "class_id": c.id, "student_id": e.student_id, "joined_at": e.joined_at, "class_name": c.name, "subject": c.subject, "join_code": c.join_code} for e, c in rows]
