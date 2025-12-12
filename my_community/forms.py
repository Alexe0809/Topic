from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import User


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
