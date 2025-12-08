import uuid

from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from slugify import slugify


class SlugGeneratorMixin:
    def save(self, *args, **kwargs):
        priority_slug_fields = ["name", "user_name"]
        slug_value = None

        for field in priority_slug_fields:
            if hasattr(self, field):
                value = getattr(self, field)
                if value:
                    slug_value = str(value)
                    break

        if not slug_value:
            raise AttributeError("No valid field found for slug generation")

        if not self.slug:
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


class Category(SlugGeneratorMixin, UUIDModel):
    name = models.CharField(max_length=50, null=False)
    slug = models.SlugField(unique=True, null=False)
    description = models.TextField(max_length=1000, null=True)
    order = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse("category", kwargs={"slug": self.slug})

    def __str__(self):
        return self.name


class User(SlugGeneratorMixin, UUIDModel):
    phone_validator = RegexValidator(
        regex=r"^[0-9A-Za-z+\-\s()]", message="Invalid phone number"
    )
    email_validator = RegexValidator(
        regex=r"[0-9A-Za-z\-_@\.]", message="Invalid email"
    )
    user_name_validator = RegexValidator(
        regex=r"[0-9A-Za-z-\_]", message="Invalid name"
    )

    user_name = models.CharField(
        max_length=30, null=False, blank=False, validators=[user_name_validator]
    )
    slug = models.SlugField(unique=True, null=False)
    phone = models.CharField(
        max_length=20, blank=False, null=False, validators=[phone_validator]
    )
    email = models.CharField(
        max_length=50, blank=False, null=False, validators=[email_validator]
    )
    is_email_verified = models.BooleanField(default=False)
    image = models.ImageField(
        null=True, blank=True, upload_to="static/avatars/"
    )
    hashed_password = models.CharField(max_length=60, null=False, blank=False)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    description = models.TextField(max_length=1000, null=True)
    order = models.IntegerField(default=0)


class Topic(SlugGeneratorMixin, UUIDModel):
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

    def get_absolute_url(self):
        return reverse("topic", kwargs={"slug": self.slug})


class Comment(UUIDModel):
    description = models.CharField(
        _("description"),
        max_length=1024,
        blank=True,
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    like = models.PositiveIntegerField(_("likes"), default=0)
    dislike = models.PositiveIntegerField(_("dislikes"), default=0)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
