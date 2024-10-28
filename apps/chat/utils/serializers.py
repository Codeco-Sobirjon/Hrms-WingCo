from rest_framework import serializers

from apps.authentification.utils.serializers import (
    UserProfilesSerializer
)
from apps.chat.models import Conversation, Message
from apps.enrolls.utils.serializers import (
    JobVacanciesListSerializer,
)


class MessageSerializer(serializers.ModelSerializer):
    sender = UserProfilesSerializer(read_only=True)

    class Meta:
        model = Message
        exclude = ('conversation_id',)


class ConversationListSerializer(serializers.ModelSerializer):
    initiator = UserProfilesSerializer(read_only=True)
    receiver = UserProfilesSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'initiator', 'jobs', 'receiver', 'last_message']

    def get_last_message(self, instance):
        message = instance.message_set.first()
        if message:
            return MessageSerializer(instance=message).data
        else:
            return None


class ConversationSerializer(serializers.ModelSerializer):
    initiator = UserProfilesSerializer(read_only=True)
    receiver = UserProfilesSerializer(read_only=True)
    message_set = MessageSerializer(many=True)
    jobs = JobVacanciesListSerializer(read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'initiator', 'receiver', 'jobs', 'message_set']
