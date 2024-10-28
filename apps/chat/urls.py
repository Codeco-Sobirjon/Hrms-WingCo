from django.urls import path

from apps.chat.views import views

urlpatterns = [
    path('start/', views.StartConversationView.as_view(), name='start_convo'),
    path('conversation/<int:convo_id>/', views.get_conversation, name='get_conversation'),

    path('initiator_conversation/<int:pk>/', views.GetInitiatorConversations.as_view()),
    path('receiver_conversation/<int:pk>/', views.GetReceiverConversations.as_view()),

    path('message_delete/<int:pk>/', views.DeleteChatSMSView.as_view()),

    path('', views.conversations, name='conversations'),

    path('chat-rooms/', views.ChatUserView.as_view()),
]
