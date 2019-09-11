import os

from django.contrib.auth.models import User
from django.test import TestCase

from core.models import TodoGroupModel, TodoModel, TodoAttachmentModel, UserProfileModel, users_upload, \
    attachment_upload


class TestUsers(TestCase):
    """UnitTest for users models"""

    def test_photo_name_unique(self):
        """test for image and file upload unique id generator"""

        image_1_id = users_upload(None, 'image1')
        image_2_id = users_upload(None, 'image2')
        self.assertNotEquals(image_1_id, image_2_id)

        file_1_id = attachment_upload(None, 'file1')
        file_2_id = attachment_upload(None, 'file2')
        self.assertNotEquals(file_1_id, file_2_id)

    def test_user_str(self):
        """test for user __str__ unction"""

        user = User.objects.create_user(username='username', password='password')
        user_profile = UserProfileModel.objects.create(account=user)
        self.assertEqual(user_profile.__str__(), user.username)

    def test_user_account_delete(self):
        """test for account delete after profile deletion from signals"""

        account = User.objects.create_user(username='username', password='password')
        user_profile = UserProfileModel.objects.create(account=account)
        user_profile.delete()
        self.assertEqual(User.objects.filter(username='username').exists(), False)


class TestTodoGroup(TestCase):
    """UnitTest for todo group models"""

    def test_todo_group_sort_unique(self):
        """test for todo group sort uniqueness"""

        user = User.objects.create_user(username='username', password='password')
        user_profile = UserProfileModel.objects.create(account=user)

        group1 = TodoGroupModel.objects.create(user=user_profile, title='group1')
        self.assertEqual(group1.sort, 1)

        group2 = TodoGroupModel.objects.create(user=user_profile, title='group2')
        self.assertEqual(group2.sort, 2)
        self.assertNotEquals(group1.sort, group2.sort)

        group1.delete()
        group2.refresh_from_db()
        self.assertEqual(group2.sort, 1)  # resorted from signals

    def test_todo_group_str(self):
        """test for todo group __str__ function"""

        user = User.objects.create_user(username='username', password='password')
        user_profile = UserProfileModel.objects.create(account=user)
        group = TodoGroupModel.objects.create(user=user_profile, title='group1')
        self.assertEqual(group.__str__(), group.title)


class TestTodo(TestCase):
    """UnitTest for todo models"""

    def test_todo_sort_unique(self):
        """test for todo item sort uniqueness"""

        user = User.objects.create_user(username='username', password='password')
        user_profile = UserProfileModel.objects.create(account=user)

        group1 = TodoGroupModel.objects.create(user=user_profile, title='group1')

        todo1 = TodoModel.objects.create(category=group1, title='todo1')
        self.assertEqual(todo1.sort, 1)

        todo2 = TodoModel.objects.create(category=group1, title='todo2')
        self.assertEqual(todo2.sort, 2)
        self.assertNotEquals(todo1.sort, todo2.sort)

        todo1.delete()
        todo2.refresh_from_db()
        self.assertEqual(todo2.sort, 1)  # resorted from signals

    def test_todo_str(self):
        """test for todo item __str__ unction"""

        user = User.objects.create_user(username='username', password='password')
        user_profile = UserProfileModel.objects.create(account=user)

        group1 = TodoGroupModel.objects.create(user=user_profile, title='group1')

        todo1 = TodoModel.objects.create(category=group1, title='todo1')

        self.assertEqual(todo1.__str__(), todo1.title)


class TestTodoAttachment(TestCase):
    """UnitTest for todo attachments models"""

    def setUp(self):
        """Setup for unittest"""
        with open("media/sample.flv", "w+"):
            pass

    def test_todo_attachment_sort_unique(self):
        """test for todo attachment sort uniqueness"""

        user = User.objects.create_user(username='username', password='password')
        user_profile = UserProfileModel.objects.create(account=user)

        group = TodoGroupModel.objects.create(user=user_profile, title='group1')
        todo = TodoModel.objects.create(category=group, title='todo1')

        attachment1 = TodoAttachmentModel.objects.create(todo_item=todo, file='sample.flv')
        self.assertEqual(attachment1.sort, 1)

        attachment2 = TodoAttachmentModel.objects.create(todo_item=todo, file='sample.flv')
        self.assertEqual(attachment2.sort, 2)
        self.assertNotEquals(attachment1.sort, attachment2.sort)

        attachment1.delete()
        attachment2.refresh_from_db()
        self.assertEqual(attachment2.sort, 1)  # resorted from signals

    def test_file_delete(self):
        """test for todo attachment delete file from os function"""

        user = User.objects.create_user(username='username', password='password')
        user_profile = UserProfileModel.objects.create(account=user)

        group = TodoGroupModel.objects.create(user=user_profile, title='group1')
        todo = TodoModel.objects.create(category=group, title='todo1')

        attachment = TodoAttachmentModel.objects.create(todo_item=todo, file='sample.flv')
        self.assertTrue(os.path.isfile(attachment.file.path))

        attachment.delete()

        self.assertFalse(os.path.isfile(attachment.file.path))
