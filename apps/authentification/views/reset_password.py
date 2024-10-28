from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import (
    smart_str,
    DjangoUnicodeDecodeError,
)
from django.utils.http import urlsafe_base64_decode
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.authentification.services.send_reset_password_email import send_reset_password_email
from apps.authentification.services.send_verification_code import send_verification_email
from services.expected_fields import check_expected_fields
from services.renderers import UserRenderers
from services.responses import (
    bad_request_response,
    unauthorized_response, success_response, user_not_found_response,
)
from services.swagger import (
    swagger_schema,
    swagger_extend_schema,
)
from services.check_required_key import check_required_key

from apps.authentification.services.token import get_token_for_user
from apps.authentification.models import CustomUser, SmsHistory
from apps.authentification.utils.serializers import (
    UserProfilesSerializer,
    PasswordResetSerializer,
    PasswordResetCompleteSerializer,
)
from apps.authentification.services.generate_sms_code import generate_sms_code


@swagger_extend_schema(fields={"email"}, description="Request password reset")
@swagger_schema(serializer=PasswordResetSerializer)
class RequestPasswordRestEmail(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request):
        valid_fields = {"email"}
        unexpected_fields = check_expected_fields(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        serializer = self.serializer_class(data=request.data)

        error_response = check_required_key(request, 'email', 'Custom error message for missing code key')
        if error_response:
            return error_response

        if CustomUser.objects.filter(email=request.data.get("email")).exists():
            user = CustomUser.objects.get(email=request.data.get("email"))
            send_reset_password_email(user)
            return success_response("We have sent you to reset your password")

        return user_not_found_response("This email is not found")



@swagger_extend_schema(fields={"uidb64", "token"}, description="Password Token Check")
@swagger_schema(serializer=UserProfilesSerializer)
class PasswordTokenCheckView(generics.GenericAPIView):
    serializer_class = UserProfilesSerializer

    def get(self, request, uidb64, token):
        try:
            user = self.get_user_from_uidb64(uidb64)
            self.validate_token(user, token)

            return success_response("Credential Valid", {"uidb64": uidb64, "token": token,}  )

        except DjangoUnicodeDecodeError:
            return unauthorized_response()

    def get_user_from_uidb64(self, uidb64):
        id = smart_str(urlsafe_base64_decode(uidb64))
        return CustomUser.objects.get(id=id)

    def validate_token(self, user, token):
        if not PasswordResetTokenGenerator().check_token(user, token):
            unauthorized_response()



@swagger_extend_schema(fields={"uidb64", "token", "password"}, description="Password Set Complete")
@swagger_schema(serializer=PasswordResetCompleteSerializer)
class SetNewPasswordView(generics.GenericAPIView):
    serializer_class = PasswordResetCompleteSerializer

    def patch(self, request):
        valid_fields = {"password", "uidb64", "token"}
        unexpected_fields = check_expected_fields(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return success_response("Successfully changed password")


class ResendCodeByEmailView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_authenticated:
            return unauthorized_response()

        if request.user.is_staff:
            return bad_request_response("You already verified...")

        sms_code = generate_sms_code()
        send_verification_email(request.user, sms_code)
        SmsHistory.objects.create(code=sms_code, user=request.user)
        return success_response({"sms_code": sms_code, "token": get_token_for_user(request.user)})
