from flask_mail import Message
from app import mail


def send_notification(to, subject, body):
    msg = Message(subject=subject, recipients=[to], sender="noreply@cms.com")
    msg.body = body
    mail.send(msg)
