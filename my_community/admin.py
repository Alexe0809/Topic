from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from my_community.models import Category, EmailConfirmation, Topic, User


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
class CustomUserAdmin(UserAdmin):
    model = User

    # Поля, которые показываются в списке пользователей
    list_display = (
        "username",
        "email",
        "phone",
        "is_staff",
        "is_superuser",
        "is_active",
        "is_email_verified",
        "created_at",
    )

    # Фильтры справа
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "is_email_verified",
        "groups",
    )

    # Поиск
    search_fields = ("username", "email", "phone")

    # Поля только для чтения
    readonly_fields = ("created_at", "updated_at", "phone")

    # Блоки в форме редактирования пользователя
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "email",
                    "phone",
                    "image",
                    "slug",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_email_verified",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important dates",
            {
                "fields": (
                    "last_login",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    # Поля при создании пользователя через админку
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "phone",
                    "slug",
                    "image",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_email_verified",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )

    ordering = ("created_at",)


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

    readonly_fields = ["slug"]

    list_per_page = 10


@admin.register(EmailConfirmation)
class EmailConfirmationAdmin(admin.ModelAdmin):
    list_display = [
        "created_at",
        "expires_at",
        "confirmed_at",
    ]

    list_filter = [
        "is_used",
        ("created_at", admin.DateFieldListFilter),
        ("expires_at", admin.DateFieldListFilter),
        "user__is_email_verified",
    ]

    search_fields = [
        "token",
        "user__email",
        "user__username",
        "user__phone",
    ]

    ordering = ["-created_at"]
    readonly_fields = [
        "token",
        "created_at",
    ]

    autocomplete_fields = ["user"]
