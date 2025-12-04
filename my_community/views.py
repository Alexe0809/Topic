from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from my_community.models import Topic


def index(request):
    return HttpResponse({"a": 1})


def categories(request):
    return HttpResponse("<h1>Categories</h1>")


def about_page(request):
    return HttpResponse("About_this_page")


def topic_page(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    return HttpResponse(f"<h1>{topic.name}</h1>")


class IndexView(TemplateView):
    template_name = "my_community/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topics = Topic.objects.all()
        context["topics"] = topics
        return context
