from django.urls import path

from .views import (
    CommentDislikeView,
    CommentLikeView,
    TopicDislikeView,
    TopicLikeView,
)

urlpatterns = [
    # Для комментариев
    path(
        "api/comments/<uuid:comment_id>/like/",
        CommentLikeView.as_view(),
        name="comment-like",
    ),
    path(
        "api/comments/<uuid:comment_id>/dislike/",
        CommentDislikeView.as_view(),
        name="comment-dislike",
    ),
    # Для тем
    path(
        "api/topics/<uuid:topic_id>/like/",
        TopicLikeView.as_view(),
        name="topic-like",
    ),
    path(
        "api/topics/<uuid:topic_id>/dislike/",
        TopicDislikeView.as_view(),
        name="topic-dislike",
    ),
]
