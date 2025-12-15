from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import DetailView, TemplateView

from my_community.forms import UserLogin, UserRegistration
from my_community.models import (
    Category,
    EmailConfirmation,
    PasswordResetConfirmation,
    Topic,
    TopicReaction,
)
from my_community.notifications.tasks import (
    send_email_confirm,
)


class TopicDetailView(DetailView):
    model = Topic
    template_name = "my_community/topic_detail.html"
    context_object_name = "topic"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        user = self.request.user
        topic = get_object_or_404(Topic, slug=slug)
        if user is not None:
            try:
                reaction = TopicReaction.objects.get(user=user, topic=topic)
                context["user_reaction"] = reaction.reaction_type
            except TopicReaction.DoesNotExist:
                context["user_reaction"] = None
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
            email_conf = EmailConfirmation.create_for_user(user)
            email_message_data = {
                "email": user.email,
                "url": email_conf.get_confirmation_url(),
                "username": user.username,
            }
            send_email_confirm.delay(email_message_data)
            return redirect(reverse("home"))

    else:
        form = UserRegistration()
    return render(request, "my_community/register.html", {"form": form})


def login_form(request):
    if request.method == "POST":
        form = UserLogin(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
    else:
        form = UserLogin(request)
    return render(request, "my_community/login.html", {"form": form})


def reset_password(request, token):
    confirmation = get_object_or_404(PasswordResetConfirmation, token=token)
    print(confirmation.is_valid)
    if not confirmation.is_valid:
        return redirect("login")

    user = confirmation.user
    if request.method == "POST":
        form = SetPasswordForm(user=user, data=request.POST)
        if form.is_valid():
            confirmation.confirm()
            form.save()
            return redirect("home")
    else:
        form = SetPasswordForm(user=user)

    return render(request, "my_community/reset_password.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")


def terms_page(request):
    return render(request, "my_community/terms.html")


def privacy_form(request):
    return render(request, "my_community/privacy.html")
