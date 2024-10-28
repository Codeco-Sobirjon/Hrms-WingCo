from datetime import timedelta

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from apps.authentification.models import (
    CustomUser
)


class CleanupConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        # Run the cleanup task
        await self.cleanup_task()

        # Close the connection after the task is completed
        await self.close()

    @database_sync_to_async
    def cleanup_task(self):
        # Define the threshold for unverified users (e.g., 48 hours)
        threshold = timezone.now() - timedelta(hours=3)

        # Get unverified users and delete them
        unverified_users = CustomUser.objects.filter(
            is_staff=False, date_joined__lte=threshold
        )
        unverified_users_count = unverified_users.count()
        print(unverified_users)
        print(unverified_users_count)
        self.send(text_data=f'Deleting {unverified_users_count} unverified users...')

        unverified_users.delete()

        self.send(text_data='Cleanup complete.')
