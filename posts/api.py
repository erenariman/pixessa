from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser


from accounts.api import UserSerializer
from hate_speech_model.preprocessing import preprocess_text
from hate_speech_model.utils.model_loader import load_model
from .models import Post, PostMedia, Comment, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ['id', 'file', 'media_type', 'order']


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    media = PostMediaSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user', 'caption', 'location', 'tags',
                  'media', 'created_at', 'likes_count', 'comments_count']
        read_only_fields = ['user']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def create(self, validated_data):
        # Automatically assign the logged in user as the post creator.
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Post.objects.none()

    def get_queryset(self):
        return Post.objects.all().prefetch_related('media', 'tags')

    @action(detail=False, methods=['get'])
    def feed(self, request):
        following_ids = request.user.following.values_list('id', flat=True)
        posts = Post.objects.filter(user__in=following_ids).order_by('-created_at')
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)


class PostMediaViewSet(viewsets.ModelViewSet):
    """
    This viewset allows you to create and manage PostMedia instances via multipart form data.
    It is assumed that this viewset is nested under the Post endpoint (e.g. /posts/{post_pk}/media/).
    """
    serializer_class = PostMediaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        # Only return media for the given post.
        return PostMedia.objects.filter(post_id=self.kwargs['post_pk'])

    def perform_create(self, serializer):
        # Get the parent post and save the media instance with it.
        post = Post.objects.get(pk=self.kwargs['post_pk'])
        serializer.save(post=post)


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'parent', 'created_at', 'replies', 'is_offensive', 'hate_score']
        read_only_fields = ['user', 'created_at', 'is_offensive', 'hate_score']

    def get_replies(self, obj):
        return CommentSerializer(obj.replies.all(), many=True).data


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Only return comments for the given post.
        return Comment.objects.filter(
            post_id=self.kwargs['post_pk'],
            is_offensive=False
        )

    def create(self, request, *args, **kwargs):
        # Get the associated post
        post = Post.objects.get(pk=self.kwargs['post_pk'])

        # Make a mutable copy of request data
        data = request.data.copy()
        data['user'] = request.user.id
        data['post'] = post.id

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Hate speech detection
        content = serializer.validated_data['content']
        model, vectorizer = load_model()
        cleaned_text = preprocess_text(content)
        text_vec = vectorizer.transform([cleaned_text])
        hate_prob = model.predict_proba(text_vec)[0][1]

        # Moderate based on threshold
        if hate_prob > 0.65:  # Block clearly hateful comments
            return Response({
                'detail': 'Comment violates community guidelines',
                'hate_probability': hate_prob,
                'threshold': 0.65
            }, status=status.HTTP_403_FORBIDDEN)

        # Save with moderation info
        comment = serializer.save(
            user=request.user,
            post=post,
            hate_score=hate_prob,
            is_offensive=hate_prob > 0.65  # Auto-approve safe comments
        )

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        post = Post.objects.get(pk=self.kwargs['post_pk'])
        serializer.save(user=self.request.user, post=post)

    def get_serializer_context(self):
        # Add post_pk to context for hyperlinked relationships
        context = super().get_serializer_context()
        context['post_pk'] = self.kwargs['post_pk']
        return context

