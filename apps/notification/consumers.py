import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    # async def receive(self, text_data=None):
    #     # text_data_json = json.loads(text_data)
    #     sender = self.scope["user"]
    #     print(sender.id)
    #     queryset = Notification.objects.filter(
    #         sender=sender.id
    #     ).filter(
    #         is_seen=False
    #     )
    #     print(queryset)
    #     chat_type = {"type": "notification_message"}
    #     message_serializer = {}
    #     # message_serializer = (dict(NotificationSerializer(instance=_queryset).data))
    #     # print(message_serializer)
    #     return_dict = {**chat_type, **message_serializer}
    #     print(return_dict)
    #     # Send message to room group
    #     await self.channel_layer.group_send(
    #         self.room_group_name, return_dict
    #     )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", }
        )

    # Receive message from room group
    # async def notification_message(self, event):
    #     dict_NOTIFICATION = event.copy()
    #     dict_NOTIFICATION.pop("type")
    #     print(dict_NOTIFICATION)
    #     # Send message to WebSocket
    #     self.send(text_data=json.dumps(dict_NOTIFICATION))

    async def chat_message(self, event):
        message = event
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))