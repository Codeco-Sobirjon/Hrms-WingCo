from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode

from apps.authentification.services.email_utils import Util


def send_reset_password_email(self, user):
    uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
    token = PasswordResetTokenGenerator().make_token(user)
    absurl = f"https://hrms.prounity.uz/reset-password/{uidb64}/{token}"
    email_body = f"Hi \n Use link below to reset password \n link: {absurl}"
    email_data = {
        "email_body": email_body,
        "to_email": user.email,
        "email_subject": "Reset your password",
    }
    Util.send(email_data)