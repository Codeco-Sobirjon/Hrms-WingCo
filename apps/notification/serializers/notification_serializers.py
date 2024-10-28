from rest_framework import serializers

from apps.authentification.utils.serializers import (
    UserProfilesSerializer
)
from apps.notification.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserProfilesSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'sender',
            'message',
            'sent_at'
        ]
