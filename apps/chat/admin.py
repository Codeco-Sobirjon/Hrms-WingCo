from django.contrib import admin
from .models import *

from import_export.admin import ImportExportModelAdmin

class ConversationAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'initiator', 'receiver', 'jobs']


class MessageAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'text', 'sender', 'conversation_id']

admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)
