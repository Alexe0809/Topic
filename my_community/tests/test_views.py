import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from my_community.tests.factories import TopicFactory
from my_community.views import IndexView, TopicDetailView


class TestIndexView:

    def setup_method(self):
        self.factory = RequestFactory()
        self.view = IndexView()

    @pytest.mark.django_db
    def test_view_class_attributes(self):
        assert IndexView.template_name == "my_community/index.html"

    @pytest.mark.django_db
    def test_get_context_data_empty(self):
        request = self.factory.get("/")
        self.view.request = request

        context = self.view.get_context_data()

        assert "topics" in context
        assert list(context["topics"]) == []  # Пустой список

    @pytest.mark.django_db
    def test_get_context_data_with_topics(self):
        topics = TopicFactory.create_batch(3)

        request = self.factory.get("/")
        self.view.request = request

        context = self.view.get_context_data()

        assert "topics" in context
        assert list(context["topics"]) == topics

    @pytest.mark.django_db
    def test_get_context_data_ordering(self):
        topic3 = TopicFactory(name="Topic C")
        topic1 = TopicFactory(name="Topic A")
        topic2 = TopicFactory(name="Topic B")

        request = self.factory.get("/")
        self.view.request = request

        context = self.view.get_context_data()

        context_topics = list(context["topics"])

        assert len(context_topics) == 3
        assert topic1 in context_topics
        assert topic2 in context_topics
        assert topic3 in context_topics

    class TestTopicDetailView:

        def setup_method(self):
            self.factory = RequestFactory()
            self.view_class = TopicDetailView

        @pytest.mark.django_db
        def test_view_class_attributes(self):
            assert TopicDetailView.model.__name__ == "Topic"
            assert (
                TopicDetailView.template_name
                == "my_community/topic_detail.html"
            )
            assert TopicDetailView.context_object_name == "topic"

        @pytest.mark.django_db
        def test_get_object_with_slug(self):
            topic = TopicFactory(slug="test-topic")

            request = self.factory.get(f"/topic/{topic.slug}/")
            view = self.view_class()
            view.request = request
            view.kwargs = {"slug": "test-topic"}

            obj = view.get_object()

            assert obj == topic
            assert obj.slug == "test-topic"

        @pytest.mark.django_db
        def test_get_context_data(self):
            topic = TopicFactory(slug="context-topic")

            request = self.factory.get(f"/topic/{topic.slug}/")
            view = self.view_class()
            view.request = request
            view.kwargs = {"slug": "context-topic"}
            view.object = topic

            request.user = AnonymousUser()

            context = view.get_context_data()

            assert "topic" in context
            assert context["topic"] == topic
            assert context["topic"].slug == "context-topic"

        @pytest.mark.django_db
        def test_view_returns_correct_template(self):
            view = self.view_class()
            assert view.template_name == "my_community/topic_detail.html"
