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
async def send_general_reminder(user):
    template = env.get_template("payment_delay_mail.html")

    html_content = template.render(
        name=user.username,
        email=user.email,
        amount="10000",
        invoice_id="N/A",
        note="Monthly Fee Reminder",
        date=datetime.now().strftime("%d %b %Y"),
        due_date="--",
        account_name="Your Account Name",
        account_no="XXXXXX",
        ifsc="XXXX",
        bank_name="Your Bank",
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
        users = (
                db.query(Users)
                .join(Fee, Fee.user_id == Users.user_id)
                .filter(
                    Users.type == 2,
                    Users.status == 1,
                    Fee.status == 1,  # active fee
                    Fee.paid_amount < Fee.total_fee
                )
                .all()
                )

        print("=== JOB STARTED ===")

        for user in users:
            try:
                if not user.email or "@" not in user.email:
                    continue

                print(f"Sending to {user.email}")

                await send_general_reminder(user)
                await asyncio.sleep(1)  # throttle

            except Exception as e:
                print(f"Failed for {user.email}: {e}")
                continue

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
