from django.contrib import admin

from my_community.models import Category, Topic, User


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


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "user_name",
        "slug",
        "phone",
        "email",
        "created_at",
        "updated_at",
        "is_email_verified",
    ]

    list_filter = ["user_name", "created_at"]

    search_fields = ["user_name", "email"]

    list_editable = ["is_email_verified"]

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