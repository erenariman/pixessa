from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from .models import Like


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'content_object', 'created_at']
        read_only_fields = ['user', 'content_object']


class LikeViewSet(viewsets.ModelViewSet):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Like.objects.none()

    def get_queryset(self):
        return Like.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        content_type = ContentType.objects.get_for_id(request.data['content_type_id'])
        obj = content_type.get_object_for_this_type(pk=request.data['object_id'])
        like, created = Like.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=obj.id
        )
        if not created:
            like.delete()
            return Response({'status': 'unliked'})
        return Response({'status': 'liked'})
