import smtplib
from email.mime.text import MIMEText

# -------------------------------------------------
# PUT YOUR DETAILS HERE
# -------------------------------------------------
SENDER_EMAIL = "parthbhale1247@gmail.com"
APP_PASSWORD = "qtfh vmme vgbq kztr"
RECEIVER_EMAIL = "parthbhale1234@gmail.com"
# -------------------------------------------------

def send_email(subject, message):

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
