# serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers

from my_community.models import (
    BaseReaction,
    Comment,
    CommentReaction,
    Topic,
    TopicReaction,
)

User = get_user_model()


class ReactionSerializer(serializers.Serializer):
    reaction_type = serializers.ChoiceField(
        choices=BaseReaction.ReactionType.choices, required=True
    )

    def validate_reaction_type(self, value):
        if value not in ["like", "dislike"]:
            raise serializers.ValidationError("Только 'like' или 'dislike'")
        return value


class CommentReactionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CommentReaction
        fields = ["id", "user", "comment", "reaction_type", "created_at"]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {"comment": {"required": True}}


class TopicReactionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TopicReaction
        fields = ["id", "user", "topic", "reaction_type", "created_at"]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {"topic": {"required": True}}


class CommentDetailSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "description",
            "created_at",
            "updated_at",
            "author",
            "topic",
            "parent",
            "user_reaction",
        ]

    def get_user_reaction(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            try:
                reaction = CommentReaction.objects.get(
                    user=request.user, comment=obj
                )
                return reaction.reaction_type
            except CommentReaction.DoesNotExist:
                return None
        return None


class TopicDetailSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
            "author",
            "user_reaction",
        ]

    def get_user_reaction(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            try:
                reaction = TopicReaction.objects.get(
                    user=request.user, topic=obj
                )
                return reaction.reaction_type
            except TopicReaction.DoesNotExist:
                return None
        return None
