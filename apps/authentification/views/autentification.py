import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentification.services.token import get_token_for_user
from apps.authentification.services.send_verification_code import send_verification_email
from services.renderers import UserRenderers
from apps.authentification.services.generate_sms_code import generate_sms_code
from apps.authentification.models import SmsHistory
from apps.authentification.utils.serializers import (
    LoginSerializer,
    RegisterSerializer,
)

from services.responses import (
    bad_request_response,
    unauthorized_response, success_created_response, success_response,
)
from services.expected_fields import check_expected_fields
from services.swagger import swagger_schema, swagger_extend_schema
from services.check_required_key import check_required_key



@swagger_extend_schema(fields={"username", "email", "role", "password", "confirm_password"}, description="Register")
@swagger_schema(serializer=RegisterSerializer)
class RegisterViews(APIView):
    def post(self, request):
        valid_fields = {"username", "email", "role", "password", "confirm_password"}
        unexpected_fields = check_expected_fields(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user_instance = self.create_user(serializer)
            sms_code = generate_sms_code()
            send_verification_email(user_instance, sms_code)
            SmsHistory.objects.create(code=sms_code, user=user_instance)

            response_data = {
                "sms_code": sms_code,
                "msg": "Verification code sent to your email, check it",
                "token": get_token_for_user(user_instance)
            }

            return success_created_response(response_data)

        return bad_request_response(serializer.errors)

    def get_serializer(self, *args, **kwargs):
        return RegisterSerializer(*args, **kwargs)

    def create_user(self, serializer):
        return serializer.save()


@swagger_extend_schema(fields={"code"}, description="Verification Sms Code")
@swagger_schema(serializer=RegisterSerializer)
class VerificationSmsCodeView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    def put(self, request):
        valid_fields = {"code"}
        unexpected_fields = check_expected_fields(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        if not request.user.is_authenticated:
            return unauthorized_response()

        error_response = check_required_key(request, 'code', 'Custom error message for missing code key')
        if error_response:
            return error_response

        try:
            check_code = SmsHistory.objects.select_related("user").filter(Q(user=request.user)).last()

            if check_code and check_code.code == int(request.data["code"]):
                check_code.user.is_staff = True
                check_code.user.save()
                return success_response(get_token_for_user(check_code.user))

            return bad_request_response("The verification code was entered incorrectly")

        except ObjectDoesNotExist:
            return bad_request_response("Object does not exist")


@swagger_extend_schema(fields={"email", "password"}, description="Login")
@swagger_schema(serializer=RegisterSerializer)
class LoginView(APIView):

    def post(self, request):
        valid_fields = {"email", "password"}
        unexpected_fields = check_expected_fields(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        return success_response(get_token_for_user(user))

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            refresh_token_obj = RefreshToken(refresh_token)
            refresh_token_obj.blacklist()

            print(f"Access Token blacklisted: {refresh_token_obj.access_token}")
            logging.info(f"Token successfully blacklisted: {refresh_token}")

            return success_response("Successfully logged out")
        except ObjectDoesNotExist:
            return bad_request_response("Invalid token")
        except Exception as e:
            logging.error(f"Error during logout: {e}")
            return bad_request_response("Error during logout")