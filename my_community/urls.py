from django.urls import path

from .views import *

urlpatterns = [
    path('home/', index),
    path('about_page/', about_page)
    path('topic/', topic_page)
]
