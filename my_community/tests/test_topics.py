import pytest
from django.shortcuts import get_object_or_404

from my_community.models import Topic
from my_community.tests.factories import (
    CategoryFactory,
    TopicFactory,
)

COUNTER = 10


class TestTopics:
    @pytest.mark.django_db
    def test_topic_create(self):
        # создаём категории и топик в базе
        categories = [CategoryFactory() for _ in range(2)]
        topic = TopicFactory(categories=categories)
        # получаем объект из базы
        topic_from_db = get_object_or_404(Topic, slug=topic.slug)
        # проверяем поля
        assert topic.name == topic_from_db.name
        assert topic.slug == topic_from_db.slug
        assert topic.description == topic_from_db.description
        # проверяем категории
        assert {c.name for c in categories} == {
            c.name for c in topic_from_db.categories.all()
        }

    @pytest.mark.django_db
    def test_topic_create_many(self):
        categories = [CategoryFactory() for _ in range(2)]
        topic = TopicFactory(categories=categories)
        topic_from_db = get_object_or_404(Topic, slug=topic.slug)
        assert topic.name == topic_from_db.name
        assert topic.slug == topic_from_db.slug
        assert topic.description == topic_from_db.description

    @pytest.mark.django_db
    def test_topic_update(self):
        categories = [CategoryFactory() for _ in range(2)]
        topic = TopicFactory(categories=categories)
        topic_from_db = get_object_or_404(Topic, pk=topic.pk)
        topic_from_db.name = "updated_user_name"
        topic_from_db.description = "updated_user_description"
        topic_from_db.save()
        topic_from_db = get_object_or_404(Topic, pk=topic.pk)
        assert "updated_user_name" == topic_from_db.name
        assert "updated_user_description" == topic_from_db.description
