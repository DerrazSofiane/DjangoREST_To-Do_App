import json

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from core.models import UserProfileModel, TodoGroupModel, TodoModel, TodoAttachmentModel


class TestUsers(TestCase):
    """Unit Test for user's views"""

    def test_login(self):
        """Test for users login view"""

        user = User.objects.create_user(username='username', first_name='first',
                                        last_name='last', password='password')
        url = reverse('core:login')

        # user has no profile not valid
        response = self.client.post(url, {'username': 'username',
                                          'password': 'password'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

        UserProfileModel.objects.create(account=user)

        # wrong login password
        response = self.client.post(url, {'username': 'username',
                                          'password': 'a wrong password'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # right login
        response = self.client.post(url, {'username': 'username',
                                          'password': 'password'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # user already logged in
        response = self.client.post(url, {'username': 'username',
                                          'password': 'password'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_logout(self):
        """Test for users logout view"""

        user = User.objects.create_user(username='username', password='password')

        # user is logged in
        url = reverse('core:logout')
        self.client.force_login(user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

        # user is NOT logged in
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)

    def test_signup(self):
        """Test for users signup view"""
        url = reverse('core:signup')

        # right sign up
        response = self.client.post(url, {'account': {
            'first_name': 'my first name',
            'last_name': 'my last name',
            'username': 'username',
            'password': 'super_secret'
        }}, content_type='application/json')

        self.assertEqual(response.status_code, 201)

        # already logged in
        response = self.client.post(url, {'account': {
            'username': 'username',
            'password': 'super_secret',
            'first_name': 'my first name',
            'last_name': 'my last name'
        }}, content_type='application/json')

        self.assertEqual(response.status_code, 401)

        # creating user with a taken username
        self.client.logout()
        response = self.client.post(url, {'account': {
            'username': 'username',  # taken
            'password': 'super_secret',
            'first_name': 'my first name',
            'last_name': 'my last name'
        }}, content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # creating user with a non valid password
        response = self.client.post(url, {'account': {
            'username': 'no_taken_username',
            'password': '123',
            'first_name': 'my first name',
            'last_name': 'my last name'
        }}, content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_get_user(self):
        """Test for users get view"""

        user = User.objects.create_user(username='username', password='password')
        UserProfileModel.objects.create(account=user)
        url = reverse('core:user-details', kwargs={'username': 'username'})

        # right
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # wrong user
        url = reverse('core:user-details', kwargs={'username': 'non existing username'})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_update_user(self):
        """Test for users update view"""

        user = User.objects.create_user(username='username', password='password')
        UserProfileModel.objects.create(account=user)
        url = reverse('core:user-details', kwargs={'username': 'username'})

        # not logged in as that user
        response = self.client.put(url, {'account': {
            'username': 'username',
            'password': 'super_secret',
            'first_name': 'my first name',
            'last_name': 'my last name'
        }}, content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # not logged in as that user
        user2 = User.objects.create_user(username='username2', password='password')
        UserProfileModel.objects.create(account=user2)
        self.client.force_login(user2)
        response = self.client.put(url, {'account': {
            'username': 'username',
            'password': 'super_secret',
            'first_name': 'my first name',
            'last_name': 'my last name'
        }}, content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # wrong or uncompleted data
        self.client.force_login(user)
        response = self.client.put(url, {'account': {'first_name': 'my first name'}},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # uncompleted data passes the patch request right
        response = self.client.patch(url, {'account': {'first_name': 'my first name'}},
                                     content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # wrong data with patch
        response = self.client.patch(url, {'account': {'username': 'username'}},  # duplicate
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # right
        response = self.client.put(url, {'account': {
            'username': 'the_new_username',
            'password': 'super_secret',
            'first_name': 'my first name',
            'last_name': 'my last name'
        }}, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # wrong username
        url = reverse('core:user-details', kwargs={'username': 'non existing username'})
        response = self.client.put(url, {'account': {
            'username': 'username',
            'password': 'super_secret',
            'first_name': 'my first name',
            'last_name': 'my last name'
        }}, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_delete_user(self):
        """Test for users delete view"""

        user = User.objects.create_user(username='username', password='password')
        UserProfileModel.objects.create(account=user)
        url = reverse('core:user-details', kwargs={'username': 'username'})

        # is not logged in as that user
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        # is not logged in as that user
        user2 = User.objects.create_user(username='username2', password='password')
        UserProfileModel.objects.create(account=user2)
        self.client.force_login(user2)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        # wrong username
        self.client.force_login(user)
        url = reverse('core:user-details', kwargs={'username': 'non existing username'})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

        # right
        url = reverse('core:user-details', kwargs={'username': 'username'})
        self.client.force_login(user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(User.objects.filter(username='username').exists(), False)


class TestTodoGroup(TestCase):
    """Unit Test for todo group views"""

    def test_create(self):
        """test for todo group create view"""

        user = User.objects.create_user(username='username', password='password')
        UserProfileModel.objects.create(account=user)
        url = reverse('core:todo_groups-list', kwargs={'username': 'username'})

        # not logged
        response = self.client.post(url, {'title': 'title'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # not logged in as that user
        user2 = User.objects.create_user(username='username2', password='password')
        UserProfileModel.objects.create(account=user2)
        self.client.force_login(user2)
        response = self.client.post(url, {'title': 'title'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # right
        self.client.force_login(user)
        response = self.client.post(url, {'title': 'title'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.content)['sort'], 1)  # check for sort from signals

        # wrong data
        response = self.client.post(url, {},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # wrong username
        url = reverse('core:todo_groups-list', kwargs={'username': 'non existing username'})
        response = self.client.post(url, {'title': 'title'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_update(self):
        """test for todo group update view"""

        user = User.objects.create_user(username='username', password='password')
        user_profile = UserProfileModel.objects.create(account=user)
        TodoGroupModel.objects.create(user=user_profile, title='title')
        url = reverse('core:todo_groups-detail', kwargs={'username': 'username', 'pk': 1})

        # not logged
        response = self.client.put(url, {'title': 'title'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # not logged in as that user
        user2 = User.objects.create_user(username='username2', password='password')
        UserProfileModel.objects.create(account=user2)
        self.client.force_login(user2)
        response = self.client.put(url, {'title': 'title'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # right
        self.client.force_login(user)
        response = self.client.put(url, {'title': 'title'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # wrong data for put
        response = self.client.put(url, {},  # missing attrs
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # wrong username
        url = reverse('core:todo_groups-detail',
                      kwargs={'username': 'non existing username', 'pk': 1})
        response = self.client.put(url, {'title': 'title'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

        # wrong group pk
        url = reverse('core:todo_groups-detail', kwargs={'username': 'username', 'pk': 123})
        response = self.client.put(url, {'title': 'title'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_delete(self):
        """test for todo group delete view"""

        user = User.objects.create_user(username='username', password='password')
        user_profile = UserProfileModel.objects.create(account=user)
        TodoGroupModel.objects.create(user=user_profile, title='title')
        group2 = TodoGroupModel.objects.create(user=user_profile, title='title')

        self.assertEqual(group2.sort, 2)
        url = reverse('core:todo_groups-detail', kwargs={'username': 'username', 'pk': 1})

        # not logged
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        # not logged in as that user
        user2 = User.objects.create_user(username='username2', password='password')
        UserProfileModel.objects.create(account=user2)
        self.client.force_login(user2)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        # right
        self.client.force_login(user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        group2.refresh_from_db()
        self.assertEqual(group2.sort, 1)  # resorted from signals

        # wrong username
        url = reverse('core:todo_groups-detail',
                      kwargs={'username': 'non existing username', 'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

        # wrong group pk
        url = reverse('core:todo_groups-detail', kwargs={'username': 'username', 'pk': 123})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)


class TestTodoItem(TestCase):
    """Unit Test for todo item views"""

    def setUp(self):
        """setup for unittest"""
        self.account = User.objects.create_user(username='username', password='password')
        user_profile = UserProfileModel.objects.create(account=self.account)
        self.group = TodoGroupModel.objects.create(user=user_profile, title='title')

    def test_list(self):
        """Test for todo items list view"""

        TodoModel.objects.create(category=self.group, title='title')
        url = reverse('core:todo-list', kwargs={'username': 'username'})

        # not logged
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # looged in as a user that has no valid user profile
        user2 = User.objects.create_user(username='username2', password='password')
        self.client.force_login(user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # not logged in as that user
        user3 = User.objects.create_user(username='username3', password='password')
        UserProfileModel.objects.create(account=user3)
        self.client.force_login(user3)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # right
        self.client.force_login(self.account)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # wrong username
        url = reverse('core:todo-list', kwargs={'username': 'non existing username'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get(self):
        """Test for todo item get view"""

        TodoModel.objects.create(category=self.group, title='title')
        url = reverse('core:todo-detail', kwargs={'username': 'username', 'group_sort': 1, 'pk': 1})

        # not logged
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # not logged in as that user
        user2 = User.objects.create_user(username='username2', password='password')
        UserProfileModel.objects.create(account=user2)
        self.client.force_login(user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # right
        self.client.force_login(self.account)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # wrong username
        url = reverse('core:todo-detail', kwargs={'username': 'wrong', 'group_sort': 1, 'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # wrong todo pk
        url = reverse('core:todo-detail',
                      kwargs={'username': 'username', 'group_sort': 1, 'pk': 123})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # wrong group sort
        url = reverse('core:todo-detail',
                      kwargs={'username': 'username', 'group_sort': 1234, 'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_create(self):
        """Test for todo item create view"""

        url = reverse('core:todo-create', kwargs={'username': 'username', 'group_sort': 1})

        # not logged
        response = self.client.post(url, {'title': 'title'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # not logged in as that user
        user2 = User.objects.create_user(username='username2', password='password')
        UserProfileModel.objects.create(account=user2)
        self.client.force_login(user2)
        response = self.client.post(url, {'title': 'title'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # right
        self.client.force_login(self.account)
        response = self.client.post(url, {'title': 'title'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.content)['sort'], 1)  # check for sort from signals

        # wrong data
        response = self.client.post(url, {},  # missing attrs
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # wrong username
        url = reverse('core:todo-create',
                      kwargs={'username': 'non existing username', 'group_sort': 1})
        response = self.client.post(url, {'title': 'title'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 404)

        # wrong group sort
        url = reverse('core:todo-create', kwargs={'username': 'username', 'group_sort': 123})
        response = self.client.post(url, {'title': 'title'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_update(self):
        """Test for todo item update view"""

        TodoModel.objects.create(category=self.group, title='title')
        url = reverse('core:todo-detail', kwargs={'username': 'username', 'group_sort': 1,
                                                  'pk': 1})

        # not logged
        response = self.client.put(url, {'title': 'title'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # not logged in as that user
        user2 = User.objects.create_user(username='username2', password='password')
        UserProfileModel.objects.create(account=user2)
        self.client.force_login(user2)
        response = self.client.put(url, {'title': 'title'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # right
        self.client.force_login(self.account)
        response = self.client.put(url, {'title': 'title'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # wrong data for put
        response = self.client.put(url, {},  # missing attrs
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # wrong data for put (bigger than the count of all todos)
        response = self.client.patch(url, {'title': 'title', 'sort': 123},
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # right for patch
        response = self.client.patch(url, {'title': 'title'},
                                     content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # wrong data with patch (bigger than the count of all todos)
        response = self.client.patch(url, {'title': 'title', 'sort': 123},
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # wrong username
        url = reverse('core:todo-detail', kwargs={'username': 'non existing username', 'group_sort': 1,
                                                  'pk': 1})
        response = self.client.put(url, {'title': 'title'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

        # wrong todo item pk
        url = reverse('core:todo-detail', kwargs={'username': 'username', 'group_sort': 1,
                                                  'pk': 123})
        response = self.client.put(url, {'title': 'title'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

        # wrong todo group sort
        url = reverse('core:todo-detail', kwargs={'username': 'username', 'group_sort': 123,
                                                  'pk': 1})
        response = self.client.put(url, {'title': 'title'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_delete(self):
        """Test for todo item delete view"""

        TodoModel.objects.create(category=self.group, title='title')
        todo2 = TodoModel.objects.create(category=self.group, title='title')
        self.assertEqual(todo2.sort, 2)
        url = reverse('core:todo-detail', kwargs={'username': 'username', 'group_sort': 1,
                                                  'pk': 1})

        # not logged
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        # not logged in as that user
        user2 = User.objects.create_user(username='username2', password='password')
        UserProfileModel.objects.create(account=user2)
        self.client.force_login(user2)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        # right
        self.client.force_login(self.account)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        todo2.refresh_from_db()
        self.assertEqual(todo2.sort, 1)  # resorted from signals

        # wrong username
        url = reverse('core:todo-detail', kwargs={'username': 'wrong', 'group_sort': 1,
                                                  'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

        # wrong todo item pk
        url = reverse('core:todo-detail', kwargs={'username': 'username', 'group_sort': 1,
                                                  'pk': 123})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

        # wrong todo group sort
        url = reverse('core:todo-detail', kwargs={'username': 'username', 'group_sort': 1234,
                                                  'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)


class TestTodoAttachment(TestCase):
    """Unit Test for todo attachment views"""

    def setUp(self):
        """set up for unittest"""

        self.account = User.objects.create_user(username='username', password='password')
        user = UserProfileModel.objects.create(account=self.account)
        group = TodoGroupModel.objects.create(user=user, title='title')
        self.todo = TodoModel.objects.create(category=group, title='title')

    def img_upload(self):
        """returns a file object"""
        file_path = settings.BASE_DIR + '/core/tests/sample.jpg'
        return SimpleUploadedFile(name='test_img.jpg',
                                  content=open(file_path, 'rb').read(),
                                  content_type='image/jpg')

    def delete_test_files(self):
        """deletes generated test files"""

        for attachment in self.todo.attachments.all():
            attachment.delete()

    def test_create(self):
        """test for todo attachment create view"""

        url = reverse('core:todo_attachments-list', kwargs={'username': 'username',
                                                            'group_sort': 1, 'item_sort': 1})

        # not logged
        response = self.client.post(url, {'file': self.img_upload()})
        self.assertEqual(response.status_code, 403)

        # not logged in as that user
        user2 = User.objects.create_user(username='username2', password='password')
        UserProfileModel.objects.create(account=user2)
        self.client.force_login(user2)
        response = self.client.post(url, {'file': self.img_upload()})
        self.assertEqual(response.status_code, 403)

        # right
        self.client.force_login(self.account)
        response = self.client.post(url, {'file': self.img_upload()})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.content)['sort'], 1)  # check for sort from signals

        # wrong data
        response = self.client.post(url, {})  # missing attrs
        self.assertEqual(response.status_code, 400)

        # wrong username
        url = reverse('core:todo_attachments-list', kwargs={'username': 'wrong',
                                                            'group_sort': 1, 'item_sort': 1})
        response = self.client.post(url, {'file': self.img_upload()})
        self.assertEqual(response.status_code, 404)

        self.delete_test_files()

    def test_delete(self):
        """test for todo attachment delete view"""

        TodoAttachmentModel.objects.create(todo_item=self.todo, file=self.img_upload())
        attachment2 = TodoAttachmentModel.objects.create(
            todo_item=self.todo, file=self.img_upload())

        self.assertEqual(attachment2.sort, 2)
        url = reverse('core:todo_attachments-detail', kwargs={'username': 'username',
                                                              'group_sort': 1,
                                                              'item_sort': 1, 'pk': 1})

        # not logged
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        # not logged in as that user
        user2 = User.objects.create_user(username='username2', password='password')
        UserProfileModel.objects.create(account=user2)
        self.client.force_login(user2)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        # right
        self.client.force_login(self.account)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        attachment2.refresh_from_db()
        self.assertEqual(attachment2.sort, 1)  # resorted from signals

        # wrong username
        url = reverse('core:todo_attachments-detail', kwargs={'username': 'wrong',
                                                              'group_sort': 1,
                                                              'item_sort': 1, 'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

        # wrong attachment pk
        url = reverse('core:todo_attachments-detail', kwargs={'username': 'username',
                                                              'group_sort': 1,
                                                              'item_sort': 1, 'pk': 123})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

        self.delete_test_files()
