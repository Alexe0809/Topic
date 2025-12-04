import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


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


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(max_length=1000)
    order = models.IntegerField(default=0)
