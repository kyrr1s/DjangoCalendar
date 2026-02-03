from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


app = FastAPI()

############################ NOTIFICATION ##############################

class EmailNotification(BaseModel):
    recipient: EmailStr
    subject: str
    message: str

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.yandex.ru")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "default_user")
SMTP_PASSWORD_PATH = "/run/secrets/smtp_password"

def send_email(recipient, subject, message):
    """ Func for sending emails """
    
    with open(SMTP_PASSWORD_PATH, "r", encoding="utf-8") as file:
        smtp_password = file.read().strip()

    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        print(SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, smtp_password)
        print(recipient, msg.as_string())
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls() # tls
            server.login(SMTP_USERNAME, smtp_password) # login
            server.sendmail(SMTP_USERNAME, recipient, msg.as_string()) #send mail 
    except Exception as e:
        print(f"Error sending email: {e}")

@app.post("/notify/")
async def notify(notification: EmailNotification, background_tasks: BackgroundTasks):
    """ Func for managing notify messages """

    background_tasks.add_task(
        send_email,
        notification.recipient,
        notification.subject,
        notification.message,
    )
    return {"message": "Notification sent in background"}

################################## AUTH #######################################


