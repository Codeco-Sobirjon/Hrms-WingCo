from apps.authentification.services.email_utils import Util


def send_verification_email(user_instance, sms_code):
    email_body = f"Hi {user_instance.username},\nThis is your verification code to register your account: {sms_code}\nThanks..."
    email_data = {
        "email_body": email_body,
        "to_email": user_instance.email,
        "email_subject": "Verify your email",
    }
    Util.send(email_data)