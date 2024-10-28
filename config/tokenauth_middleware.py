from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.tokens import AccessToken

from apps.authentification.models import CustomUser


@database_sync_to_async
def get_user(token_key):
    try:
        access_token_obj = AccessToken(token_key)
        user_id = access_token_obj['user_id']
        user = CustomUser.objects.get(id=user_id)
        return user
    except ObjectDoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        token_key = scope['query_string'].decode().split('=')[-1]
        scope['user'] = await get_user(token_key)
        return await super().__call__(scope, receive, send)

