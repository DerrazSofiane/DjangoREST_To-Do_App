from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core.views import UserProfileView, user_login, user_logout, TodoGroupView, TodoView, TodoAttachmentView

app_name = 'core'

todo_group_router = DefaultRouter()
todo_group_router.register('', TodoGroupView, basename='todo_groups')

todo_attachment_router = DefaultRouter()
todo_attachment_router.register('', TodoAttachmentView, basename='todo_attachments')

urlpatterns = [
    path('users/login/', user_login, name='login'),
    path('users/logout/', user_logout, name='logout'),
    path('users/signup/', UserProfileView.as_view({'post': 'create'}), name='signup'),
    path('users/<username>/', UserProfileView.as_view({'get': 'retrieve',
                                                       'put': 'update',
                                                       'patch': 'partial_update',
                                                       'delete': 'destroy'}), name='user-details'),
    path('users/<username>/todo-items/', TodoView.as_view({'get': 'list'}), name='todo-list'),
    path('users/<username>/todo-groups/', include(todo_group_router.urls)),
    path('users/<username>/todo-groups/<int:group_sort>/todo-items/',
         TodoView.as_view({'post': 'create'}), name='todo-create'),
    path('users/<username>/todo-groups/<int:group_sort>/todo-items/<int:pk>',
         TodoView.as_view({'get': 'retrieve',
                           'put': 'update',
                           'patch': 'partial_update',
                           'delete': 'destroy'}), name='todo-detail'),
    path('users/<username>/todo-groups/<int:group_sort>/todo-items/<int:item_sort>/attachments/',
         include(todo_attachment_router.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
