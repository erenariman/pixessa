from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

User = get_user_model()


class NotificationManager(models.Manager):
    def unread(self, user):
        return self.filter(user=user, is_read=False)

    def mark_all_as_read(self, user):
        return self.filter(user=user, is_read=False).update(is_read=True)

    def for_content_object(self, content_object):
        content_type = ContentType.objects.get_for_model(content_object)
        return self.filter(
            content_type=content_type,
            object_id=content_object.pk
        )

    def create_notification(self, user, notification_type, content_object):
        content_type = ContentType.objects.get_for_model(content_object)
        return self.create(
            user=user,
            notification_type=notification_type,
            content_type=content_type,
            object_id=content_object.pk
        )


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('message', 'Message'),
        ('mention', 'Mention'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = NotificationManager()

    def __str__(self):
        return f"{self.notification_type} notification for {self.user}"
