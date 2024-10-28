from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, reverse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from services.renderers import UserRenderers
from apps.chat.models import (
    Conversation,
    Message
)
from apps.chat.utils.serializers import (
    ConversationListSerializer,
    ConversationSerializer
)
from apps.notification.models import (
    Notification
)


class StartConversationView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    def post(self, request):
        data = request.data

        # get doctor username here
        username = data['username']

        # check the user is or not in databases
        try:
            participant = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'message': 'You cannot chat with a non existent user'})
        # ------------------------------------
        # we are checked (Patient and Doctor) or (Doctor and Patient) chat group has or not
        conversation = Conversation.objects.filter(Q(initiator=request.user, receiver=participant) |
                                                   Q(initiator=participant, receiver=request.user))
        # -----------------------------------
        # We are check groups is have or not, and if room is does not we will create new room
        if conversation.exists():
            return redirect(reverse('get_conversation', args=(conversation[0].id,)))
        else:
            conversation = Conversation.objects.create(initiator=request.user, receiver=participant)
            return Response(ConversationSerializer(instance=conversation).data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_conversation(request, convo_id):
    conversation = Conversation.objects.filter(id=convo_id)
    queryset_update = Notification.objects.select_related('sender').filter(
        sender=request.user
    ).filter(
        is_seen=False
    ).update(is_seen=True)
    if not conversation.exists():
        return Response({'message': 'Conversation does not exist'})
    else:
        serializer = ConversationSerializer(instance=conversation[0])
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def conversations(request):
    conversation_list = Conversation.objects.filter(Q(initiator=request.user) |
                                                    Q(receiver=request.user))
    serializer = ConversationListSerializer(instance=conversation_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class GetInitiatorConversations(APIView):
    render_classes = [UserRenderers]
    permission = [IsAuthenticated]

    def get(self, request, pk):
        queryset = get_object_or_404(User, id=pk)
        get_convo = Conversation.objects.select_related(
            'receiver'
        ).filter(
            receiver__id=queryset.id
        )
        serializer = ConversationSerializer(instance=get_convo, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class GetReceiverConversations(APIView):
    render_classes = [UserRenderers]
    permission = [IsAuthenticated]

    def get(self, request, pk):
        queryset = get_object_or_404(User, id=pk)
        get_convo = Conversation.objects.select_related(
            'initiator'
        ).filter(
            initiator__id=queryset.id
        )
        serializer = ConversationSerializer(instance=get_convo, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteChatSMSView(APIView):
    render_classes = [UserRenderers]
    permission = [IsAuthenticated]

    def delete(self, request, pk):
        queryset = get_object_or_404(Message, id=pk).delete()
        return Response({'msg': "Message Deleted successfully"}, status=status.HTTP_200_OK)


class ChatUserView(APIView):
    render_classes = [UserRenderers]
    permission = [IsAuthenticated]

    def get(self, request):
        objects = Conversation.objects.filter(initiator=request.user.id)
        serializers = ConversationSerializer(objects, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
