from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, TemplateView

from my_community.models import Category, Topic


def index(request):
    return HttpResponse({"a": 1})


def categories(request):
    return HttpResponse("<h1>Categories</h1>")


def about_page(request):
    return HttpResponse("About_this_page")


class TopicDetailView(DetailView):
    model = Topic
    template_name = "my_community/topic_detail.html"
    context_object_name = "topic"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        topic = get_object_or_404(Topic, slug=slug)
        context["topic"] = topic
        return context


class IndexView(TemplateView):
    template_name = "my_community/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        topics = Topic.objects.all()
        context["topics"] = topics
        context["categories"] = categories
        context["cat_selected"] = 0
        return context


class CategoryView(TemplateView):
    template_name = "my_community/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        categories = Category.objects.all()
        topics = Topic.objects.filter(categories__slug=slug).select_related(
            "author"
        )
        context["topics"] = topics
        context["categories"] = categories
        context["cat_selected"] = categories.filter(slug=slug).first()
        return context
