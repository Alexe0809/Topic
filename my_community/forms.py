from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User


def password_validator(value):
    try:
        validate_password(value)
    except ValidationError as e:
        raise ValidationError(e.messages)


class UserRegistration(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput, validators=[password_validator]
    )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # хэшируем
        if commit:
            user.save()
        return user

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
