from django import forms

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
