from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Block


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ['id', 'blocked', 'created_at']
        read_only_fields = ['blocker']


class BlockViewSet(viewsets.ModelViewSet):
    serializer_class = BlockSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Block.objects.none()

    def get_queryset(self):
        return Block.objects.filter(blocker=self.request.user)

    def perform_create(self, serializer):
        serializer.save(blocker=self.request.user)

    @action(detail=True, methods=['post'])
    def unblock(self, request, pk=None):
        block = self.get_object()
        block.delete()
        return Response({'status': 'user unblocked'})