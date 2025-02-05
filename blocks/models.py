from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class BlockManager(models.Manager):
    def is_blocked(self, blocker, blocked):
        return self.filter(blocker=blocker, blocked=blocked).exists()

    def get_blocked_users(self, user):
        return self.filter(blocker=user).select_related('blocked')

    def get_blockers(self, user):
        return self.filter(blocked=user).select_related('blocker')


class Block(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocking')
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blockers')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BlockManager()

    class Meta:
        unique_together = ('blocker', 'blocked')

    def __str__(self):
        return f"{self.blocker} blocks {self.blocked}"
