from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.app.api.deps import get_db, role_required
from backend.app.app.schemas.feedback_schemas import (
    FeedbackCreate,
    FeedbackReply,
    FeedbackResponse
)
from backend.app.app.crud.feedback_crud import (
    create_feedback,
    get_all_feedback,
    get_my_feedback,
    get_feedback_for_admin,
    reply_feedback,
    delete_feedback
)

router = APIRouter(prefix="/feedback", tags=["Feedback"])


# Create feedback (Intern)
@router.post("/", response_model=FeedbackResponse)
def create_feedback_api(
    data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([2]))
):
    return create_feedback(db, data, current_user)


# Intern → View all feedback
@router.get("/all", response_model=list[FeedbackResponse])
def get_all_feedback_only(
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1]))  # admin only
):
    return get_all_feedback(db, current_user)


@router.get("/me", response_model=list[FeedbackResponse])
def get_my_feedback_api(
    db: Session = Depends(get_db),
    current_user=Depends(role_required([2]))
):
    return get_my_feedback(db, current_user)


# Admin/Mentor → View assigned feedback
@router.get("/admin", response_model=list[FeedbackResponse])
def get_admin_feedback_only(
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1, 4]))
):
    return get_feedback_for_admin(db, current_user)


@router.post("/reply/admin", response_model=FeedbackResponse)
def reply_feedback_api(
    data: FeedbackReply,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1]))  # admin only
):
    return reply_feedback(db, data, current_user)


#Delete (Admin)
@router.delete("/{feedback_id}")
def delete_feedback_api(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1]))
):
    return delete_feedback(db, feedback_id, current_user)
