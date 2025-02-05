from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

User = get_user_model()


class LikeManager(models.Manager):
    def likes_for_object(self, obj):
        content_type = ContentType.objects.get_for_model(obj)
        return self.filter(
            content_type=content_type,
            object_id=obj.pk
        ).select_related('user')

    def user_likes(self, user):
        return self.filter(user=user).prefetch_related('content_object')

    def toggle_like(self, user, content_object):
        content_type = ContentType.objects.get_for_model(content_object)
        like, created = self.get_or_create(
            user=user,
            content_type=content_type,
            object_id=content_object.id
        )
        if not created:
            like.delete()
            return False
        return True


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = LikeManager()

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
        unique_together = ('user', 'content_type', 'object_id')

    def __str__(self):
        return f"{self.user} likes {self.content_object}"
