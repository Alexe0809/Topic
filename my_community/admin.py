from django.contrib import admin

from my_community.models import Category, Topic


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "is_pinned",
        "is_closed",
        "is_archived",
        "created_at",
    ]

    list_filter = ["is_pinned", "is_closed", "is_archived", "created_at"]

    search_fields = ["name", "description", "slug"]

    list_editable = ["is_pinned", "is_closed", "is_archived"]

    list_per_page = 50

    ordering = ["-created_at"]

    readonly_fields = ["created_at", "updated_at", "slug"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "description",
        "order",
    ]

    search_fields = ["name", "description", "slug"]

    ordering = ["order", "name"]

    list_per_page = 10


