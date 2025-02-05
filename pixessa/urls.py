from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from accounts.api import UserViewSet, FollowRequestViewSet
from posts.api import PostViewSet, CommentViewSet, PostMediaViewSet
from likes.api import LikeViewSet
from messaging.api import ConversationViewSet, MessageViewSet
from notifications.api import NotificationViewSet
from blocks.api import BlockViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'follow-requests', FollowRequestViewSet, basename='followrequest')
router.register(r'posts', PostViewSet)
router.register(r'likes', LikeViewSet)
router.register(r'conversations', ConversationViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'blocks', BlockViewSet)

posts_router = routers.NestedSimpleRouter(router, r'posts', lookup='post')
posts_router.register(r'media', PostMediaViewSet, basename='post-media')
posts_router.register(r'comments', CommentViewSet, basename='post-comments')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/', include(posts_router.urls)),

    path('api/conversations/<int:conversation_pk>/messages/', MessageViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='conversation-messages'),

    path('api/', include(router.urls)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
