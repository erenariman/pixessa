from django.contrib import admin

from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    raw_id_fields = ('participants',)
    date_hierarchy = 'created_at'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'conversation',
        'sender',
        'content',
        'timestamp',
        'read',
    )
    list_filter = ('conversation', 'sender', 'timestamp', 'read')
