from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.app.models.feedback import Feedback
from backend.app.app.models.portal_users import Users


# Create (Intern only)
def create_feedback(db: Session, data, current_user):

    if current_user["role"] != 2:
        raise HTTPException(status_code=403, detail="Only interns can send feedback")

    receiver = db.query(Users).filter(
        Users.user_id == data.assigned_to,
        Users.type.in_([1, 4])
    ).first()

    if not receiver:
        feedback = Feedback(
        user_id=current_user["user_id"],
        assigned_to=None,
        category=data.category,
        message=data.message,
        status="pending"
    )

        db.add(feedback)
        db.commit()
        db.refresh(feedback)

        return feedback

    if current_user["user_id"] == data.assigned_to:
        raise HTTPException(status_code=400, detail="Cannot send feedback to yourself")

    feedback = Feedback(
        user_id=current_user["user_id"],
        assigned_to=data.assigned_to,
        category=data.category,
        message=data.message,
        status="pending"
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return feedback


# Intern → View all feedback
def get_all_feedback(db: Session, current_user):

    # Only admin
    if current_user["role"] != 1:
        raise HTTPException(status_code=403, detail="Only admin allowed")

    # return ALL
    return db.query(Feedback).order_by(
        Feedback.created_at.desc()
    ).all()


# Admin/Mentor → View assigned feedback
def get_feedback_for_admin(db: Session, current_user):

    if current_user["role"] not in [1, 4]:
        raise HTTPException(status_code=403, detail="Permission denied")

    return db.query(Feedback).filter(
        Feedback.assigned_to == current_user["user_id"]
    ).order_by(Feedback.created_at.desc()).all()


# Reply (Admin/Mentor)
def reply_feedback(db: Session, data, current_user):

    # Only ADMIN allowed
    if current_user["role"] != 1:
        raise HTTPException(
            status_code=403,
            detail="Only admin can reply to feedback"
        )

    feedback = db.query(Feedback).filter(
        Feedback.id == data.feedback_id
    ).first()

    if not feedback:
        raise HTTPException(
            status_code=404,
            detail="Feedback not found"
        )

    # REMOVE this check (important)
    # if feedback.assigned_to != current_user["user_id"]:
    #     raise HTTPException(status_code=403, detail="Not assigned to you")

    # Admin can reply ANY feedback
    feedback.reply = data.reply
    feedback.status = "replied"

    db.commit()
    db.refresh(feedback)

    return feedback


# Delete (Admin only)
def delete_feedback(db: Session, feedback_id: int, current_user):

    if current_user["role"] != 1:
        raise HTTPException(status_code=403, detail="Only admin can delete")

    feedback = db.query(Feedback).filter(
        Feedback.id == feedback_id
    ).first()

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    db.delete(feedback)
    db.commit()

    return {"message": "Deleted successfully"}