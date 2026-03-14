import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from my_community.mixins.model_mixins import SlugGeneratorMixin
from my_community.utils.model_utils import (
    get_dict_with_reaction_counts,
    reaction_action,
)
from my_community.validators.model_validators import password_validator


class UUIDModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("ID"),
    )

    class Meta:
        abstract = True


class BaseReaction(UUIDModel):
    class ReactionType(models.TextChoices):
        LIKE = "like", "Лайк"
        DISLIKE = "dislike", "Дизлайк"

    reaction_type = models.CharField(
        max_length=10, choices=ReactionType.choices, default=ReactionType.LIKE
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        abstract = True


class Category(SlugGeneratorMixin, UUIDModel):
    name = models.CharField(max_length=50, null=False)
    slug = models.SlugField(unique=True, null=False)
    description = models.TextField(max_length=1000, null=True)
    order = models.IntegerField(default=0)

    slug_field_name = "name"
    SAVE_LIMIT = 10

    def get_absolute_url(self):
        return reverse("category", kwargs={"slug": self.slug})

    def __str__(self):
        return self.name


class User(SlugGeneratorMixin, UUIDModel, AbstractUser):
    username_validator = RegexValidator(
        regex=r"^(?=.*[A-Za-z])[A-Za-z0-9_@/-]*$",
        message="Invalid username: must contain at least one letter and only letters,"
        " numbers, or '_', '@', '-', '/' are allowed.",
    )
    username = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        unique=True,
        validators=[username_validator],
    )
    password = models.CharField(
        max_length=50, null=False, blank=False, validators=[password_validator]
    )
    email = models.EmailField(unique=True, blank=False)
    slug = models.SlugField(unique=True, null=False)
    phone = PhoneNumberField(region=None, unique=False, blank=True, null=False)
    is_email_verified = models.BooleanField(default=False)
    description = models.CharField(max_length=350, blank=True)
    image = models.ImageField(
        null=True, blank=True, upload_to="static/avatars/"
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    order = models.IntegerField(default=0)
    groups = models.ManyToManyField(
        Group,
        related_name="custom_users",
        blank=True,
        help_text="The groups this user belongs to.",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
    )
    slug_field_name = "username"
    SAVE_LIMIT = 10


class ReactionInterface:
    def like_action(self, user):
        raise NotImplementedError

    def dislike_action(self, user):
        raise NotImplementedError


class Topic(ReactionInterface, SlugGeneratorMixin, UUIDModel):
    name = models.CharField(_("name"), max_length=100, null=False)
    description = models.TextField(_("description"))
    slug = models.SlugField(_("slug"), max_length=250, unique=True)
    is_pinned = models.BooleanField(_("is pinned"), default=False)
    is_closed = models.BooleanField(_("is closed"), default=False)
    is_archived = models.BooleanField(_("is archived"), default=False)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="topics"
    )
    categories = models.ManyToManyField(
        Category, related_name="topics", blank=True
    )
    views = models.PositiveIntegerField(_("views"), default=0)

    slug_field_name = "name"
    SAVE_LIMIT = 10

    def get_absolute_url(self):
        return reverse("topic", kwargs={"slug": self.slug})

    def like_action(self, user):
        return reaction_action(
            reaction_model=TopicReaction,
            user=user,
            target_field="topic",
            target=self,
            reaction_type=TopicReaction.ReactionType.LIKE,
        )

    def dislike_action(self, user):
        return reaction_action(
            reaction_model=TopicReaction,
            user=user,
            target_field="topic",
            target=self,
            reaction_type=TopicReaction.ReactionType.DISLIKE,
        )

    def get_like_dislike_dict(self):
        return get_dict_with_reaction_counts(TopicReaction, "topic", self)


class BaseConfirmation(UUIDModel):
    token = models.CharField(
        _("token"),
        max_length=255,
        unique=True,
    )

    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True,
    )

    expires_at = models.DateTimeField(
        _("expires at"),
    )

    confirmed_at = models.DateTimeField(
        _("confirmed at"),
        null=True,
        blank=True,
    )

    is_used = models.BooleanField(
        _("is used"),
        default=False,
    )

    class Meta:
        abstract = True

    @classmethod
    def _generate_token(cls):
        return uuid.uuid4().hex + uuid.uuid4().hex

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired

    def confirm(self):
        raise ValueError("undefined")

    @classmethod
    def create_for_user(cls, user, expiration_hours=24):
        cls.objects.filter(user=user, is_used=False).update(is_used=True)

        return cls.objects.create(
            user=user,
            token=cls._generate_token(),
            expires_at=timezone.now() + timedelta(hours=expiration_hours),
        )


class PasswordResetConfirmation(BaseConfirmation):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_confirmations",
        verbose_name=_("user"),
    )

    class Meta:
        verbose_name = _("password reset confirmation")
        verbose_name_plural = _("password resets confirmations")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Password reset confirmation for {self.user.email} ({self.created_at})"

    def confirm(self):
        if not self.is_valid:
            raise ValueError(_("Token is invalid, expired or already used"))

        self.is_used = True
        self.confirmed_at = timezone.now()
        self.save()

        return True

    def get_confirmation_url(self):
        from django.urls import reverse

        return reverse("reset_password", kwargs={"token": self.token})


class EmailConfirmation(BaseConfirmation):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="email_confirmations",
        verbose_name=_("user"),
    )

    class Meta:
        verbose_name = _("email confirmation")
        verbose_name_plural = _("email confirmations")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Email confirmation for {self.user.email} ({self.created_at})"

    def confirm(self):
        if not self.is_valid:
            raise ValueError(_("Token is invalid, expired or already used"))

        self.is_used = True
        self.confirmed_at = timezone.now()
        self.user.is_email_verified = True
        self.user.save()
        self.save()

        return True

    def get_confirmation_url(self):
        from django.urls import reverse

        return reverse("confirm-email", kwargs={"token": self.token})


class Comment(ReactionInterface, UUIDModel):
    description = models.CharField(
        _("description"),
        max_length=1024,
        blank=True,
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

    def like_action(self, user):
        return reaction_action(
            reaction_model=CommentReaction,
            user=user,
            target_field="comment",
            target=self,
            reaction_type=CommentReaction.ReactionType.LIKE,
        )

    def dislike_action(self, user):
        return reaction_action(
            reaction_model=CommentReaction,
            user=user,
            target_field="comment",
            target=self,
            reaction_type=CommentReaction.ReactionType.DISLIKE,
        )

    def get_like_dislike_dict(self):
        return get_dict_with_reaction_counts(CommentReaction, "comment", self)


class CommentReaction(BaseReaction):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comment_reaction",
    )
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="reaction"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "comment"], name="unique_user_comment_reaction"
            )
        ]
        indexes = [
            models.Index(fields=["comment", "reaction_type"]),
            models.Index(fields=["user", "comment"]),
        ]


class TopicReaction(BaseReaction):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="topic_reaction",
    )
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name="reaction"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "topic"], name="unique_user_topic_reaction"
            )
        ]
        indexes = [
            models.Index(fields=["topic", "reaction_type"]),
            models.Index(fields=["user", "topic"]),
        ]
