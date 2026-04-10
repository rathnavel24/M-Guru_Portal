from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.app.api.deps import get_db
from backend.app.app.crud.Exam_option_crud import OptionsCrud

router = APIRouter(tags=["Options"])

@router.get("/api/options/{question_id}")
def get_options(question_id: int, db: Session = Depends(get_db)):
    try:
        return OptionsCrud(db).get_options(question_id)
    except Exception as e:
        return{"error": str(e)}