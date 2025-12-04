from django.urls import path

from .views import about_page, index, topic_page

urlpatterns = [
    path("home/", index),
    path("about_page/", about_page),
    path("topic/", topic_page),
]
