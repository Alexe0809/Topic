import pytest

from my_community.forms import UserLogin, UserRegistration
from my_community.models import User
from my_community.tests.factories import UserTestData

data = {
    "username": UserTestData.valid_usernames(),
    "password": UserTestData.valid_passwords(),
    "phone": UserTestData.valid_phones(),
    "email": UserTestData.valid_emails(),
    "first_name": "Alex",
    "last_name": "OJOIJ",
}


@pytest.mark.django_db
def test_valid_form():
    form = UserRegistration(data)
    assert form.is_valid(), f"Форма невалидна: {form.errors}"


@pytest.mark.django_db
def test_invalid_username():
    field = data.copy()
    field["username"] = UserTestData.invalid_usernames()
    form = UserRegistration(field)
    assert not form.is_valid(), f"Форма невалидна: {form.errors}"


@pytest.mark.django_db
def test_invalid_password():
    field = data.copy()
    field["password"] = UserTestData.invalid_passwords()
    form = UserRegistration(field)
    assert not form.is_valid(), f"Форма невалидна: {form.errors}"


@pytest.mark.django_db
def test_invalid_phone():
    field = data.copy()
    field["phone"] = UserTestData.invalid_phones()
    form = UserRegistration(field)
    assert not form.is_valid(), f"Форма невалидна: {form.errors}"


@pytest.mark.django_db
def test_invalid_email():
    field = data.copy()
    field["email"] = UserTestData.invalid_emails()
    form = UserRegistration(field)
    assert not form.is_valid(), f"Форма невалидна: {form.errors}"


@pytest.mark.django_db
def test_correct_context():
    field = data.copy()
    form = UserRegistration(field)
    assert form.is_valid()

    user = form.save()
    user_from_bd = User.objects.get(id=user.id)
    assert user_from_bd.username == field["username"]
    assert user_from_bd.email == field["email"]
    assert user_from_bd.first_name == field["first_name"]
    assert user_from_bd.last_name == field["last_name"]


@pytest.mark.django_db
def test_unique_username():
    field1 = data.copy()
    field2 = data.copy()
    form1 = UserRegistration(field1)
    form1.save()
    assert form1.is_valid()
    form2 = UserRegistration(field2)
    assert not form2.is_valid(), f"Форма невалидна: {form2.errors}"


@pytest.mark.django_db
def test_login_valid():
    User.objects.create_user(**data)
    username = data["username"]
    password = data["password"]
    form = UserLogin(
        request=None, data={"username": username, "password": password}
    )
    assert form.is_valid()
    assert form.cleaned_data["username"] == username


@pytest.mark.django_db
def test_login_invalid_username():
    username = "invalid_username"
    password = data["password"]
    form = UserLogin(
        request=None, data={"username": username, "password": password}
    )
    assert not form.is_valid()


@pytest.mark.django_db
def test_login_invalid_password():
    username = data["username"]
    password = "invalid_password"
    form = UserLogin(
        request=None, data={"username": username, "password": password}
    )
    assert not form.is_valid()
