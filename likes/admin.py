from django.contrib import admin

from .models import Like


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_type', 'object_id', 'created_at')
    list_filter = ('user', 'content_type', 'created_at')
    date_hierarchy = 'created_at'
