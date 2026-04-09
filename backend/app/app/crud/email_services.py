import aiosmtplib
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from backend.app.app.models import Users, Pay_email,Fee
from backend.app.app.schemas.user_schema import Paymentmail
from pathlib import Path
from email.message import EmailMessage
from datetime import datetime
import os
from dotenv import load_dotenv

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

    try:
        user = (
            db.query(Users.username, Users.email).join(Fee, Fee.user_id == Users.user_id)
            .filter(Users.user_id == data.user_id,Fee.paid_amount < Fee.total_fee)
            .first()
        )

        if not user:
            raise ValueError("User not found")
        #new invoice
        if data.email_type == 1:
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
            if not data.invoice_no:
                raise ValueError("Invoice number is required")

            existing = db.query(Pay_email).filter(
                Pay_email.invoice_no == data.invoice_no.strip(),
                Pay_email.email_type == "1"
            ).first()

            if not existing:
                raise ValueError("Invalid invoice ID")

            gen_invoice_id = existing.invoice_no

            # Always take values from DB
            account_name = existing.account_name
            account_no = existing.account_no
            ifsc = existing.ifsc
            bank_name = existing.bank_name
            amount = existing.amount
            due_date = existing.due_date
            is_complete = existing.is_complete

            # REMINDER
            if data.email_type == 2:
                status = 3  # Reminder sent

            # CONFIRMATION
            elif data.email_type == 3:
                reference_no = data.reference_no   #to store reference number in db
                status = existing.status  # keep existing (no change)
                if existing.is_complete:
                    raise ValueError("Payment already completed")

                fee = db.query(Fee).filter(
                    Fee.user_id == existing.to_id
                ).first()

                if not fee:
                    raise ValueError("Fee record not found")

                # Add invoice amount
                fee.paid_amount = (fee.paid_amount or 0) + existing.amount

                payment_confirmation_service(invoice_no=data.invoice_no,reference_no=data.reference_no,db=db)
                is_complete = True
                db.commit()

            else:
                raise ValueError("Invalid email type")
            
        #  EMAIL TEMPLATE
        if data.email_type == 1:
            template = env.get_template("payment_invoice_mail.html")
            subject = f"Invoice - {gen_invoice_id}"

        elif data.email_type == 2:
            template = env.get_template("payment_remainder_mail.html")
            subject = f"Reminder - {gen_invoice_id}"

        else:
            template = env.get_template("payment_confirmation_mail.html")
            subject = f"Confirmation - {gen_invoice_id}"

        html_content = template.render(
            name=user.username,
            email=user.email,
            amount=amount,
            invoice_id=gen_invoice_id,
            note=data.note if data.email_type == 1 else existing.note,
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

        #LOG ENTRY
        add_log = Pay_email(
            invoice_no=gen_invoice_id,
            from_id=sender_id,
            to_id=data.user_id,
            note=data.note if data.email_type == 1 else existing.note,
            email_type=data.email_type,
            amount=amount,
            due_date=due_date,
            account_name=account_name,
            account_no=account_no,
            ifsc=ifsc,
            bank_name=bank_name,
            is_complete=is_complete,
            status=status,
            reference_no = reference_no,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="ADMIN",
        )

        db.add(add_log)
        db.commit()

        return {"message": "Email sent successfully"}

    except Exception as e:
        db.rollback()
        raise {"User completed their fee ", e}

def payment_confirmation_service(invoice_no,reference_no, db:Session):
    records = db.query(Pay_email).filter(
        Pay_email.invoice_no == invoice_no
    ).all()

    if not records:
        return {"message": "Invalid invoice no"}

    updated = False

    for record in records:
        if not record.is_complete:
            record.reference_no = reference_no
            record.is_complete = True
            record.updated_at = datetime.now()
            updated = True

    if not updated:
        return {"message": "Payment already confirmed"}

    db.commit()

    return {
        "message": "Payment confirmed",
        "invoice_no": invoice_no,
        "reference_no": reference_no
    }

def get_bankdetail(invoice_no: str, db: Session):
    bank_details = db.query(
        Pay_email.amount,
        Pay_email.bank_name,
        Pay_email.account_name,
        Pay_email.account_no,
        Pay_email.ifsc
    ).filter(Pay_email.invoice_no == invoice_no,
             Pay_email.is_complete == False).first()

    if not bank_details:
        return {"message": "Enter Valid Invoice number"}

    return {
        "bank_name": bank_details.bank_name,
        "amount":bank_details.amount,
        "account_name": bank_details.account_name,
        "account_no": bank_details.account_no,
        "ifsc": bank_details.ifsc
    }
