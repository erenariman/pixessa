from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'notification_type',
        'content_type',
        'object_id',
        'is_read',
        'created_at',
    )
    list_filter = ('user', 'content_type', 'is_read', 'created_at')
    date_hierarchy = 'created_at'
