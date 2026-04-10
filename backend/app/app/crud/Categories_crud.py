from fastapi import HTTPException
from sqlalchemy import and_, case, func, text
from sqlalchemy.orm import Session, aliased
from datetime import datetime, timedelta
from backend.app.app.models.categories import Category
from backend.app.app.models.assessment import Assessment    


from yaml import Mark
from backend.app.app import db

class CategoriesCrud:
    def __init__(self,db: Session):
        self.db=db

    def create_category(self, assessment_type_id: int, category_name: str, created_by: str):

        category = db.Category(
            assessment_type_id=assessment_type_id,
            category_name=category_name,
            created_by=created_by
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        
        return category