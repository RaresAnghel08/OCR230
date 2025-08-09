import smtplib
import os
from email.message import EmailMessage
from email.utils import make_msgid
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_report_email(sender_email, sender_password, recipient_email, subject, body, attachments):
    """
    Trimite automat rapoarte (PDF/Excel/CSV) pe email.
    attachments: list of file paths
    """
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    for file_path in attachments:
        if not os.path.exists(file_path):
            continue
        with open(file_path, 'rb') as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        msg.attach(part)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"✅ Email trimis către {recipient_email}")
        return True
    except Exception as e:
        print(f"❌ Eroare la trimiterea emailului: {e}")
        return False
