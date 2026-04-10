from fastapi import HTTPException
from sqlalchemy import and_, case, func, text
from sqlalchemy.orm import Session, aliased
from datetime import datetime, timedelta
from backend.app.app.models.mentor_assessment_categories import Category
from backend.app.app.models.mentor_assessment import Assessment    


from yaml import Mark
from backend.app.app import db
from backend.app.app.models.mentor_assessment_types import AssessmentType
from backend.app.app.models.mentor_assessment_types import AssessmentType

class CategoriesCrud:

    def __init__(self,db: Session):
        self.db=db


    def create_category(self, data, current_user):

        if self.db.query(Category).filter(
            func.lower(Category.category_name) == func.lower(data.category_name),
            
        ).first():
            raise HTTPException(status_code=400, detail="Category with this name already exists")   

        category = Category(
            category_name=data.category_name,
            total_marks=data.total_marks,
            created_by=str(current_user["user_id"])
        )

        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        return category


    def get_all_categories(self):
        return self.db.query(Category).filter(Category.status == 1).all()


class AssessmentCrud:

    def __init__(self, db: Session):
        self.db = db

    def create_assessment(self, data, current_user):

        assessment = Assessment(
            assessment_type_id=data.assessment_type_id,
            category_id=data.category_id,
            intern_id=data.intern_id,
            mentor_id=data.mentor_id,
            remarks=data.remarks,
            task_details=data.task_details,
            obtained_marks=data.obtained_marks,
            created_by=str(current_user["user_id"])
        )

        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)

        return assessment

    def create_assessment_type(self, data, current_user):

        assessment_type = AssessmentType(
            assessment_name=data.assessment_name,
            created_by=str(current_user["user_id"])
        )

        self.db.add(assessment_type)
        self.db.commit()
        self.db.refresh(assessment_type)

        return assessment_type

 


    def get_all_assessments(self):
        return self.db.query(Assessment).filter(Assessment.status == 1).all()


    def get_assessment_by_id(self, assessment_id: int):
        assessment = self.db.query(Assessment).filter(
            Assessment.assessment_id == assessment_id,
            Assessment.status == 1
        ).first()

        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")

        return assessment
    
    def get_assessment_with_categories(self, assessment_id: int):

        assessment = self.db.query(Assessment).filter(
            Assessment.assessment_id == assessment_id,
            Assessment.status == 1
        ).first()

        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")

        # get all categories
        categories = self.db.query(Category).filter(
            Category.status == 1
        ).all()

        result = {
            "assessment_id": assessment.assessment_id,
            "intern_id": assessment.intern_id,
            "mentor_id": assessment.mentor_id,
            "remarks": assessment.remarks,
            "obtained_marks": assessment.obtained_marks,   
            "categories": []
        }

        for cat in categories:
            result["categories"].append({
                "category_id": cat.id,
                "category_name": cat.category_name,
                "total_marks": cat.total_marks
            })

        return result