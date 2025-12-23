from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


def password_validator(value):
    try:
        validate_password(value)
    except ValidationError as e:
        raise ValidationError(e.messages)
