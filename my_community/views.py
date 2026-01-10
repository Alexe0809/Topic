from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, TemplateView, UpdateView

from my_community.forms import (
    ResetPasswordForm,
    TopicForm,
    UserLogin,
    UserRegistration,
)
from my_community.models import (
    BaseReaction,
    Category,
    EmailConfirmation,
    PasswordResetConfirmation,
    Topic,
    TopicReaction,
    User,
)
from my_community.notifications.tasks import send_email


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
        topic.views += 1
        topic.save()
        context["topic"] = topic
        context["categories"] = topic.categories.all()
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


class UserProfile(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "my_community/user_profile.html"
    success_url = reverse_lazy("user_profile")
    fields = [
        "email",
        "phone",
        "username",
        "first_name",
        "last_name",
        "image",
        "description",
    ]
    login_url = "/login/"  # путь к твоему логину
    redirect_field_name = "next"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        liked_topics = Topic.objects.filter(
            reaction__user=self.request.user,
            reaction__reaction_type=BaseReaction.ReactionType.LIKE,
        )
        paginator = Paginator(liked_topics, 10)
        page_number = self.request.GET.get("page")
        context["created_topics"] = Topic.objects.filter(
            author=self.request.user
        )
        context["liked_topics_page"] = paginator.get_page(page_number)
        context["password_form"] = PasswordChangeForm(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if (
            "new_password1" in request.POST
        ):  # new_password1 это поле формы PasswordChangeForm,
            # если оно присутствует в POST запросе, значит запрос на смену пароля
            form = PasswordChangeForm(user=request.user, data=request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # чтобы не разлогинило
                messages.success(request, "Пароль успешно изменён!")
                return redirect("user_profile")
            else:
                context = self.get_context_data()
                context["password_form"] = form
                return self.render_to_response(context)
        return super().post(request, *args, **kwargs)


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
            send_email.delay(email_message_data, "confirmation")
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


def reset_password_form_view(request):
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            user = get_object_or_404(User, email=email)
            reset_password_obj = PasswordResetConfirmation.create_for_user(user)
            email_message_data = {
                "email": user.email,
                "url": reset_password_obj.get_confirmation_url(),
                "username": user.username,
            }
            send_email.delay(email_message_data, "reset_password")
            return redirect("login")
    else:
        form = ResetPasswordForm()
    return render(
        request, "my_community/reset_password_form.html", {"form": form}
    )


@login_required
def topic_create(request):
    if request.method == "POST":
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user

            topic.save()

            selected_categories = form.cleaned_data.get("categories")
            if selected_categories:
                topic.categories.add(*selected_categories)

            new_category_name = form.cleaned_data.get("new_category")
            if new_category_name and new_category_name.strip():
                new_category_name = new_category_name.strip()

                existing_category = Category.objects.filter(
                    name__iexact=new_category_name
                ).first()

                if existing_category:
                    topic.categories.add(existing_category)
                else:
                    category, created = Category.objects.get_or_create(
                        name=new_category_name,
                        defaults={
                            "description": f'Категория "{new_category_name}"'
                        },
                    )
                    topic.categories.add(category)

            messages.success(request, "Тема успешно создана!")
            return redirect(topic.get_absolute_url())
    else:
        form = TopicForm()

    categories = Category.objects.all().order_by("name")

    return render(
        request,
        "my_community/topic_create.html",
        {
            "form": form,
            "categories": categories,
        },
    )
