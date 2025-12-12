import random

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


class UserTestData:
    def __init__(self, item_count: int):
        self.item_count = item_count

    @staticmethod
    def valid_emails():
        valid_emails = [
            "user@gmail.com",
            "test.user@example.com",
            "first_last@domain.co",
            "user+tag@gmail.com",
            "user123@yahoo.com",
        ]
        return random.choice(valid_emails)

    @staticmethod
    def invalid_emails():
        invalid_emails = [
            "plainaddress",
            "@no-local-part.com",
            "user@.com",
            "user@com",
            "user@domain..com",
            "user@@domain.com",
        ]
        return random.choice(invalid_emails)

    @staticmethod
    def valid_phones():
        valid_phones = [
            "+79991234567",
            "+7 999 123 45 67",
            "+1-415-555-2671",
            "+44 7911 123456",
            "+8613800138000",
            "+33 6 12 34 56 78",
            "+7(999)1234567",
            "+7-999-123-45-67",
        ]
        return random.choice(valid_phones)

    @staticmethod
    def invalid_phones():
        invalid_phones = [
            "89991234567",
            "12345",
            "06 12 34 56 78",
            "phone123456",
        ]
        return random.choice(invalid_phones)

    @staticmethod
    def valid_passwords():
        valid_passwords = [
            "Q_P_Password1vr",
            "3456278jfdeabcDEFghiJ",
            "P_P09user_12345",
            "A_096511Test@Pass10",
        ]
        return random.choice(valid_passwords)

    @staticmethod
    def invalid_passwords():
        invalid_passwords = [
            "1234567890",
            # "!!!!@@@@####",
            "abc",
            "          ",
            "",
        ]
        return random.choice(invalid_passwords)

    @staticmethod
    def valid_usernames():
        valid_usernames = [
            "user123",
            "John_Doe",
            "alice@home",
            "name-01",
            "user/name",
        ]
        return random.choice(valid_usernames)

    @staticmethod
    def invalid_usernames():
        invalid_usernames = [
            "123456",
            "@@@---",
            "!!##$$",
            "",
        ]
        return random.choice(invalid_usernames)
