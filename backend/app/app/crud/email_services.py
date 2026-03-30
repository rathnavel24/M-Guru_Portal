import aiosmtplib
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader
import qrcode
from sqlalchemy.orm import Session
# from backend.app.app.main import is_overdue
from backend.app.app.models import Users, Pay_email,Fee
from backend.app.app.models.Exam_attempt import Attempts
from backend.app.app.schemas.user_schema import Paymentmail
from pathlib import Path
from email.message import EmailMessage
from datetime import datetime
import random
import string
import os 
from dotenv import load_dotenv
from backend.app.app.models.Exam_user import ExamUsers
import smtplib
from email.mime.text import MIMEText
import os
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(os.path.join(BASE_DIR,  "../templates")))  # load html file


async def send_email(msg: EmailMessage):
    await aiosmtplib.send(
        msg,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=os.getenv("user"),
        password=os.getenv("password"),
    )


# def generate_invoice_id():
#     random_inv = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
#     return f"MG-{random_inv}"

def generate_invoice_id(db: Session):
    last_invoice = (
        db.query(Pay_email.invoice_no)
        .order_by(Pay_email.invoice_no.desc())
        .first()
    )

    if last_invoice and last_invoice[0]:
        last_number = int(last_invoice[0].split("-")[1])
        new_number = last_number + 1
    else:
        new_number = 1

    return f"MG-{new_number:06d}"


async def send_invoice_email(data: Paymentmail, current_user, db: Session):
    sender_id = current_user["user_id"]


async def send_invoice_email(data: Paymentmail, current_user ,db: Session):
    sender_id =current_user["user_id"]

    try:
        user = (
            db.query(Users.username, Users.email)
            .filter(Users.user_id == data.user_id)
            .first()
        )

        if not user:
            raise ValueError("User not found")

        if data.email_type == "1":
            # 🧾 NEW INVOICE
            gen_invoice_id = generate_invoice_id(db)

            account_name = data.account_name
            account_no = data.account_no
            ifsc = data.ifsc
            bank_name = data.bank_name
            amount = data.amount
            due_date = data.due_date

            status = 1  # Sent
            is_complete = False

        else:
            # 🔍 FETCH EXISTING INVOICE
            if not data.invoice_no:
                raise ValueError("Invoice number is required")
            existing = db.query(Pay_email).filter(
                Pay_email.invoice_no == (data.invoice_no or "").strip(),
                Pay_email.email_type == "1"
            ).first()
            if not existing:
                 raise ValueError("Invalid invoice ID")

            gen_invoice_id = existing.invoice_no

            # 🔐 Use DB values (not frontend)
            account_name = existing.account_name
            account_no = existing.account_no
            ifsc = existing.ifsc
            bank_name = existing.bank_name
            amount = existing.amount
            due_date = existing.due_date
        

            # 🔔 REMINDER
            if data.email_type == "2":
                status = 3  # Reminder sent
                is_complete = existing.is_complete

            # ✅ CONFIRMATION
            elif data.email_type == "3":
                if existing.is_complete:
                    raise ValueError("Payment already completed")

                existing.status = 2
                if existing.status == 2:
                    fee = db.query(Fee).filter(Fee.user_id == existing.to_id).first()
                if not fee:
                    raise ValueError("Fee record not found")
                # Add invoice amount to paid_amount
                fee.paid_amount = (fee.paid_amount or 0) + existing.amount
                existing.is_complete = True
                existing.updated_at = datetime.now()
                db.commit()
                status = 2
                is_complete = True

        if data.email_type == "1":
            template = env.get_template("payment_invoice_mail.html")
            subject =  f"Invoice - {gen_invoice_id}"
        elif data.email_type == "2":
            template = env.get_template("payment_remainder_mail.html")
            subject =  f"Invoice  - {gen_invoice_id}"
        else:
            template = env.get_template("payment_confirmation_mail.html")
            subject = f"Invoice - {gen_invoice_id}"

        html_content = template.render(
            name=user.username,
            email=user.email,
            amount=amount,
            invoice_id=gen_invoice_id,
            note=(data.note  if data.email_type == "1" else existing.note) or "",
            date=datetime.now().strftime("%d %b %Y"),
            due_date=due_date,
            account_name=account_name,
            account_no=account_no,
            ifsc=ifsc,
            bank_name=bank_name,
        )

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = os.getenv("user")
        msg["To"] = user.email

        if not user.email:
            raise ValueError("User email missing")

        msg.set_content("Please view this email in HTML format.")
        msg.add_alternative(html_content, subtype="html")

        await send_email(msg)
        
        add_log = Pay_email(
            invoice_no=gen_invoice_id,
            from_id=sender_id,
            to_id=data.user_id,
            # note=data.note,
            note = str(data.note or existing.note or ""),
            email_type=data.email_type,
            amount=amount,
            due_date=due_date,
            account_name=account_name,
            account_no=account_no,
            ifsc=ifsc,
            bank_name=bank_name,
            is_complete=is_complete,
            status=status,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="ADMIN",
        )
        db.add(add_log)
        db.commit()

        return {"message": "Email sent successfully"}

    except Exception as e:
        db.rollback()
        print(" Email Error:", str(e))

def payment_confirmation(invoice_no:str,db:Session):
    user = db.query(Pay_email).filter(Pay_email.invoice_no == invoice_no).first()
    if not user:
        return "Invalid invoice no"
    
    user.status = 2
    user.is_complete = True
    user.updated_at = datetime.now()

    db.commit()
    db.refresh(user)

def get_bankdetail(invoice_no: str, db: Session):
    bank_details = db.query(
        Pay_email.bank_name,
        Pay_email.account_name,
        Pay_email.account_no,
        Pay_email.ifsc
    ).filter(Pay_email.invoice_no == invoice_no).first()

    if not bank_details:
        return {"message": "Enter Valid Invoice number"}

    return {
        "bank_name": bank_details.bank_name,
        "account_name": bank_details.account_name,
        "account_no": bank_details.account_no,
        "ifsc": bank_details.ifsc
    }
async def check_and_notify(db: Session):
    payments = db.query(Pay_email).filter(
        Pay_email.email_type == "1"  
    ).all()
    
    # today = 2  # For testing; use datetime.utcnow().day in production
    today = datetime.utcnow().day
    
    for payment in payments:
        print(f"Checking: {payment.invoice_no}, is_complete={payment.is_complete}, stage={payment.reminder_stage}")

        # Handle None/empty is_complete
        if payment.is_complete is True or payment.is_complete == 1:
            print(f"Skipping {payment.invoice_no} - already complete")
            continue

        user = db.query(Users).filter(Users.user_id == payment.to_id).first()
        if not user:
            print(f"No user found for to_id={payment.to_id}")
            continue

        # FIRST REMINDER
        if today == 2 and (payment.reminder_stage == 0 or payment.reminder_stage is None):
            print(f"Sending first reminder for {payment.invoice_no}")
            
            data = Paymentmail(
                user_id=payment.to_id,
                invoice_no=payment.invoice_no,
                email_type="2",
                note=str(payment.note or ""),
                account_name=payment.account_name,
                account_no=payment.account_no,
                ifsc=payment.ifsc,
                bank_name=payment.bank_name,
                amount=payment.amount,
                due_date=payment.due_date
            )

            current_user = {"user_id": payment.from_id}

            try:
                await send_invoice_email(data, current_user, db)
                payment.reminder_stage = 1
                payment.last_reminder_at = datetime.utcnow()
                db.commit()
                print(f"Reminder sent for {payment.invoice_no}")
            except Exception as e:
                print(f"Failed to send reminder: {e}")
                db.rollback()

        # FINAL REMINDER
        
        elif today == 20 and payment.reminder_stage == 1:
            print(f"Sending final reminder for {payment.invoice_no}")

            data = Paymentmail(
                user_id=payment.to_id,
                invoice_no=payment.invoice_no,
                email_type="2",  # still reminder type
                note=str(payment.note or ""),
                account_name=payment.account_name,
                account_no=payment.account_no,
                ifsc=payment.ifsc,
                bank_name=payment.bank_name,
                amount=payment.amount,
                due_date=payment.due_date
            )

            current_user = {"user_id": payment.from_id}

            try:
                await send_invoice_email(data, current_user, db)

                # move to next stage
                payment.reminder_stage = 2
                payment.last_reminder_at = datetime.utcnow()

                db.commit()
                print(f"Final reminder sent for {payment.invoice_no}")

            except Exception as e:
                print(f"Failed to send final reminder: {e}")
                db.rollback()

    db.commit()


##############################
# import os
# import smtplib
# from email.mime.text import MIMEText

# def send_notify_email(to_email: str, username: str, stage: str):
#     subject = f"Payment Reminder: {stage}"

#     body = f"""
# Hi {username},

# {stage}

# Your payment is still pending. Please complete it before the due date.

# Regards,  
# Team
# """

#     sender_email = os.getenv("EMAIL_USER")
#     sender_password = os.getenv("EMAIL_PASS")

#     msg = MIMEText(body)
#     msg['Subject'] = subject
#     msg['From'] = sender_email
#     msg['To'] = to_email

#     with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
#         server.login(sender_email, sender_password)
#         server.send_message(msg)

# from datetime import datetime

# # def check_and_notify(db):

# #     payments = db.query(Pay_email).all()
# #     print("Checking payment reminders...")

# #     today = datetime.utcnow().day  # current date (1–31)

# #     for payment in payments:

# #         # ❌ skip completed
# #         if payment.is_complete:
# #             continue

# #         if not payment.due_date:
# #             continue

# #         if payment.last_reminder_at and payment.last_reminder_at.date() == datetime.utcnow().date():
# #             continue

# #         user = db.query(ExamUsers).filter(
# #             ExamUsers.user_id == payment.created_by
# #         ).first()
# # # user = db.query(ExamUsers).filter(
# # #     ExamUsers.username == payment.created_by
# # # ).first()
# #         if not user:
# #             continue

# #         # -----------------------------
# #         # 📅 2nd of month → FIRST REMINDER
# #         # -----------------------------
# #         if today == 2 and payment.reminder_stage == 0:
# #             send_notify_email(
# #                 user.email,
# #                 user.username,
# #                 "First Payment Reminder (2nd of Month)"
# #             )

# #             payment.reminder_stage = 1
# #             payment.last_reminder_at = datetime.utcnow()

# #         # -----------------------------
# #         # 📅 20th of month → FINAL REMINDER
# #         # -----------------------------
# #         elif today == 20 and payment.reminder_stage == 1:
# #             send_notify_email(
# #                 user.email,
# #                 user.username,
# #                 "Final Payment Reminder (20th of Month)"
# #             )

# #             payment.reminder_stage = 2
# #             payment.last_reminder_at = datetime.utcnow()

# # #     db.commit()

# from datetime import datetime

# def check_and_notify(db):

#     payments = db.query(Pay_email).all()
#     print("Checking payment reminders...")

#     today = datetime.utcnow().day

#     #to test       #PUT today =2 or 20

#     for payment in payments:

#         if payment.is_complete == True:
#             continue

#         # ✅ USE RELATIONSHIP (NO QUERY NEEDED)
#         # SINCE
#     # sender = relationship("Users", foreign_keys=[from_id], back_populates="sent_emails")
#     # receiver = relationship("Users", foreign_keys=[to_id], back_populates="received_emails")

#         user = payment.receiver   


#         if not user:
#             continue

    
#         if today == 2 and payment.reminder_stage == 0:
#             send_notify_email(
#                 user.email,
#                 user.username,
#                 "First Payment Reminder (2nd of Month)"
#             )
#             payment.reminder_stage = 1   # STAGE 1 MEANS FIRST REMAINDER SENT
#             payment.last_reminder_at = datetime.utcnow()

#         elif today == 20 and payment.reminder_stage == 1:
#             send_notify_email(
#                 user.email,
#                 user.username,
#                 "Final Payment Reminder (20th of Month)"
#             )
#             payment.reminder_stage = 2 # STAGE 2 MEANS SECOND REMAINDER SENT
#             payment.last_reminder_at = datetime.utcnow()

#     db.commit()