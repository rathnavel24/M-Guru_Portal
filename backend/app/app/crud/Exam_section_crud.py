from sqlalchemy.orm import Session
from backend.app.app.models.Exam_section import Section

class SectionCrud:
    def __init__(self, db: Session):
        self.db = db

    def get_sections(self):
        return self.db.query(Section).all()

    def get_section_by_id(self, section_id: int):
        return self.db.query(Section).filter(
            Section.section_id == section_id
        ).first()

