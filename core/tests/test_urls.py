from django.test import TestCase
from django.urls import reverse, resolve

from core.views import UserProfileView, user_login, user_logout, TodoGroupView, TodoView, TodoAttachmentView


class TestUsers(TestCase):
    """Test for the users urls"""

    def test_signup(self):
        """test for signup url"""
        url = reverse('core:signup')
        self.assertEqual(resolve(url).func.__name__,
                         UserProfileView.as_view({'post': 'create'}).__name__)

    def test_login(self):
        """test for login url"""
        url = reverse('core:login')
        self.assertEqual(resolve(url).func, user_login)

    def test_logout(self):
        """test for logout url"""
        url = reverse('core:logout')
        self.assertEqual(resolve(url).func, user_logout)

    def test_user_details(self):
        """test for user details url"""
        url = reverse('core:user-details', kwargs={'username': 'username'})
        self.assertEqual(resolve(url).func.__name__,
                         UserProfileView.as_view({'get': 'retrieve'}).__name__)


class TestTodoGroup(TestCase):
    """Test for the todo group urls"""

    def test_todo_group_create(self):
        """test for users todo group create url"""
        url = reverse('core:todo_groups-list', kwargs={'username': 'username'})
        self.assertEqual(resolve(url).func.__name__,
                         TodoGroupView.as_view({'post': 'create'}).__name__)

    def test_todo_group_detail(self):
        """test for users todo group details url"""
        url = reverse('core:todo_groups-detail', kwargs={'username': 'username', 'pk': 1})
        self.assertEqual(resolve(url).func.__name__,
                         TodoGroupView.as_view({'get': 'retrieve'}).__name__)


class TestTodo(TestCase):
    """Test for the todo urls"""

    def test_todo_create(self):
        """test for users todo create url"""
        url = reverse('core:todo-create', kwargs={'username': 'username', 'group_sort': 1})
        self.assertEqual(resolve(url).func.__name__,
                         TodoView.as_view({'post': 'create'}).__name__)

    def test_todo_list(self):
        """test for users todo list url"""
        url = reverse('core:todo-list', kwargs={'username': 'username'})
        self.assertEqual(resolve(url).func.__name__,
                         TodoView.as_view({'get': 'list'}).__name__)

    def test_todo_detail(self):
        """test for users todo details url"""
        url = reverse('core:todo-detail', kwargs={'username': 'username', 'group_sort': 1, 'pk': 1})
        self.assertEqual(resolve(url).func.__name__,
                         TodoView.as_view({'get': 'retrieve'}).__name__)


class TestTodoAttachments(TestCase):
    """Test for the users todo attachments urls"""

    def test_attachments_list(self):
        """test for users attachments list url"""
        url = reverse('core:todo_attachments-list', kwargs={'username': 'username', 'group_sort': 1,
                                                            'item_sort': 1})
        self.assertEqual(resolve(url).func.__name__,
                         TodoAttachmentView.as_view({'get': 'list'}).__name__)

    def test_attachment_detail(self):
        """test for users attachments details url"""
        url = reverse('core:todo_attachments-detail', kwargs={'username': 'username', 'group_sort': 1,
                                                              'item_sort': 1, 'pk': 1})
        self.assertEqual(resolve(url).func.__name__,
                         TodoAttachmentView.as_view({'get': 'retrieve'}).__name__)
