from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class ConversationManager(models.Manager):
    def get_or_create_conversation(self, participants):
        participants = sorted(participants, key=lambda x: x.id)
        conversation = self.filter(participants__in=participants).distinct()
        for conv in conversation:
            if set(conv.participants.all()) == set(participants):
                return conv, False
        conversation = self.create()
        conversation.participants.set(participants)
        return conversation, True

    def user_conversations(self, user):
        return self.filter(participants=user).prefetch_related('participants', 'messages')

class MessageManager(models.Manager):
    def unread_messages(self, user):
        return self.filter(conversation__participants=user, read=False).exclude(sender=user)

    def mark_as_read(self, message_ids):
        return self.filter(id__in=message_ids).update(read=True)

    def recent_messages(self, conversation, limit=50):
        return self.filter(conversation=conversation).order_by('-timestamp')[:limit]


class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ConversationManager()

    def __str__(self):
        return f"Conversation {self.id}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    objects = MessageManager()

    def __str__(self):
        return f"Message from {self.sender} in {self.conversation}"
