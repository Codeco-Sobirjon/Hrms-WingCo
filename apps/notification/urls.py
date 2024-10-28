from django.urls import path

from apps.notification.views.views import (
    NotificationsViews
)

urlpatterns = [
    path('', NotificationsViews.as_view())
]
