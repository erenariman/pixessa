from django.contrib import admin

from .models import Tag, Post, PostMedia, Comment


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    date_hierarchy = 'created_at'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'caption',
        'location',
        'created_at',
        'updated_at',
    )
    list_filter = ('user', 'created_at', 'updated_at')
    raw_id_fields = ('tags',)
    date_hierarchy = 'created_at'


@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'post',
        'file',
        'media_type',
        'order',
        'created_at',
    )
    list_filter = ('post', 'created_at')
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'post',
        'user',
        'content',
        'parent',
        'created_at',
        'updated_at',
    )
    list_filter = ('post', 'user', 'parent', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
