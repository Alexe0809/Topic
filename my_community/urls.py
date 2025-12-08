from django.urls import path

from .views import (
    CategoryView,
    ConfirmView,
    IndexView,
    TopicDetailView,
    about_page,
)

urlpatterns = [
    path("", IndexView.as_view()),
    path("category/<slug:slug>", CategoryView.as_view(), name="category"),
    path("about_page/", about_page),
    path("topic/<slug:slug>", TopicDetailView.as_view(), name="topic"),
    path(
        "confirmation/<str:token>", ConfirmView.as_view(), name="confirm-email"
    ),
]
