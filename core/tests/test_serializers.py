import os

from django.contrib.auth.models import User
from django.core.files import File
from django.test import TestCase

from core.models import TodoGroupModel, UserProfileModel, TodoModel
from core.serializers import UserSerializer, TodoGroupSerializer, TodoItemSerializer, TodoAttachmentSerializer


class TestUsers(TestCase):
    """UnitTest for users serializers"""

    def test_name_fields_required(self):
        """test for name fields requirements"""

        serializer = UserSerializer(data={'username': 'username', 'password': 'super_secret'})
        self.assertFalse(serializer.is_valid())

        serializer = UserSerializer(data={'username': 'username', 'first_name': 'first',
                                          'last_name': 'last', 'password': 'super_secret'})
        self.assertTrue(serializer.is_valid())

    def test_username_unique(self):
        """test for username uniqueness"""

        User.objects.create(username='username', password='super_secret')
        serializer = UserSerializer(data={'username': 'username', 'first_name': 'first',
                                          'last_name': 'last', 'password': 'super_secret'})
        self.assertFalse(serializer.is_valid())

    def test_password_validation(self):
        """test for password validation"""

        # true
        serializer = UserSerializer(data={'username': 'username', 'first_name': 'first',
                                          'last_name': 'last', 'password': 'super_secret'})
        self.assertTrue(serializer.is_valid())

        # less than 8 chars
        serializer = UserSerializer(data={'username': 'username', 'first_name': 'first',
                                          'last_name': 'last', 'password': 'hi'})
        self.assertFalse(serializer.is_valid())

        # user attr similar
        serializer = UserSerializer(data={'username': 'username', 'first_name': 'first',
                                          'last_name': 'last', 'password': 'username'})
        self.assertFalse(serializer.is_valid())

        # common password
        serializer = UserSerializer(data={'username': 'username', 'first_name': 'first',
                                          'last_name': 'last', 'password': 'password'})
        self.assertFalse(serializer.is_valid())

        # numbers only
        serializer = UserSerializer(data={'username': 'username', 'first_name': 'first',
                                          'last_name': 'last', 'password': '123456789'})
        self.assertFalse(serializer.is_valid())


class TestTodoGroup(TestCase):
    """Unittest for todo group serializer"""

    def setUp(self):
        """setup for unittest"""
        account = User.objects.create(username='username', password='super_secret')
        self.user = UserProfileModel.objects.create(account=account)

    def test_validate_sort(self):
        """test for sort field validation"""

        # right
        serializer = TodoGroupSerializer(data={'title': 'title'})
        self.assertTrue(serializer.is_valid())

        # wrong cuz sort can't be passed on create
        serializer = TodoGroupSerializer(data={'title': 'title', 'sort': 1})
        self.assertFalse(serializer.is_valid())

        # right cuz sort can be passed on updating
        group = TodoGroupModel.objects.create(title='title', user=self.user)

        serializer = TodoGroupSerializer(group, data={'title': 'title', 'sort': 1})
        self.assertTrue(serializer.is_valid())

        # wrong cuz sort is bigger than the count of all groups
        serializer = TodoGroupSerializer(group, data={'title': 'title', 'sort': 5})
        self.assertFalse(serializer.is_valid())

        another_group = TodoGroupModel.objects.create(title='title', user=self.user)

        self.assertEqual(another_group.sort, 2)

        # right and the two groups will be replaced in positions
        serializer = TodoGroupSerializer(group, data={'title': 'title', 'sort': 2})
        self.assertTrue(serializer.is_valid())
        serializer.save()

        group.refresh_from_db()
        another_group.refresh_from_db()
        self.assertEqual(group.sort, 2)
        self.assertEqual(another_group.sort, 1)

        # reverse again
        serializer = TodoGroupSerializer(group, data={'title': 'title', 'sort': 1})
        self.assertTrue(serializer.is_valid())
        serializer.save()

        group.refresh_from_db()
        another_group.refresh_from_db()
        self.assertEqual(group.sort, 1)
        self.assertEqual(another_group.sort, 2)


class TestTodo(TestCase):
    """Unittest for todo items serializer"""

    def setUp(self):
        """setup for unittest"""
        account = User.objects.create(username='username', password='super_secret')
        user = UserProfileModel.objects.create(account=account)
        self.group = TodoGroupModel.objects.create(user=user, title='title')

    def test_validate_sort(self):
        """test for sort field validation"""

        # right
        serializer = TodoItemSerializer(data={'title': 'title'})
        self.assertTrue(serializer.is_valid())

        # wrong cuz sort can't be passed on create
        serializer = TodoItemSerializer(data={'title': 'title', 'sort': 1})
        self.assertFalse(serializer.is_valid())

        # right cuz sort can be passed on updating
        todo = TodoModel.objects.create(title='title', category=self.group)

        serializer = TodoItemSerializer(todo, data={'title': 'title', 'sort': 1})
        self.assertTrue(serializer.is_valid())

        # wrong cuz sort is bigger than the count of all todos
        serializer = TodoItemSerializer(todo, data={'title': 'title', 'sort': 5})
        self.assertFalse(serializer.is_valid())

        another_todo = TodoModel.objects.create(title='title', category=self.group)

        self.assertEqual(another_todo.sort, 2)

        # right and the two todos will be replaced in positions
        serializer = TodoItemSerializer(todo, data={'title': 'title', 'sort': 2})
        self.assertTrue(serializer.is_valid())
        serializer.save()

        todo.refresh_from_db()
        another_todo.refresh_from_db()
        self.assertEqual(todo.sort, 2)
        self.assertEqual(another_todo.sort, 1)

        # reverse again
        serializer = TodoItemSerializer(todo, data={'title': 'title', 'sort': 1})
        self.assertTrue(serializer.is_valid())
        serializer.save()

        todo.refresh_from_db()
        another_todo.refresh_from_db()
        self.assertEqual(todo.sort, 1)
        self.assertEqual(another_todo.sort, 2)

    def test_status_type(self):
        """test for status type validation"""

        # right
        serializer = TodoItemSerializer(data={'title': 'title', 'status': 'C'})
        self.assertTrue(serializer.is_valid())

        # right
        serializer = TodoItemSerializer(data={'title': 'title', 'status': 'U'})
        self.assertTrue(serializer.is_valid())

        # wrong status choice
        serializer = TodoItemSerializer(data={'title': 'title', 'status': 'wrong'})
        self.assertFalse(serializer.is_valid())


class TestAttachment(TestCase):
    """Unittest for todo attachment"""

    def setUp(self):
        """setup for unittest"""

        # makes dummy file to test
        with open('media/sample.flv', 'w+') as f:
            # 1 mb file
            f.write('a' * 10 ** 6)
            self.file = File(f)

        with open('media/sample2.flv', 'w+') as f:
            # 7 mb file
            f.write('a' * 7 * 10 ** 6)
            self.file2 = File(f)

    def test_file_size(self):
        """test for file size validator"""

        # right
        serializer = TodoAttachmentSerializer(data={'file': self.file})
        self.assertTrue(serializer.is_valid())

        # wrong file size bigger than 2 mb
        serializer = TodoAttachmentSerializer(data={'file': self.file2})
        self.assertFalse(serializer.is_valid())

        # delete file from os after test
        os.remove(self.file.name)
        os.remove(self.file2.name)
