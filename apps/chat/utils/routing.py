from django.urls import path

from apps.chat.utils.consumers import (
    ChatConsumer,
)
from apps.notification.consumers import (
    NotificationConsumer
)

websocket_urlpatterns = [
    path('ws/chat/<int:room_name>/', ChatConsumer.as_asgi()),
    path('ws/notification/<int:room_name>/', NotificationConsumer.as_asgi()),
]

