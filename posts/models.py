from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from likes.models import Like

User = get_user_model()


class PostManager(models.Manager):
    def public_posts(self):
        return self.filter(user__is_private=False).select_related('user')

    def user_posts(self, user):
        return self.filter(user=user).prefetch_related('media', 'tags')

    def with_comments_count(self):
        return self.annotate(comments_count=models.Count('comments'))

    def with_likes_count(self):
        return self.annotate(likes_count=models.Count('likes'))

    def feed_posts(self, user):
        following_ids = user.following.values_list('id', flat=True)
        return self.filter(
            models.Q(user__in=following_ids) |
            models.Q(user=user)
        ).distinct()

class CommentManager(models.Manager):
    def root_comments(self):
        return self.filter(parent__isnull=True)

    def replies_to(self, comment):
        return self.filter(parent=comment)

    def active_comments(self):
        return self.filter(is_deleted=False)

    def with_replies_count(self):
        return self.annotate(replies_count=models.Count('replies'))


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    caption = models.TextField()
    location = models.CharField(max_length=100, blank=True)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    likes = GenericRelation(Like, related_query_name='post')

    objects = PostManager()

    def __str__(self):
        return f"Post by {self.user} at {self.created_at}"

class PostMedia(models.Model):
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='post_media/')
    media_type = models.CharField(max_length=5, choices=MEDIA_TYPES)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.media_type} for post {self.post.id}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_offensive = models.BooleanField(default=False)
    hate_score = models.FloatField(null=True, blank=True)

    objects = CommentManager()

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"
