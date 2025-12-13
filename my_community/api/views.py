# views_simple.py
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from my_community.models import Comment, Topic


class CommentLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        comment.like_action(request.user)
        return Response({"likes": comment.like, "dislikes": comment.dislike})


class CommentDislikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        comment.dislike_action(request.user)
        return Response({"likes": comment.like, "dislikes": comment.dislike})


class TopicLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id)
        topic.like_action(request.user)
        return Response({"likes": topic.like, "dislikes": topic.dislike})


class TopicDislikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id)
        topic.dislike_action(request.user)
        return Response({"likes": topic.like, "dislikes": topic.dislike})
