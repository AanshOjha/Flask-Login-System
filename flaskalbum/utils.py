import random
import smtplib
from flask import url_for
from flaskalbum import EMAIL_ID, EMAIL_PASS, app

# Function to send a password reset email to the user
def send_reset_email(user):
    # Generate a password reset token and construct the reset email content
    token = user.get_reset_token()
    
    # Email configuration and content
    email_user = EMAIL_ID
    email_pwd = EMAIL_PASS

    TO = [user.email]
    SUBJECT = "Password Reset Request"
    TEXT = f'''
To reset your password, visit the following link:

{url_for('reset_token', token=token, _external=True)}

This link is valid for 10 minutes.
If you did not make this request, then simply ignore this email and no changes will be made.

Regards
Aansh Ojha
'''
    server = smtplib.SMTP('smtp.zoho.in', 587)
    server.ehlo()
    server.starttls()
    server.login(email_user, email_pwd)
    BODY = '\r\n'.join(['To: %s' % TO,
            'From: %s' % email_user,
            'Subject: %s' % SUBJECT,
            '', TEXT])
    
    # Send the email using SMTP
    server.sendmail(email_user, [TO], BODY)

otp = int(random.randint(100000, 999999))

def send_otp_email(user):    
    # Email configuration and content
    email_user = EMAIL_ID
    email_pwd = EMAIL_PASS

    TO = [user.email]
    SUBJECT = "OTP to Reset Password"
    TEXT = f'''
To reset your password, enter this OTP in the website:

{otp}

This OTP is valid for 10 minutes.
If you did not make this request, then simply ignore this email and no changes will be made.

Regards
Aansh Ojha
'''
    server = smtplib.SMTP('smtp.zoho.in', 587)
    server.ehlo()
    server.starttls()
    server.login(email_user, email_pwd)
    BODY = '\r\n'.join(['To: %s' % TO,
            'From: %s' % email_user,
            'Subject: %s' % SUBJECT,
            '', TEXT])
    
    # Send the email using SMTP
    server.sendmail(email_user, [TO], BODY)