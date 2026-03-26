from fastapi import FastAPI
<<<<<<< HEAD
from backend.app.app.api.endpoints import user
from backend.app.app.api.endpoints import Exam_assessment
from backend.app.app.api.endpoints import Exam_question
from backend.app.app.api.endpoints import Exam_option
from backend.app.app.api.endpoints import Exam_attempt
from backend.app.app.api.endpoints import Exam_answer
from backend.app.app.api.endpoints import Exam_section
=======
from backend.app.app.api.endpoints import user,attendance
from backend.app.app.api.endpoints import Exam_user

>>>>>>> 4b02df20cba7112f653b2b57d1abbf68d589ba98

app = FastAPI()


app.include_router(user.router)
<<<<<<< HEAD
app.include_router(Exam_assessment.router)
app.include_router(Exam_question.router)
app.include_router(Exam_option.router)
app.include_router(Exam_attempt.router)
app.include_router(Exam_answer.router)
app.include_router(Exam_section.router)
=======
app.include_router(attendance.router)
app.include_router(Exam_user.router)
>>>>>>> 4b02df20cba7112f653b2b57d1abbf68d589ba98
