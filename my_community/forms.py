from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Category, Topic, User


class UserRegistration(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "phone",
            "email",
            "first_name",
            "last_name",
        ]


class UserLogin(AuthenticationForm):
    username = forms.CharField(
        label="Имя пользователя",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите имя пользователя",
            }
        ),
    )

    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Введите пароль"}
        ),
    )

    class Meta:
        fields = ["username", "password"]


class ResetPasswordForm(forms.Form):
    email = forms.CharField(
        label="Введите почту",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Почта",
            }
        ),
    )


class TopicForm(forms.ModelForm):
    new_category = forms.CharField(
        required=False,
        max_length=50,
        label="Новая категория",
        help_text="Создать новую категорию",
    )

    class Meta:
        model = Topic
        fields = ["name", "description", "categories"]
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 10,
                    "placeholder": "Подробно опишите вашу тему...",
                }
            ),
            "name": forms.TextInput(
                attrs={"placeholder": "Введите название темы..."}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categories"].required = False
        self.fields["categories"].queryset = Category.objects.all().order_by(
            "name"
        )
        self.fields["categories"].widget.attrs.update(
            {"class": "form-check-input"}
        )
