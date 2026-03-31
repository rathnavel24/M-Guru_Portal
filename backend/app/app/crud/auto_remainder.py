from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.app.db.session import sessionLocal
from backend.app.app.models import Pay_email
from backend.app.app.models import Users
from backend.app.app.crud.email_services import send_email
from backend.app.app.templates import env
from email.message import EmailMessage


# ✅ DB session
def get_db():
    return sessionLocal()


# ✅ PURE REMINDER EMAIL FUNCTION
async def send_payment_reminder(invoice, user):
    template = env.get_template("payment_remainder_mail.html")

    html_content = template.render(
        name=user.username,
        email=user.email,
        amount=invoice.amount,
        invoice_id=invoice.invoice_no,
        note=invoice.note,
        date=datetime.now().strftime("%d %b %Y"),
        due_date=invoice.due_date,
        account_name=invoice.account_name,
        account_no=invoice.account_no,
        ifsc=invoice.ifsc,
        bank_name=invoice.bank_name,
    )

    msg = EmailMessage()
    msg["Subject"] = f"Reminder - {invoice.invoice_no}"
    msg["From"] = "your_email@example.com"
    msg["To"] = user.email

    msg.set_content("Please view this email in HTML format.")
    msg.add_alternative(html_content, subtype="html")

    await send_email(msg)


# ✅ MAIN JOB
async def send_auto_reminders():
    db: Session = get_db()

    try:
        pending_invoices = db.query(Pay_email).filter(
            Pay_email.email_type == 1,
            Pay_email.is_complete == False
        ).all()

        for invoice in pending_invoices:
            try:
                user = db.query(Users).filter(
                    Users.user_id == invoice.to_id
                ).first()

                if not user or not user.email:
                    continue

                await send_payment_reminder(invoice, user)

            except Exception as e:
                raise Exception(f"Reminder failed for {invoice.invoice_no}: {str(e)}")

    except Exception as e:
        raise Exception(f"Auto reminder job failed: {str(e)}")

    finally:
        db.close()


# # ✅ SCHEDULER
# def start_scheduler():
#     scheduler.add_job(
#         send_auto_reminders,
#         'cron',
#         day=2,
#         hour=10,
#         minute=0
#     )

#     scheduler.add_job(
#         send_auto_reminders,
#         'cron',
#         day=20,
#         hour=10,
#         minute=0
#     )

#     scheduler.start() 