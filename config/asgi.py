import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.core.asgi import get_asgi_application
import apps.chat.utils.routing
from channels.routing import URLRouter, ProtocolTypeRouter
from channels.security.websocket import AllowedHostsOriginValidator

django_asgi = get_asgi_application()

from config.tokenauth_middleware import (
    TokenAuthMiddleware
)

application = ProtocolTypeRouter({
    "http": django_asgi,
    "websocket": AllowedHostsOriginValidator(
        TokenAuthMiddleware(
            URLRouter(
                apps.chat.utils.routing.websocket_urlpatterns
            )
        ),
    ),
})
