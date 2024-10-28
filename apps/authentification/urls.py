from django.urls import path

from apps.authentification.views.autentification import (
    RegisterViews,
    VerificationSmsCodeView,
    LoginView,
    LogoutView
)
from apps.authentification.views.reset_password import (
    RequestPasswordRestEmail,
    SetNewPasswordView,
    ResendCodeByEmailView,
)
from rest_framework_simplejwt.views import TokenBlacklistView

urlpatterns = [
    path('register', RegisterViews.as_view()),
    path('login', LoginView.as_view()),
    path('logout', LogoutView.as_view()),
    path('logout-user', TokenBlacklistView.as_view()),
    path('reset', RequestPasswordRestEmail.as_view()),
    path('reset_complete', SetNewPasswordView.as_view()),
    path('verification', VerificationSmsCodeView.as_view()),
    path('resend', ResendCodeByEmailView.as_view()),
]
