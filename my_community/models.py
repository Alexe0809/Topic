import uuid
from datetime import timedelta
from typing import Any

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from slugify import slugify


class SlugGeneratorMixin:
    def save(self, *args, **kwargs):
        if not self.slug:
            priority_slug_fields = ["name", "username"]
            slug_value = None

            for field in priority_slug_fields:
                if hasattr(self, field):
                    value = getattr(self, field)
                    if value:
                        slug_value = str(value)
                        break

            if not slug_value:
                raise AttributeError("No valid field found for slug generation")

            base_slug = slugify(slug_value)
            if not base_slug:
                base_slug = "item"

            model_class = self.__class__
            candidate = base_slug
            counter = 1

            while model_class.objects.filter(slug=candidate).exists():
                candidate = f"{base_slug}-{counter}"
                counter += 1
                if counter > 100:
                    candidate = f"{base_slug}-{uuid.uuid4().hex[:8]}"
                    break

            self.slug = candidate

            if (
                self.__class__.objects.filter(slug=self.slug)
                .exclude(pk=self.pk)
                .exists()
            ):
                self.slug = f"{self.slug}-{uuid.uuid4().hex[:8]}"

        super().save(*args, **kwargs)


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
    email = models.EmailField(unique=True, blank=False)
    slug = models.SlugField(unique=True, null=False)
    phone = PhoneNumberField(region=None, unique=False, blank=True, null=False)
    is_email_verified = models.BooleanField(default=False)
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


class ReactionInterface:
    def like_action(self, user: User):
        pass

    def dislike_action(self, user: User):
        pass

    def create_reaction(
        self,
        user: User,
        reaction_type: BaseReaction.ReactionType,
        reaction_model: Any,
    ):
        try:
            if reaction_model == TopicReaction:
                reaction = reaction_model.objects.get(user=user, topic=self)
            else:
                reaction = reaction_model.objects.get(user=user, comment=self)
            if reaction.reaction_type == reaction_type:
                reaction.delete()
                if reaction_type == BaseReaction.ReactionType.LIKE:
                    self.like = max(0, self.like - 1)
                else:
                    self.dislike = max(0, self.dislike - 1)
            else:
                reaction.reaction_type = reaction_type
                reaction.save()
                if reaction_type == BaseReaction.ReactionType.LIKE:
                    self.like += 1
                    self.dislike = max(0, self.dislike - 1)
                else:
                    self.dislike += 1
                    self.like = max(0, self.like - 1)
        except reaction_model.DoesNotExist:
            if reaction_model == TopicReaction:
                reaction_model.objects.create(
                    user=user, topic=self, reaction_type=reaction_type
                )
            else:
                reaction_model.objects.create(
                    user=user, comment=self, reaction_type=reaction_type
                )
            if reaction_type == BaseReaction.ReactionType.LIKE:
                self.like += 1
            else:
                self.dislike += 1

        self.save()


class Topic(ReactionInterface, SlugGeneratorMixin, UUIDModel):
    name = models.CharField(_("name"), max_length=100, null=False)
    description = models.CharField(
        _("description"),
        max_length=1024,
        blank=True,
    )
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
    like = models.PositiveIntegerField(_("likes"), default=0)
    dislike = models.PositiveIntegerField(_("dislikes"), default=0)

    def get_absolute_url(self):
        return reverse("topic", kwargs={"slug": self.slug})

    @transaction.atomic
    def like_action(self, user: User):
        self.create_reaction(
            user,
            reaction_type=BaseReaction.ReactionType.LIKE,
            reaction_model=TopicReaction,
        )

    @transaction.atomic
    def dislike_action(self, user: User):
        self.create_reaction(
            user,
            reaction_type=BaseReaction.ReactionType.DISLIKE,
            reaction_model=TopicReaction,
        )


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

    def __str__(self):
        return "No defined"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)

        if not self.token:
            self.token = self._generate_token()

        super().save(*args, **kwargs)

    def _generate_token(self):
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
            expires_at=timezone.now() + timedelta(hours=expiration_hours),
        )

    @classmethod
    def validate_token(cls, token):
        try:
            confirmation = cls.objects.get(token=token)
            if confirmation.is_valid:
                confirmation.confirm()
                return confirmation
            return None
        except cls.DoesNotExist:
            return None


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
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name="comments"
    )
    like = models.PositiveIntegerField(_("likes"), default=0)
    dislike = models.PositiveIntegerField(_("dislikes"), default=0)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

    @transaction.atomic
    def like_action(self, user: User):
        self.create_reaction(
            user,
            reaction_type=BaseReaction.ReactionType.LIKE,
            reaction_model=CommentReaction,
        )

    @transaction.atomic
    def dislike_action(self, user: User):
        self.create_reaction(
            user,
            reaction_type=BaseReaction.ReactionType.DISLIKE,
            reaction_model=CommentReaction,
        )


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
