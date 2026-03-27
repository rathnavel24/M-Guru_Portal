from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.app.models.portal_users import Users
from backend.app.app.models.pay_email_table import Pay_email
from datetime import datetime


def dashboard(batch_id, db: Session):

    email_query = db.query(Pay_email).join(Users, Pay_email.to_id == Users.user_id)
    invoice_query = db.query(func.sum(Pay_email.amount)).join(
        Users, Pay_email.to_id == Users.user_id
    )
    recent_mail = db.query(
        Pay_email.invoice_no,
        Pay_email.to_id,
        Pay_email.email_type,
        Pay_email.amount,
        Pay_email.due_date,
        Pay_email.is_complete,
        Pay_email.created_at,
    ).join(Users, Pay_email.to_id == Users.user_id)

    email_type_data = db.query(
        Pay_email.email_type, func.count(Pay_email.id).label("count")
    ).join(Users, Pay_email.to_id == Users.user_id)

    if batch_id:
        email_query = email_query.filter(Users.batch == batch_id)
        invoice_query = invoice_query.filter(Users.batch == batch_id)
        recent_mail = recent_mail.filter(Users.batch == batch_id)
        email_type_data = email_type_data.filter(Users.batch == batch_id)

    email_sent = email_query.count()
    total_invoice = invoice_query.scalar() or 0
    recent_mail_data = recent_mail.order_by(Pay_email.created_at.desc()).limit(5).all()
    recent_mail_his = [dict(row._mapping) for row in recent_mail_data]

    email_type = email_type_data.group_by(Pay_email.email_type).all()
    email_type_count = [dict(row._mapping) for row in email_type]

    # Active customers
    active_query = db.query(Users).filter(Users.status == 1)
    if batch_id:
        active_query = active_query.filter(Users.batch == batch_id)
    active_cus = active_query.count()

    # Overdue
    overdue_query = (
        db.query(Pay_email)
        .join(Users, Pay_email.to_id == Users.user_id)
        .filter(Pay_email.due_date < datetime.now())
    )

    if batch_id:
        overdue_query = overdue_query.filter(Users.batch == batch_id)
    overdue = overdue_query.count()

    return {
        "email_sent": email_sent,
        "total_invoice": total_invoice,
        "active_customers": active_cus,
        "overdue": overdue,
        "recent_mail": recent_mail_his,
        "email_type_count": email_type_count,
    }
