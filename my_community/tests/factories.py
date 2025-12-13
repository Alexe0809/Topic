import random

import factory

from my_community.models import Category, Topic, User

# class UserListTestData:
#     def __init__(self, item_count: int):
#         self.item_count = item_count
#
#     @property
#     def data_list(self):
#         result_data = []
#         data, exclude_fields = get_original_user_data()
#         for i in range(self.item_count):
#             for key, value in data.items():
#                 if key not in exclude_fields:
#                     data[key] = value + str(i)
#         if len(data) == 1:
#             return result_data[0]
#         return result_data
#
#
# class CategoryListTestData:
#     def __init__(self, item_count: int):
#         self.item_count = item_count
#
#     @property
#     def data_list(self):
#         result_data = []
#         data, exclude_fields = get_original_user_data()
#         for i in range(self.item_count):
#             for key, value in data.items():
#                 if key not in exclude_fields:
#                     data[key] = value + str(i)
#         if len(data) == 1:
#             return result_data[0]
#         return result_data
#
#
# class TopicTestData:
#     def __init__(self, item_count: int):
#         self.item_count = item_count
#
#
#
#
# class TopicTestUpdateData:
#     @property
#     def data(self):
#         return Topic(name="new", description="new", slug="new")
#
#
#
#
#
# class TopicFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = Topic
#
#     author = factory.Sequence(lambda n: UserFactory())
#     name = factory.Sequence(lambda n: f"Topic {n}")
#     slug = factory.Sequence(lambda n: f"topic-{n}")
#     categories = [factory.Sequence(lambda n: CategoryFactory())]
#     description = "test"
#
#
#
#     @property
#     def data_list(self):
#         data = []
#         for i in range(10):
#             author = factory.Sequence(lambda n: UserFactory())
#             name = factory.Sequence(lambda n: f"Topic {n}")
#             slug = factory.Sequence(lambda n: f"topic-{n}")
#             categories = [factory.Sequence(lambda n: CategoryFactory())]
#             description = "test"
#             data.append(
#                 Topic(name=name, slug=slug, description=description, author=author, )
#             )
#         if len(data) == 1:
#             return data[0]
#         return data


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"test_user-{n}")
    password = factory.Sequence(lambda n: f"test_pass1234{n}")
    phone = factory.Sequence(lambda n: "+375292556867")
    email = factory.Sequence(lambda n: f"t{n}est@gmail.com")


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"test-{n}")


class TopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Topic

    name = factory.Sequence(lambda n: f"Topic {n}")
    description = "test"
    author = factory.SubFactory(UserFactory)  # ForeignKey на User

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:  # передали категории при создании
            for cat in extracted:
                self.categories.add(cat)


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
