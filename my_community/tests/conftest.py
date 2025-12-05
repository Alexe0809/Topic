import pytest

from my_community.tests.factories import TopicFactory


@pytest.fixture(autouse=True)
def reset_all_sequences():
    TopicFactory.reset_sequence()
    yield
