from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    content_object = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'content_object', 'is_read', 'created_at']

    def get_content_object(self, obj):
        # Implement custom logic to serialize different content objects
        return str(obj.content_object)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Notification.objects.none()

    def get_queryset(self):
        return self.request.user.notifications.all().order_by('-created_at')

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return Response({'status': 'all notifications marked as read'})