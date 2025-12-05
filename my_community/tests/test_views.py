import pytest
from django.test import RequestFactory

from my_community.tests.factories import TopicFactory
from my_community.views import IndexView


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
