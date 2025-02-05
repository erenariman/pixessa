from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, FollowRequest


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'password2',
            'bio', 'profile_picture', 'is_private'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.bio = validated_data.get('bio', '')
        user.profile_picture = validated_data.get('profile_picture')
        user.is_private = validated_data.get('is_private', False)
        user.save()
        return user


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        user_to_follow = self.get_object()
        if request.user == user_to_follow:
            return Response({'error': 'You cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)

        if user_to_follow.is_private:
            FollowRequest.objects.get_or_create(requester=request.user, receiver=user_to_follow)
            return Response({'status': 'follow request sent'})
        else:
            request.user.following.add(user_to_follow)
            return Response({'status': 'following'})

    @action(detail=True, methods=['post'])
    def unfollow(self, request, pk=None):
        user_to_unfollow = self.get_object()
        request.user.following.remove(user_to_unfollow)
        return Response({'status': 'unfollowed'})


class FollowRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowRequest
        fields = ['id', 'requester', 'receiver', 'status', 'created_at']


class FollowRequestViewSet(viewsets.ModelViewSet):
    serializer_class = FollowRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FollowRequest.objects.filter(receiver=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        follow_request = self.get_object()
        follow_request.status = 'accepted'
        follow_request.save()
        follow_request.requester.following.add(follow_request.receiver)
        return Response({'status': 'request approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        follow_request = self.get_object()
        follow_request.status = 'rejected'
        follow_request.save()
        return Response({'status': 'request rejected'})
