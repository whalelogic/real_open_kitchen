import smtplib
from email.message import EmailMessage
import os

def send_otp_email(user_email, otp_code):
    """sends 6-digit OTP to the provied email"""
    email_address = os.environ.get('MAIL_USERNAME')
    email_password = os.environ.get('MAIL_PASSWORD')

    if not email_address or not email_password:
        print("Warning: Email credentials not set in environment.")
        return False

    msg = EmailMessage()
    msg.set_content(f"Hello,\n\nYour My Open Kitchen password reset code is: {otp_code} \n\nThis code will expire in 10 minutes.")

    msg['Subject'] = 'My Open Kitchen - Password Reset Code'
    msg['From'] = email_address
    msg["To"] = user_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_address, email_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
