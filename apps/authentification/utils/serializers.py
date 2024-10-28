""" Django Libary """
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError
from django.utils.encoding import (
    force_str,
)
from django.utils.http import urlsafe_base64_decode

""" Django Rest Framework Libary """
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueValidator
from django.core.exceptions import ObjectDoesNotExist

from apps.authentification.models import CustomUser


class IncorrectCredentialsError(serializers.ValidationError):
    pass

class UnverifiedAccountError(serializers.ValidationError):
    pass

def validate_file_size(value):
    max_size = 2 * 1024 * 1024
    if value.size > max_size:
        raise ValidationError(
            (f'File size must be no more than 2 mb.'),
            params={'max_size': max_size},
        )


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = [
            "id",
            "name",
        ]


class UserProfilesSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    avatar = serializers.ImageField()

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "first_name",
            "username",
            "last_name",
            "email",
            "role",
            "phone",
            "country",
            "city",
            "bio",
            "avatar",
        ]

    def get_role(self, obj):
        role_names = [role.name for role in obj.groups.all()]
        result_str = ''.join(role_names)
        if not role_names:
            return None

        return result_str


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=50, min_length=2)
    password = serializers.CharField(max_length=50, min_length=1)

    class Meta:
        model = get_user_model()
        fields = ("email", "password")

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = self.authenticate_user(email, password)
        self.validate_user(user)

        data["user"] = user
        return data

    def authenticate_user(self, email, password):
        return authenticate(email=email, password=password)

    def validate_user(self, user):
        if not user or not user.is_active:
            raise IncorrectCredentialsError({"error": "Incorrect email or password"})

        if not user.is_staff:
            raise UnverifiedAccountError({"error": "Your account is not verified yet. Verify and try again."})



class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=255,
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())],
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    role = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "password",
            "confirm_password",
            "role",
        ]

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return value

    def create(self, validated_data):
        self.validate_password_match(validated_data)
        self.validate_admin_role(validated_data)

        validated_data.pop("confirm_password")
        role_name = validated_data.pop("role", None)

        user = self.create_user(validated_data)
        self.add_user_to_role(user, role_name)

        return user

    def validate_password_match(self, validated_data):
        if validated_data["password"] != validated_data["confirm_password"]:
            raise serializers.ValidationError({"error": "Passwords don't match"})

    def validate_admin_role(self, validated_data):
        role_name = validated_data.get("role")
        if role_name == "admin":
            raise serializers.ValidationError({"error": "You can't submit this role"})

    def create_user(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def add_user_to_role(self, user, role_name):
        if role_name:
            try:
                role = Group.objects.get(name=role_name)
                user.groups.add(role)
                user.is_staff = False
                user.save()
            except ObjectDoesNotExist:
                raise serializers.ValidationError({"error": "Invalid role"})


class UserDetailSerializers(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    avatar = serializers.FileField(
        max_length=None,
        allow_empty_file=False,
        validators=[validate_file_size]
    )

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "first_name",
            "last_name",
            "role",
            "phone",
            "email",
            "country",
            "city",
            "bio",
            "avatar",
            "avatar",
        ]

    def get_role(self, obj):
        role_names = [role.name for role in obj.groups.all()]
        result_str = ''.join(role_names)
        if not role_names:
            return None

        return result_str

    def update(self, instance, validated_data):
        update = super().update(instance, validated_data)
        return update


class PasswordResetCompleteSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8, max_length=32, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ["password", "token", "uidb64"]

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            token = attrs.get("token")
            uidb64 = attrs.get("uidb64")

            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("Invalid link", 401)

            user.set_password(password)
            user.save()
            return user
        except Exception:
            raise AuthenticationFailed("Invalid link", 401)


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = [
            "email",
        ]


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    default_error_message = {"bad_token": ("Token is expired or invalid")}

    def validate(self, attrs):
        self.token = attrs["refresh_token"]
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail("bad_token")
