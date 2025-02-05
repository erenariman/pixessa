from django.contrib import admin

from .models import Block


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('id', 'blocker', 'blocked', 'created_at')
    list_filter = ('blocker', 'blocked', 'created_at')
    date_hierarchy = 'created_at'
