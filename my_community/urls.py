from django.urls import path

from .views import IndexView, about_page, topic_page

urlpatterns = [
    path("home/", IndexView.as_view()),
    path("about_page/", about_page),
    path("topic/<slug:slug>", topic_page, name="topic"),
]
