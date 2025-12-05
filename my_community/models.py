import uuid

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from slugify import slugify


class UUIDModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("ID"),
    )


class Topic(UUIDModel):
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

    def get_absolute_url(self):
        return reverse("topic", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
            counter = 1
            while Topic.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1

        if not self.slug:
            self.slug = slugify(self.name)

        if Topic.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{self.slug}-{uuid.uuid4().hex[:8]}"

        super().save(*args, **kwargs)
