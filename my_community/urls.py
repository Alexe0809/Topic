from django.urls import path

from .views import (
    CategoryView,
    ConfirmView,
    IndexView,
    TopicDetailView,
    login_form,
    logout_view,
    privacy_form,
    registration_form,
    reset_password,
    terms_page,
)

urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path("category/<slug:slug>", CategoryView.as_view(), name="category"),
    path("topic/<slug:slug>", TopicDetailView.as_view(), name="topic"),
    path("register/", registration_form, name="register"),
    path("login/", login_form, name="login"),
    path("reset_password/<str:token>", reset_password, name="reset_password"),
    path("logout/", logout_view, name="logout"),
    path("privacy/", privacy_form, name="privacy"),
    path("terms/", terms_page, name="terms"),
    path(
        "confirmation/<str:token>", ConfirmView.as_view(), name="confirm-email"
    ),
]
