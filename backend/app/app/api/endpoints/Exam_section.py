from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.app.api.deps import get_db
from backend.app.app.crud.Exam_section_crud import SectionCrud
from backend.app.app.schemas.Exam_section_schemas import SectionResponse

router = APIRouter(tags=["Section"])

@router.get("/api/sections")
def get_sections(db: Session = Depends(get_db)):

    try:
        return SectionCrud(db).get_sections()
    except Exception as e:
        return {"error":
                str(e)}
    
@router.get("/api/sections/{section_id}")
def get_section(section_id: int, db: Session = Depends(get_db)):

    try:
        return SectionCrud(db).get_section_by_id(section_id)
    except Exception as e:
        return {"error": str(e)}