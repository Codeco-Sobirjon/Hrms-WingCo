from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notification.models import (
    Notification
)
from apps.notification.serializers.notification_serializers import (
    NotificationSerializer
)


class NotificationsViews(APIView):

    def get(self, request):
        queryset = Notification.objects.select_related('sender').filter(
            sender=request.user
        ).filter(
            is_seen=False
        )
        serializers = NotificationSerializer(queryset, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class NotificationView(APIView):

    def get(self, request):
        queryset = Notification.objects.select_related('sender').filter(
            sender=request.user
        ).filter(
            is_seen=False
        )
        serializers = NotificationSerializer(queryset, many=True)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'notification'
        )
        return Response({'msg': 'Send Notification in Websoccet'}, status=status.HTTP_200_OK)
