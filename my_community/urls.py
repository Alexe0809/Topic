from django.urls import path

from .views import CategoryView, IndexView, TopicDetailView, about_page

urlpatterns = [
    path("home/", IndexView.as_view()),
    path("category/<slug:slug>", CategoryView.as_view(), name="category"),
    path("about_page/", about_page),
    path("topic/<slug:slug>", TopicDetailView.as_view(), name="topic"),
]
