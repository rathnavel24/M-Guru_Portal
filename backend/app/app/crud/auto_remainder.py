from apscheduler.schedulers.asyncio import AsyncIOScheduler
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.app.db.session import sessionLocal
from backend.app.app.models import Pay_email
from backend.app.app.models import Users
from backend.app.app.crud.email_services import send_email
from email.message import EmailMessage
import os
import asyncio

from backend.app.app.models.portaluserfee import Fee

#  Scheduler
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(os.path.join(BASE_DIR, "../templates")))


#  DB session
def get_db():
    return sessionLocal()


#  Scheduler runner
def run_auto_reminder_job():
    asyncio.run(send_auto_reminders())

#  EMAIL FUNCTION (UNCHANGED)
async def send_general_reminder(user,fee,x):
    template = env.get_template("payment_delay_mail.html")
    
    html_content = template.render(
        name=user.username,
        email=user.email,
        amount=fee.emi_amount,
        invoice_id="N/A",
        note="Monthly Fee Reminder",
        date=datetime.now().strftime("%d %b %Y"),
        due_date="--",
        account_name=x.account_name,
        account_no=x.account_no,
        ifsc=x.ifsc,
        bank_name=x.bank_name,
    )

    msg = EmailMessage()
    msg["Subject"] = "Monthly Payment Reminder"
    msg["From"] = os.getenv("user")
    msg["To"] = user.email

    msg.set_content("Please view this email in HTML format.")
    msg.add_alternative(html_content, subtype="html")

    await send_email(msg)

# MAIN JOB (UPDATED LOGIC ONLY)
async def send_auto_reminders():
    db: Session = get_db()

    try:
        results = (
        db.query(Users, Fee)
        .join(Fee, Fee.user_id == Users.user_id)
        .filter(
            Users.type == 2,
            Users.status == 1,
            Fee.monthly_installment.is_(True),
            Fee.status == 1,
            Fee.paid_amount < Fee.total_fee
        )
        .all()
    )

        print("=== JOB STARTED ===")

        for user, fee in results:
            try:
                if not user.email or "@" not in user.email:
                    continue

                print(f"Sending to {user.email}")

                # pass fee also if needed
                x=db.query(Pay_email.bank_name,
                           Pay_email.account_no,
                           Pay_email.ifsc,
                           Pay_email.account_name).first()
                await send_general_reminder(user, fee, x)

                await asyncio.sleep(1)

            except Exception as e:
                print(f"Failed for {user.email}: {e}")

    finally:
        db.close()


#  SCHEDULER
def start_scheduler(test_mode=False):
    if test_mode:
        # TEST MODE
        scheduler.add_job(run_auto_reminder_job, "interval", minutes=1)
    else:
        #  PRODUCTION MODE
        scheduler.add_job(run_auto_reminder_job, "cron", day="2,20", hour=10, minute=0)

    scheduler.start()
