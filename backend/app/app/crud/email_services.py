import aiosmtplib
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader
from io import BytesIO
import qrcode
from sqlalchemy.orm import Session
from backend.app.app.models import Users, Pay_email
from backend.app.app.schemas.user_schema import Paymentmail
from pathlib import Path
from email.message import EmailMessage
from datetime import datetime
import random
import string
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


def generate_upi_qr(upi_id, amount):  # qr generate function
    upi_string = f"upi://pay?pa={upi_id}&am={amount}&cu=INR"

    qr = qrcode.make(upi_string)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def generate_invoice_id(user_id):
    date = datetime.now().strftime("%Y%m%d")
    random_inv = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"INV-{user_id}{random_inv}{date}"


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

        #  Load HTML template
        if data.email_type == 1:
            template = env.get_template("payment_invoice_mail.html")
        elif data.email_type == 2:
            template = env.get_template("payment_remainder_mail.html")
        else:
            template = env.get_template("payment_confirmation_mail.html")

        gen_invoice_id = generate_invoice_id(data.user_id)

        html_content = template.render(
            name=user.username,
            email=user.email,
            amount=data.amount,
            invoice_id=gen_invoice_id,
            note=data.note,
            date=datetime.now().strftime("%d %b %Y"),
            due_date=data.due_date,
            upi_id=data.upi_id,
        )
        qr_buffer = None
        if data.email_type in [1, 2]:
            #  Generate QR
            qr_buffer = generate_upi_qr(data.upi_id, data.amount)
            qr_buffer.seek(0)

        # Create Email
        msg = EmailMessage()
        msg["Subject"] = f"Invoice {gen_invoice_id} - Payment Request"
        msg["From"] = os.getenv("user")
        msg["To"] = user.email
        if not user.email:
            raise ValueError("User email is missing")

        msg.set_content("Please view this email in HTML format.")
        msg.add_alternative(html_content, subtype="html")  #  Add HTML
        #  Attach QR image
        if qr_buffer:
            msg.get_payload()[1].add_related(
                qr_buffer.read(), maintype="image", subtype="png", cid="<qrcode>"
            )
        await send_email(msg)

        add_log = Pay_email(
            invoice_no=gen_invoice_id,
            from_id= sender_id,
            to_id=data.user_id,
            note=data.note,
            email_type="REMAINDER",
            amount=data.amount,
            due_date=data.due_date,
            upi_id=data.upi_id,
            is_complete=False,
            status=1,  # 1= success,2=Failed
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="ADMIN",
        )
        db.add(add_log)
        db.commit()

    except Exception as e:
        print("Email Error:", str(e))