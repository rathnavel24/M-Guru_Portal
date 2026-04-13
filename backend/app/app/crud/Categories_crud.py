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

        if not user:   
           raise HTTPException(status_code=404, detail="User not found")

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

        query = self.db.query(Category).filter(Category.status == 1)

        if assessment_type_id:
            query = query.filter(
                Category.assessment_type_id == assessment_type_id
            )

        categories = query.all()

        #  ERROR MESSAGE
        if not categories:
            raise HTTPException(
                status_code=404,
                detail="No categories found"
            )

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
            created_by="MENTOR" if current_user["role"] == 4 else "ADMIN",
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

        if not types:
            raise HTTPException(status_code=404, detail="No assessment types found")
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

    def get_assessment_by_id(self, assessment_id: int, current_user):

        assessment = self.db.query(Assessment).filter(
            Assessment.assessment_id == assessment_id,
            Assessment.status == 1,
        ).first()

        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")

        #  ROLE CHECK
        if current_user["role"] == 4:   # Mentor
            if assessment.mentor_id != current_user["user_id"]:
                raise HTTPException(
                    status_code=403,
                    detail="You can only view your own assessments"
                )

        # Fetch users
        mentor = self.db.query(Users).filter(Users.user_id == assessment.mentor_id).first()
        intern = self.db.query(Users).filter(Users.user_id == assessment.intern_id).first()

        # Fetch categories
        categories = self.db.query(Category).filter(
            Category.assessment_type_id == assessment.assessment_type_id,
            Category.status == 1,
        ).all()

        # Fetch marks
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
    def get_all_assessments(self, intern_id: int = None, mentor_id: int = None, batch: str = None):

        query = self.db.query(Assessment).filter(Assessment.status == 1)

        if intern_id:
            query = query.filter(Assessment.intern_id == intern_id)

        if mentor_id:
            query = query.filter(Assessment.mentor_id == mentor_id)

        # ✅ NEW BATCH FILTER
        if batch:
            query = query.join(
                Users, Users.user_id == Assessment.intern_id
            ).filter(
                Users.batch == batch
            )

        assessments = query.all()

        if not assessments:
            raise HTTPException(status_code=404, detail="No data found for this batch")
        
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

                "intern_name": intern.username if intern else None,
                "batch": intern.batch if intern else None, 
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
        
        if user.type != 4:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Only mentors can create or update assessments"
            )
        assessment_type = self.db.query(AssessmentType).filter(
            AssessmentType.assessment_type_id == data.assessment_type_id
        ).first()

        if not assessment_type:
            raise HTTPException(status_code=404, detail="Invalid assessment type ID")

        intern = self.db.query(Users).filter(
            Users.user_id == data.intern_id
        ).first()

        if not intern:
            raise HTTPException(status_code=404, detail="Invalid intern ID")

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
        input_ids = {item.category_id for item in data.category_marks}
        db_ids = {cat.id for cat in categories}

        if not input_ids.issubset(db_ids):
            raise HTTPException(
                status_code=400,
                detail="Category mismatch. Provide valid categories only"
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
                    detail=f"Invalid category_id: {category_id} for this assessment type"
                )

            #  CHANGE THIS LINE (FIX ERROR)
            if obtained_marks > cat.total_marks:
                raise HTTPException(
                    status_code=400,
                    detail=f"Marks ({obtained_marks}) exceed maximum ({cat.total_marks}) for category '{cat.category_name}'"
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
            "batch":intern.batch,
            "total_obtained": total_obtained,
            "total_marks": total_max,
            "percentage": round((total_obtained / total_max) * 100, 2) if total_max else 0,
            "categories_saved": saved,
            "message": "Assessment saved successfully"
        }
    


from backend.app.app.models.mentor_assessment import Assessment
from backend.app.app.models.mentor_assessment_types import AssessmentType
from backend.app.app.models.portal_users import Users
from backend.app.app.models.mentor_assesment_details import AssessmentDetail

class DashboardCrud:

    def __init__(self, db: Session):
        self.db = db

    def get_dashboard(self, mentor_id: int, batch: str = None):  # ← batch param added

        # ─────────────────────────────
        # BASE INTERN IDS FOR THIS BATCH (if filtered)
        # ─────────────────────────────
        intern_ids = None

        if batch:
            intern_ids = [
                u.user_id for u in self.db.query(Users).filter(
                    Users.batch == batch,
                    Users.type == 2,
                    Users.status == 1
                ).all()
            ]

        def base_filter(query, model=Assessment):
            query = query.filter(
                model.mentor_id == mentor_id,
                model.status == 1
            )
            if intern_ids is not None:
                query = query.filter(model.intern_id.in_(intern_ids))
            return query

        # ─────────────────────────────
        # TOTAL ASSESSMENTS
        # ─────────────────────────────
        total_assessments = base_filter(
            self.db.query(Assessment)
        ).count()

        # ─────────────────────────────
        # INTERNS (DISTINCT)
        # ─────────────────────────────
        interns_assessed = base_filter(
            self.db.query(func.count(func.distinct(Assessment.intern_id)))
        ).scalar()

        # ─────────────────────────────
        # BATCH COUNT
        # ─────────────────────────────
        batches_q = self.db.query(
            func.count(func.distinct(Users.batch))
        ).join(
            Assessment, Assessment.intern_id == Users.user_id
        ).filter(
            Assessment.mentor_id == mentor_id,
            Assessment.status == 1
        )
        if intern_ids is not None:
            batches_q = batches_q.filter(Assessment.intern_id.in_(intern_ids))

        batches = batches_q.scalar() or 0

        # ─────────────────────────────
        # OVERALL AVG
        # ─────────────────────────────
        overall_subq_q = self.db.query(
            func.sum(AssessmentDetail.obtained_marks).label("total")
        ).join(
            Assessment, Assessment.assessment_id == AssessmentDetail.assessment_id
        ).filter(
            Assessment.mentor_id == mentor_id,
            Assessment.status == 1
        )
        if intern_ids is not None:
            overall_subq_q = overall_subq_q.filter(Assessment.intern_id.in_(intern_ids))

        overall_subq = overall_subq_q.group_by(
            AssessmentDetail.assessment_id
        ).subquery()

        overall_avg = self.db.query(
            func.avg(overall_subq.c.total)
        ).scalar() or 0

        overall_avg = round(float(overall_avg), 2)

        # ─────────────────────────────
        # AVG TECHNICAL SCORE
        # ─────────────────────────────
        tech_subq_q = self.db.query(
            func.sum(AssessmentDetail.obtained_marks).label("total")
        ).join(
            Assessment, Assessment.assessment_id == AssessmentDetail.assessment_id
        ).filter(
            Assessment.assessment_type_id == 2,
            Assessment.mentor_id == mentor_id,
            Assessment.status == 1
        )
        if intern_ids is not None:
            tech_subq_q = tech_subq_q.filter(Assessment.intern_id.in_(intern_ids))

        tech_subq = tech_subq_q.group_by(
            AssessmentDetail.assessment_id
        ).subquery()

        avg_technical_score = self.db.query(
            func.avg(tech_subq.c.total)
        ).scalar() or 0

        avg_technical_score = round(float(avg_technical_score), 2)

        # ─────────────────────────────
        # SECTION CARDS
        # ─────────────────────────────
        section_data = []

        types = self.db.query(AssessmentType).filter(
            AssessmentType.status == 1
        ).all()

        for t in types:

            count_q = self.db.query(Assessment).filter(
                Assessment.assessment_type_id == t.assessment_type_id,
                Assessment.mentor_id == mentor_id,
                Assessment.status == 1
            )
            if intern_ids is not None:
                count_q = count_q.filter(Assessment.intern_id.in_(intern_ids))
            total_assessments_type = count_q.count()

            batch_q = self.db.query(
                func.count(func.distinct(Users.batch))
            ).join(
                Assessment, Assessment.intern_id == Users.user_id
            ).filter(
                Assessment.assessment_type_id == t.assessment_type_id,
                Assessment.mentor_id == mentor_id,
                Assessment.status == 1
            )
            if intern_ids is not None:
                batch_q = batch_q.filter(Assessment.intern_id.in_(intern_ids))
            batches_for_type = batch_q.scalar() or 0

            type_subq_q = self.db.query(
                func.sum(AssessmentDetail.obtained_marks).label("total")
            ).join(
                Assessment, Assessment.assessment_id == AssessmentDetail.assessment_id
            ).filter(
                Assessment.assessment_type_id == t.assessment_type_id,
                Assessment.mentor_id == mentor_id,
                Assessment.status == 1
            )
            if intern_ids is not None:
                type_subq_q = type_subq_q.filter(Assessment.intern_id.in_(intern_ids))

            type_subq = type_subq_q.group_by(
                AssessmentDetail.assessment_id
            ).subquery()

            avg_score_type = self.db.query(
                func.avg(type_subq.c.total)
            ).scalar() or 0

            avg_score = (
                round(float(avg_score_type), 2)
                if total_assessments_type
                else 0
            )

            section_data.append({
                "assessment_type": t.assessment_name,
                "assessments": total_assessments_type,
                "avg_score": avg_score,
                "batches": batches_for_type
            })

        # ─────────────────────────────
        # RECENT ASSESSMENTS
        # ─────────────────────────────
        recent_q = self.db.query(Assessment).filter(
            Assessment.mentor_id == mentor_id,
            Assessment.status == 1
        )
        if intern_ids is not None:
            recent_q = recent_q.filter(Assessment.intern_id.in_(intern_ids))

        recent = recent_q.order_by(
            Assessment.created_at.desc()
        ).limit(5).all()

        recent_data = []

        for r in recent:
            intern = self.db.query(Users).filter(
                Users.user_id == r.intern_id
            ).first()

            recent_data.append({
                "assessment_id": r.assessment_id,
                "intern_name": intern.username if intern else None,
                "type": r.assessment_type.assessment_name if r.assessment_type else None,
                "date": r.created_at.isoformat() if r.created_at else None
            })

        # ─────────────────────────────
        # ALL BATCHES FOR DROPDOWN
        # ─────────────────────────────
        all_batches = [
            u.batch for u in self.db.query(Users.batch).join(
                Assessment, Assessment.intern_id == Users.user_id
            ).filter(
                Assessment.mentor_id == mentor_id,
                Assessment.status == 1,
                Users.batch.isnot(None)
            ).distinct().all()
        ]

        # ─────────────────────────────
        # FINAL RESPONSE
        # ─────────────────────────────
        return {
            "total_assessments": total_assessments,
            "interns_assessed": interns_assessed,
            "avg_technical_score": avg_technical_score,
            "batches": batches,
            "overall_avg": overall_avg,
            "sections": section_data,
            "recent_assessments": recent_data,
            "all_batches": all_batches,       # ← dropdown options for frontend
            "active_batch": batch or "all"    # ← currently selected batch
        }
