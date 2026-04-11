from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.app.models.mentor_assesment_details import AssessmentDetail
from backend.app.app.models.mentor_assessment_categories import Category
from backend.app.app.models.mentor_assessment import Assessment
from backend.app.app.models.mentor_assessment_types import AssessmentType
from backend.app.app.models.portal_users import Users


class CategoriesCrud:

    def __init__(self, db: Session):
        self.db = db

    def create_category(self, data, current_user):

        if self.db.query(Category).filter(
            func.lower(Category.category_name) == func.lower(data.category_name)
        ).first():
            raise HTTPException(status_code=400, detail="Category with this name already exists")

        user = self.db.query(Users).filter(
            Users.user_id == current_user["user_id"]
        ).first()

        assessment_type = self.db.query(AssessmentType).filter(
            AssessmentType.assessment_type_id == data.assessment_type_id
        ).first()

        if not assessment_type:
            raise HTTPException(status_code=404, detail="Assessment type not found")

        category = Category(
            assessment_type_id=assessment_type.assessment_type_id,
            category_name=data.category_name,
            total_marks=data.total_marks,
            created_by="MENTOR" if user.type == 4 else "ADMIN",
        )

        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        return {
            "category_id": category.id,
            "category_name": category.category_name,
            "total_marks": category.total_marks,
            "assessment_type": assessment_type.assessment_name,
        }

    def get_all_categories(self, assessment_type_id: int = None):
        categories = self.db.query(Category).filter(Category.status == 1).all()

        if assessment_type_id:
            query = query.filter(Category.assessment_type_id == assessment_type_id)


        return [
            {
                "category_id": cat.id,
                "category_name": cat.category_name,
                "total_marks": cat.total_marks,
                "assessment_type": cat.assessment_type.assessment_name if cat.assessment_type else None,
                "assessment_type_id": cat.assessment_type_id,
            }
            for cat in categories
        ]


class AssessmentCrud:

    def __init__(self, db: Session):
        self.db = db

    def get_intern_by_name_batch(self, name: str, batch: str):

        intern = self.db.query(Users).filter(
            Users.username == name,
            Users.batch == batch,
            Users.type == 2,
            Users.status == 1
        ).first()

        if not intern:
            raise HTTPException(
                status_code=404,
                detail="Intern not found with given name and batch"
            )

        return {
            "intern_name": intern.username,
            "specialization": intern.tech_stack,
            "batch": intern.batch
        }
    
    def create_assessment_type(self, data, current_user):

        existing = self.db.query(AssessmentType).filter(
            func.lower(AssessmentType.assessment_name) == func.lower(data.assessment_name)
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Assessment type with this name already exists")

        assessment_type = AssessmentType(
            assessment_name=data.assessment_name,
            created_by="MENTOR" if current_user["type"] == 4 else "ADMIN",
        )

        self.db.add(assessment_type)
        self.db.commit()
        self.db.refresh(assessment_type)

        return {
            "assessment_type_id": assessment_type.assessment_type_id,
            "assessment_name": assessment_type.assessment_name,
            "message": "Assessment type created successfully",
        }
    def get_all_assessment_types(self, assessment_type_id: int = None):

        query = self.db.query(AssessmentType).filter(
            AssessmentType.status == 1
        )

        if assessment_type_id:
            query = query.filter(
                AssessmentType.assessment_type_id == assessment_type_id
            )

        types = query.all()

        return [
            {
                "assessment_type_id": assessment.assessment_type_id,
                "assessment_name": assessment.assessment_name,
            }
            for assessment in types
    ]
          

    # # ────────────────────────────────────────────────
    # #  2. CREATE ASSESSMENT
    # # ────────────────────────────────────────────────
    # def create_assessment(self, data, current_user):

    #     user = self.db.query(Users).filter(
    #         Users.user_id == current_user["user_id"]
    #     ).first()

    #     assessment_type = self.db.query(AssessmentType).filter(
    #         AssessmentType.assessment_type_id == data.assessment_type_id
    #     ).first()


    #     if not assessment_type:
    #         raise HTTPException(status_code=404, detail="Assessment type not found")

    #     intern = self.db.query(Users).filter(
    #         Users.user_id == data.intern_id
    #     ).first()

    #     category = self.db.query(Category).filter(
    #         Category.assessment_type_id == data.assessment_type_id
    #     ).first()

    #     if not intern:
    #         raise HTTPException(status_code=404, detail="Intern not found")

    #     existing = self.db.query(Assessment).filter(
    #         Assessment.intern_id == data.intern_id,
    #         Assessment.mentor_id == data.mentor_id,
    #         Assessment.assessment_type_id == data.assessment_type_id,
    #         Assessment.status == 1,
    #     ).first()

    #     if existing:
    #         raise HTTPException(
    #             status_code=400,
    #             detail=f"Assessment of type '{assessment_type.assessment_name}' already exists for this intern",
    #         )

    #     assessment = Assessment(
    #         intern_id=data.intern_id,
    #         mentor_id=data.mentor_id,
    #         remarks=data.remarks,
    #         task_details=data.task_details,
    #         status=1,
    #         created_by="MENTOR" if user.type == 4 else "ADMIN",
    #         assessment_type_id=data.assessment_type_id,
    #     )

    #     self.db.add(assessment)
    #     self.db.commit()
    #     self.db.refresh(assessment)


    #     # Get ALL categories (IMPORTANT FIX)
    #     categories = self.db.query(Category).filter(
    #         Category.assessment_type_id == data.assessment_type_id
    #     ).all()

    #     return {
    #         "assessment_id": assessment.assessment_id,
    #         "assessment_type": assessment_type.assessment_name,
    #         "intern_id": data.intern_id,
    #         "categories": [
    #             {
    #                 "category_id": cat.id,
    #                 "category_name": cat.category_name,
    #                 "total_marks": cat.total_marks
    #             }
    #             for cat in categories
    #         ],
    #         "message": "Assessment created successfully"
    #     }
    # # ────────────────────────────────────────────────
    # #  3. ADD / UPDATE MARKS PER CATEGORY
    # # ────────────────────────────────────────────────
    # def add_assessment_marks(self, assessment_id: int, category_marks: list, current_user):

    #     assessment = self.db.query(Assessment).filter(
    #         Assessment.assessment_id == assessment_id,
    #         Assessment.status == 1,
    #     ).first()

    #     if not assessment:
    #         raise HTTPException(status_code=404, detail="Assessment not found")

    #     valid_categories = self.db.query(Category).filter(
    #         Category.assessment_type_id == assessment.assessment_type_id,
    #         Category.status == 1,
    #     ).all()

    #     valid_category_ids = {cat.id: cat for cat in valid_categories}

    #     saved = []

    #     for item in category_marks:
    #         category_id = item.get("category_id")
    #         obtained_marks = item.get("marks")

    #         cat = valid_category_ids.get(category_id)
    #         if not cat:
    #             raise HTTPException(
    #                 status_code=400,
    #                 detail=f"Category {category_id} does not belong to this assessment type",
    #             )

    #         if obtained_marks > cat.total_marks:
    #             raise HTTPException(
    #                 status_code=400,
    #                 detail=f"Marks ({obtained_marks}) exceed total marks ({cat.total_marks}) for '{cat.category_name}'",
    #             )

    #         detail = self.db.query(AssessmentDetail).filter(
    #             AssessmentDetail.assessment_id == assessment_id,
    #             AssessmentDetail.category_id == category_id,
    #         ).first()

    #         if detail:
    #             detail.obtained_marks = obtained_marks
    #         else:
    #             detail = AssessmentDetail(
    #                 assessment_id=assessment_id,
    #                 category_id=category_id,
    #                 obtained_marks=obtained_marks,
    #             )
    #             self.db.add(detail)

    #         saved.append({
    #             "category_id": category_id,
    #             "category_name": cat.category_name,
    #             "obtained_marks": obtained_marks,
    #             "total_marks": cat.total_marks,
    #         })

    #     self.db.flush()
    #     all_details = self.db.query(AssessmentDetail).filter(
    #         AssessmentDetail.assessment_id == assessment_id
    #     ).all()
    #     assessment.obtained_marks = sum(d.obtained_marks or 0 for d in all_details)

    #     self.db.commit()

    #     return {
    #         "assessment_id": assessment_id,
    #         "total_obtained": assessment.obtained_marks,
    #         "categories_saved": saved,
    #         "message": "Marks saved successfully",
    #     }

    # ────────────────────────────────────────────────
    #  4. GET ASSESSMENT BY ID  
    # ────────────────────────────────────────────────

    def get_assessment_by_id(self, assessment_id: int):

        assessment = self.db.query(Assessment).filter(
            Assessment.assessment_id == assessment_id,
            Assessment.status == 1,
        ).first()

        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")

        intern = self.db.query(Users).filter(Users.user_id == assessment.intern_id).first()
        mentor = self.db.query(Users).filter(Users.user_id == assessment.mentor_id).first()

        categories = self.db.query(Category).filter(
            Category.assessment_type_id == assessment.assessment_type_id,
            Category.status == 1,
        ).all()

        details = self.db.query(AssessmentDetail).filter(
            AssessmentDetail.assessment_id == assessment_id
        ).all()

        detail_map = {d.category_id: d for d in details}

        category_list = []
        total_obtained = 0
        total_max = 0

        for cat in categories:
            detail = detail_map.get(cat.id)
            obtained = detail.obtained_marks if detail else None
            total_obtained += obtained or 0
            total_max += cat.total_marks or 0

            category_list.append({
                "category_id": cat.id,
                "category_name": cat.category_name,
                "obtained_marks": obtained,
                "total_marks": cat.total_marks,
            })

        return {
            "assessment_id": assessment.assessment_id,
            "assessment_type": assessment.assessment_type.assessment_name if assessment.assessment_type else None,

            "intern_id": assessment.intern_id,
            "intern_name": intern.username if intern else None,
            "specialization": intern.tech_stack if intern else None,
            "batch": intern.batch if intern else None,

            "mentor_id": assessment.mentor_id,
            "mentor_name": mentor.username if mentor else None,

            "remarks": assessment.remarks,
            "task_details": assessment.task_details,

            "total_obtained": total_obtained,
            "total_marks": total_max,
            "percentage": round((total_obtained / total_max) * 100, 2) if total_max else 0,

            "categories": category_list,
        }

    # ────────────────────────────────────────────────
    #  5. GET ALL ASSESSMENTS
    # ────────────────────────────────────────────────
    def get_all_assessments(self, intern_id: int = None, mentor_id: int = None):

        query = self.db.query(Assessment).filter(Assessment.status == 1)

        if intern_id:
            query = query.filter(Assessment.intern_id == intern_id)

        if mentor_id:
            query = query.filter(Assessment.mentor_id == mentor_id)

        assessments = query.all()
        response = []

        for assessment in assessments:
            intern = self.db.query(Users).filter(Users.user_id == assessment.intern_id).first()
            mentor = self.db.query(Users).filter(Users.user_id == assessment.mentor_id).first()

            categories = self.db.query(Category).filter(
                Category.assessment_type_id == assessment.assessment_type_id,
                Category.status == 1,
            ).all()

            total_max = sum(cat.total_marks or 0 for cat in categories)

            details = self.db.query(AssessmentDetail).filter(
                AssessmentDetail.assessment_id == assessment.assessment_id
            ).all()
            total_obtained = sum(d.obtained_marks or 0 for d in details)

            response.append({
                "assessment_id": assessment.assessment_id,
                "assessment_type": assessment.assessment_type.assessment_name if assessment.assessment_type else None,

                # "intern_id": assessment.intern_id,
                "intern_name": intern.username if intern else None,

                # "mentor_id": assessment.mentor_id,
                "mentor_name": mentor.username if mentor else None,

                "total_obtained": total_obtained,
                "total_marks": total_max,
                "percentage": round((total_obtained / total_max) * 100, 2) if total_max else 0,

                "remarks": assessment.remarks,
                "created_at": assessment.created_at,
            })

        return response

    # # ────────────────────────────────────────────────
    # #  6. GET INTERN ASSESSMENT SUMMARY
    # # ────────────────────────────────────────────────
    # def get_intern_assessment_summary(self, intern_id: int):

    #     intern = self.db.query(Users).filter(Users.user_id == intern_id).first()
    #     if not intern:
    #         raise HTTPException(status_code=404, detail="Intern not found")

    #     assessments = self.db.query(Assessment).filter(
    #         Assessment.intern_id == intern_id,
    #         Assessment.status == 1,
    #     ).all()

    #     all_types = self.db.query(AssessmentType).filter(AssessmentType.status == 1).all()
    #     type_map = {at.assessment_type_id: at.assessment_name for at in all_types}

    #     summary = []
    #     grand_obtained = 0
    #     grand_max = 0

    #     for assessment in assessments:
    #         mentor = self.db.query(Users).filter(Users.user_id == assessment.mentor_id).first()

    #         categories = self.db.query(Category).filter(
    #             Category.assessment_type_id == assessment.assessment_type_id,
    #             Category.status == 1,
    #         ).all()

    #         details = self.db.query(AssessmentDetail).filter(
    #             AssessmentDetail.assessment_id == assessment.assessment_id
    #         ).all()

    #         detail_map = {d.category_id: d for d in details}
    #         total_max = sum(cat.total_marks or 0 for cat in categories)
    #         total_obtained = sum(
    #             (detail_map[cat.id].obtained_marks or 0)
    #             for cat in categories
    #             if cat.id in detail_map
    #         )

    #         grand_obtained += total_obtained
    #         grand_max += total_max

    #         category_list = [
    #             {
    #                 "category_id": cat.id,
    #                 "category_name": cat.category_name,
    #                 "obtained_marks": detail_map.get(cat.id).obtained_marks if cat.id in detail_map else None,
    #                 "total_marks": cat.total_marks,
    #             }
    #             for cat in categories
    #         ]

    #         summary.append({
    #             "assessment_id": assessment.assessment_id,
    #             "assessment_type": type_map.get(assessment.assessment_type_id, "Unknown"),
    #             "mentor_name": mentor.username if mentor else None,
    #             "remarks": assessment.remarks,
    #             "task_details": assessment.task_details,
    #             "total_obtained": total_obtained,
    #             "total_marks": total_max,
    #             "percentage": round((total_obtained / total_max) * 100, 2) if total_max else 0,
    #             "categories": category_list,
    #         })

    #     return {
    #         "intern_id": intern_id,
    #         "intern_name": intern.username,
    #         "specialization": intern.tech_stack if hasattr(intern, "tech_stack") else None,
    #         "batch": intern.batch if hasattr(intern, "batch") else None,
    #         "grand_total_obtained": grand_obtained,
    #         "grand_total_marks": grand_max,
    #         "grand_percentage": round((grand_obtained / grand_max) * 100, 2) if grand_max else 0,
    #         "assessments": summary,
    #     }

    # ── Alias kept for compatibility ──
    # def get_assessment_with_categories(self, assessment_id: int, current_user):
    #     return self.get_assessment_by_id(assessment_id, current_user)
    
    def save_assessment(self, data, current_user):

    # ────────────────────────────────────────────────
    # 1. VALIDATIONS
    # ────────────────────────────────────────────────

        user = self.db.query(Users).filter(
            Users.user_id == current_user["user_id"]
        ).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        assessment_type = self.db.query(AssessmentType).filter(
            AssessmentType.assessment_type_id == data.assessment_type_id
        ).first()

        if not assessment_type:
            raise HTTPException(status_code=404, detail="Assessment type not found")

        intern = self.db.query(Users).filter(
            Users.user_id == data.intern_id
        ).first()

        if not intern:
            raise HTTPException(status_code=404, detail="Intern not found")

        # ────────────────────────────────────────────────
        # 2. CHECK EXISTING (IMPORTANT)
        # ────────────────────────────────────────────────

        assessment = self.db.query(Assessment).filter(
            Assessment.intern_id == data.intern_id,
            Assessment.mentor_id == data.mentor_id,
            Assessment.assessment_type_id == data.assessment_type_id,
            Assessment.status == 1,
        ).first()

        # ────────────────────────────────────────────────
        # 3. CREATE OR UPDATE ASSESSMENT
        # ────────────────────────────────────────────────

        if not assessment:
            assessment = Assessment(
                intern_id=data.intern_id,
                mentor_id=data.mentor_id,
                remarks=data.remarks,
                task_details=data.task_details,
                status=1,
                created_by="MENTOR" if user.type == 4 else "ADMIN",
                assessment_type_id=data.assessment_type_id,
                assessment_date=data.assessment_date 
            )
            self.db.add(assessment)
            self.db.flush()   # get assessment_id without commit

        else:
            # Update existing
            assessment.remarks = data.remarks
            assessment.task_details = data.task_details
            assessment.assessment_date = data.assessment_date

        # ────────────────────────────────────────────────
        # 4. GET VALID CATEGORIES
        # ────────────────────────────────────────────────

        categories = self.db.query(Category).filter(
            Category.assessment_type_id == data.assessment_type_id,
            Category.status == 1,
        ).all()

        valid_category_map = {cat.id: cat for cat in categories}

        # Optional strict validation
        if len(data.category_marks) != len(categories):
            raise HTTPException(
                status_code=400,
                detail="All categories must be scored"
            )

        # ────────────────────────────────────────────────
        # 5. SAVE / UPDATE MARKS
        # ────────────────────────────────────────────────

        saved = []

        for item in data.category_marks:
            category_id = item.category_id
            obtained_marks = item.marks

            cat = valid_category_map.get(category_id)

            if not cat:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid category_id: {category_id}"
                )

            if obtained_marks > cat.total_marks:
                raise HTTPException(
                    status_code=400,
                    detail=f"Marks ({obtained_marks}) exceed total ({cat.total_marks}) for {cat.category_name}"
                )

            detail = self.db.query(AssessmentDetail).filter(
                AssessmentDetail.assessment_id == assessment.assessment_id,
                AssessmentDetail.category_id == category_id,
            ).first()

            if detail:
                detail.obtained_marks = obtained_marks
            else:
                detail = AssessmentDetail(
                    assessment_id=assessment.assessment_id,
                    category_id=category_id,
                    obtained_marks=obtained_marks,
                )
                self.db.add(detail)

            saved.append({
                "category_id": category_id,
                "category_name": cat.category_name,
                "obtained_marks": obtained_marks,
                "total_marks": cat.total_marks,
            })

        # ────────────────────────────────────────────────
        # 6. CALCULATE TOTAL
        # ────────────────────────────────────────────────

        self.db.flush()

        all_details = self.db.query(AssessmentDetail).filter(
            AssessmentDetail.assessment_id == assessment.assessment_id
        ).all()

        total_obtained = sum(d.obtained_marks or 0 for d in all_details)
        total_max = sum(cat.total_marks or 0 for cat in categories)

        assessment.obtained_marks = total_obtained

        # ────────────────────────────────────────────────
        # 7. COMMIT
        # ────────────────────────────────────────────────

        self.db.commit()

        # ────────────────────────────────────────────────
        # 8. RESPONSE
        # ────────────────────────────────────────────────

        return {
            "assessment_id": assessment.assessment_id,
            "assessment_type": assessment_type.assessment_name,
            "intern_id": assessment.intern_id,
            "total_obtained": total_obtained,
            "total_marks": total_max,
            "percentage": round((total_obtained / total_max) * 100, 2) if total_max else 0,
            "categories_saved": saved,
            "message": "Assessment saved successfully"
        }
