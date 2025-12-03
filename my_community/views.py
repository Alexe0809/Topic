from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return HttpResponse({"a": 1})


def categories(request):
    return HttpResponse('<h1>Categories</h1>')


def about_page(request):
    return HttpResponse('About_this_page')
def topic_page(request):
    return HttpResponse('<h1>topic_page</h1>')

