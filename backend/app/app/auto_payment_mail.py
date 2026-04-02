from backend.app.app.db.session import sessionLocal
from backend.app.app.crud.auto_remainder import send_auto_reminders
import asyncio

async def run_job():
    db = sessionLocal()

    try:
        await send_auto_reminders()
        await asyncio.sleep(2)
        print("Reminder sent successfully")
    except Exception as e:
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_job()) 


#cron command 
# 0 9 2,20 * * /usr/bin/python3 /full/path/auto_payment_mail.py    
#0 9 2,20 * * /usr/bin/python3 /home/user/project/auto_payment_mail.py

# ad task scheduler in windows 
# Action:

# Program:

# C:\Users\traje\AppData\Local\Programs\Python\Python313\python.exe

# Arguments:

# -m backend.app.app.auto_payment_mail

# Start in:

# C:\Users\traje\OneDrive\Desktop\M-guru Portal\M-Guru_Portal