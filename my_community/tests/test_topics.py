import pytest
from django.shortcuts import get_object_or_404

from my_community.models import Topic
from my_community.tests.factories import (
    TopicFactory,
    TopicTestData,
    TopicTestUpdateData,
)

COUNTER = 10


class TestTopics:
    @pytest.mark.django_db
    def test_topic_create(self):
        topic = TopicFactory()
        test_data = TopicTestData(1).data_list
        topic = get_object_or_404(Topic, slug=topic.slug)
        assert test_data.name == topic.name
        assert test_data.slug == topic.slug
        assert test_data.description == topic.description

    @pytest.mark.django_db
    def test_topic_create_many(self):
        topic_test_data = TopicTestData(COUNTER).data_list
        for i in range(COUNTER):
            topic = TopicFactory()
            topic = get_object_or_404(Topic, slug=topic.slug)
            assert topic_test_data[i].name == topic.name
            assert topic_test_data[i].slug == topic.slug
            assert topic_test_data[i].description == topic.description

    @pytest.mark.django_db
    def test_topic_update(self):
        topic = TopicFactory()
        test_data = TopicTestUpdateData().data
        topic = get_object_or_404(Topic, slug=topic.slug)
        topic.name = test_data.name
        topic.description = test_data.description
        topic.slug = test_data.slug
        topic.save()
        topic = get_object_or_404(Topic, slug=topic.slug)
        assert test_data.name == topic.name
        assert test_data.slug == topic.slug
        assert test_data.description == topic.description
