import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .models import EmailContent

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

def send_email(to_email: str, email_content: EmailContent) -> bool:
    try:
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = to_email
        message["Subject"] = email_content.subject
        content = email_content.body.replace("\\n", "\n")
        body = f"{content}"
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False