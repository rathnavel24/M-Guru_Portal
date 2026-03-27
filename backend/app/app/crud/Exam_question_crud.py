from sqlalchemy.orm import Session
from backend.app.app.models import Assessments,Questions, Options,Section

def create_test(db: Session, data):


    assessment = db.query(Assessments).filter(
        Assessments.name == data.name
    ).first()

    if not assessment:
        assessment = Assessments(
            name=data.name,
            total_questions=len(data.questions),
            pass_mark=int(len(data.questions) * 0.6),  # dynamic
            total_mark=len(data.questions),
            duration_minutes=45,
            level="Easy"
        )

        db.add(assessment)
        db.commit()
        db.refresh(assessment)

    for q in data.questions:

        section = db.query(Section).filter_by(
            section_name=q.section
        ).first()

        if not section:
            section = Section(section_name=q.section)
            db.add(section)
            db.commit()
            db.refresh(section)

        question = Questions(
            question_text=q.q,
            question_section=q.section,
            section_id=section.section_id,
            question_type="mcq",
            assessments_id=assessment.assessment_id
        )

        db.add(question)
        db.commit()
        db.refresh(question)

        options = []
        for idx, opt in enumerate(q.opts):
            options.append(
                Options(
                    question_id=question.question_id,
                    option_label=chr(65 + idx),
                    option_text=opt,
                    is_correct=(idx == q.ans)
                )
            )

        db.add_all(options)
        db.commit()

    return {"message": "Inserted successfully"}

def get_all_questions(db: Session):

    questions = db.query(Questions).all()

    result = []

    for q in questions:
        result.append({
            "id": q.question_id,
            "question": q.question_text,
            "section": q.section.section_name if q.section else None,
            "options": [
                {
                    "id": opt.option_id,
                    "label": opt.option_label,
                    "text": opt.option_text
                }
                for opt in q.user_questions
            ]
        })

    return result


def evaluate_test(db: Session, answers):

    score = 0

    for ans in answers:

        correct = db.query(Options).filter_by(
            question_id=ans.question_id,
            is_correct=True
        ).first()

        if correct and correct.option_id == ans.option_id:
            score += 1

    return score


"""
{
  "questions": [
    {
      "section": "Quantitative - Number System",
      "q": "The HCF of two numbers is 18 and their product is 1944. If one number is 54, the other is:",
      "opts": ["18", "24", "36", "42"],
      "ans": 2
    },
    {
      "section": "Quantitative - Percentages",
      "q": "A student scored 360 marks out of 450. What is the percentage score?",
      "opts": ["75%", "80%", "82%", "84%"],
      "ans": 1
    },
    {
      "section": "Quantitative - Profit and Loss",
      "q": "An article bought for Rs.800 is sold at a profit of 12.5%. Selling price is:",
      "opts": ["Rs.880", "Rs.900", "Rs.920", "Rs.940"],
      "ans": 1
    },
    {
      "section": "Quantitative - Ratio",
      "q": "If A:B = 4:7 and B:C = 3:5, then A:B:C is:",
      "opts": ["12:21:35", "4:7:5", "12:7:15", "8:21:35"],
      "ans": 0
    },
    {
      "section": "Quantitative - Averages",
      "q": "The average of 8 numbers is 24. If one number 32 is removed, the new average becomes:",
      "opts": ["22", "23", "24", "25"],
      "ans": 1
    },
    {
      "section": "Quantitative - Algebra",
      "q": "If x + y = 11 and xy = 24, then x^2 + y^2 =",
      "opts": ["49", "61", "73", "97"],
      "ans": 2
    },
    {
      "section": "Quantitative - Time and Work",
      "q": "A can finish a work in 10 days and B in 15 days. In how many days can they finish it together?",
      "opts": ["5", "6", "7.5", "8"],
      "ans": 1
    },
    {
      "section": "Quantitative - Time and Distance",
      "q": "A car travels 150 km in 3 hours. Its speed is:",
      "opts": ["45 km/h", "50 km/h", "55 km/h", "60 km/h"],
      "ans": 1
    },
    {
      "section": "Quantitative - Simple Interest",
      "q": "Find the simple interest on Rs.5000 at 8% per annum for 3 years.",
      "opts": ["Rs.1000", "Rs.1100", "Rs.1200", "Rs.1300"],
      "ans": 2
    },
    {
      "section": "Quantitative - Compound Interest",
      "q": "A sum of Rs.10000 amounts to Rs.12100 in 2 years at compound interest. The rate is:",
      "opts": ["8%", "9%", "10%", "11%"],
      "ans": 2
    },
    {
      "section": "Quantitative - Mensuration",
      "q": "What is the area of a circle with radius 7 cm? (Use pi = 22/7)",
      "opts": ["144 sq cm", "154 sq cm", "164 sq cm", "174 sq cm"],
      "ans": 1
    },
    {
      "section": "Logical - Series",
      "q": "Find the next term: 5, 11, 19, 29, 41, ?",
      "opts": ["51", "53", "55", "57"],
      "ans": 2
    },
    {
      "section": "Logical - Analogy",
      "q": "Book is to Reading as Fork is to:",
      "opts": ["Drawing", "Writing", "Eating", "Cooking"],
      "ans": 2
    },
    {
      "section": "Logical - Coding Decoding",
      "q": "If CAT is coded as DBU, then DOG is coded as:",
      "opts": ["EPH", "EPI", "FPH", "EPG"],
      "ans": 0
    },
    {
      "section": "Logical - Blood Relations",
      "q": "Pointing to a man, Riya said, \"He is the son of my grandfather's only son.\" How is the man related to Riya?",
      "opts": ["Brother", "Father", "Cousin", "Uncle"],
      "ans": 0
    },
    {
      "section": "Logical - Direction Sense",
      "q": "A person walks 10 m north, then 6 m east, then 10 m south. How far is the person from the starting point?",
      "opts": ["4 m", "6 m", "10 m", "16 m"],
      "ans": 1
    },
    {
      "section": "Logical - Syllogism",
      "q": "Statements: All pens are books. Some books are bags. Which conclusion follows?",
      "opts": ["All bags are pens", "Some bags are pens", "Some books are pens", "No pen is a bag"],
      "ans": 2
    },
    {
      "section": "Logical - Odd One Out",
      "q": "Choose the odd one out.",
      "opts": ["Square", "Rectangle", "Triangle", "Circle"],
      "ans": 1
    },
    {
      "section": "Logical - Seating",
      "q": "Five people A, B, C, D and E sit in a row. A is left of B, C is right of D, and B is right of E. Who can be in the middle?",
      "opts": ["A", "B", "C", "E"],
      "ans": 1
    },
    {
      "section": "Data Interpretation - Table",
      "q": "A company sold 120, 150, 180 and 210 units in four quarters. Average quarterly sales are:",
      "opts": ["155", "160", "165", "170"],
      "ans": 2
    },
    {
      "section": "Data Interpretation - Percentages",
      "q": "Out of 200 students, 120 passed. The pass percentage is:",
      "opts": ["50%", "55%", "60%", "65%"],
      "ans": 2
    },
    {
      "section": "Data Interpretation - Pie Chart",
      "q": "If 25% of a budget of Rs.80000 is spent on transport, the transport expense is:",
      "opts": ["Rs.18000", "Rs.20000", "Rs.22000", "Rs.25000"],
      "ans": 1
    },
    {
      "section": "Data Interpretation - Bar Graph",
      "q": "Production in two months is 320 and 280 units. What is the difference?",
      "opts": ["20", "30", "40", "50"],
      "ans": 2
    },
    {
      "section": "Verbal - Synonyms",
      "q": "Choose the synonym of \"Brief\".",
      "opts": ["Short", "Bright", "Broad", "Swift"],
      "ans": 0
    },
    {
      "section": "Verbal - Antonyms",
      "q": "Choose the antonym of \"Expand\".",
      "opts": ["Increase", "Stretch", "Contract", "Enlarge"],
      "ans": 2
    },
    {
      "section": "Verbal - Grammar",
      "q": "Choose the correct sentence.",
      "opts": ["He go to office daily.", "He goes to office daily.", "He going to office daily.", "He gone to office daily."],
      "ans": 1
    },
    {
      "section": "Verbal - Vocabulary",
      "q": "Choose the word closest in meaning to \"Diligent\".",
      "opts": ["Lazy", "Careful", "Hardworking", "Careless"],
      "ans": 2
    },
    {
      "section": "Verbal - Sentence Completion",
      "q": "She was tired, ____ she completed the assignment on time.",
      "opts": ["because", "but", "although", "unless"],
      "ans": 1
    },
    {
      "section": "Verbal - Reading Logic",
      "q": "If all roses are flowers and some flowers fade quickly, which statement is definitely true?",
      "opts": ["All flowers are roses", "Some roses fade quickly", "All roses are flowers", "No roses fade quickly"],
      "ans": 2
    }
  ]
}
"""