import factory

from my_community.models import Topic


class TopicTestData:
    def __init__(self, item_count: int):
        self.item_count = item_count

    @property
    def data_list(self):
        data = []
        for i in range(self.item_count):
            data.append(
                Topic(name=f"Topic {i}", slug=f"topic-{i}", description="test")
            )
        if len(data) == 1:
            return data[0]
        return data


class TopicTestUpdateData:
    @property
    def data(self):
        return Topic(name="new", description="new", slug="new")


class TopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Topic

    name = factory.Sequence(lambda n: f"Topic {n}")
    slug = factory.Sequence(lambda n: f"topic-{n}")
    description = "test"
