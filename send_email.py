from dotenv import load_dotenv
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
load_dotenv()

def send_email(subject, body):
    
    # Check if environment variables are loaded
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('EMAIL_PASSWORD')
    recipients = ["ludwig.wagberg@herrljunga.se", ]

    # Debug: print the values to check if they are being loaded correctly
    print(f"Sending email to: {recipients}")

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ', '.join(recipients)
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))
    # Rest of your code remains the same
    with smtplib.SMTP('smtp.office365.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipients, msg.as_string())
