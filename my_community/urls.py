from django.urls import path

from .views import IndexView, TopicDetailView, about_page

urlpatterns = [
    path("home/", IndexView.as_view()),
    path("about_page/", about_page),
    path("topic/<slug:slug>", TopicDetailView.as_view(), name="topic"),
]
