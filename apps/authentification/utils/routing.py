from django.urls import path

from apps.authentification.utils.consumers import CleanupConsumer

websocket_urlpatterns = [
    path("ws/cleanup/", CleanupConsumer.as_asgi()),
]
