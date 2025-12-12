from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import DetailView, TemplateView

from my_community.forms import UserRegistration
from my_community.models import Category, EmailConfirmation, Topic


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


class ConfirmView(TemplateView):
    template_name = "my_community/email_confirm.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.kwargs.get("token")
        confirmation = get_object_or_404(EmailConfirmation, token=token)
        try:
            if confirmation.confirm():
                context["success"] = True
                context["message"] = "Email успешно подтверждён"
        except ValueError as e:
            context["expired"] = True
            context["message"] = str(e)

        except EmailConfirmation.DoesNotExist:
            context["else"] = True
            context["message"] = "Токен не найден"

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


def registration_form(request):
    if request.method == "POST":
        form = UserRegistration(request.POST)
        if form.is_valid():
            user = form.save()
            EmailConfirmation.create_for_user(user)
            return redirect(reverse("home"))

    else:
        form = UserRegistration()
    return render(request, "my_community/register.html", {"form": form})


def terms_page(request):
    return render(request, "my_community/terms.html")


def privacy_form(request):
    return render(request, "my_community/privacy.html")
