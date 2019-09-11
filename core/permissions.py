from rest_framework import permissions

from core.models import UserProfileModel, TodoGroupModel, TodoModel


class UserProfilePermissions(permissions.BasePermission):
    """The Permission class used by UserProfileView."""

    safe_methods = {'GET', 'POST', 'HEAD', 'OPTIONS'}

    def has_permission(self, request, view):
        """Checks if request is safe, if not it checks if
        the user is authenticated and has a valid profile.
        """
        if request.method in self.safe_methods:
            return True
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """Checks if the user has permissions to update
        or delete a user profile"""
        if obj.account == request.user:
            return True
        return False


class TodoGroupPermissions(permissions.BasePermission):
    """The Permission class used by TodoGroupView."""

    def has_permission(self, request, view):
        """Checks if the user is authenticated and has a valid profile."""
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """Checks if the user has the permissions to
        update or delete a todo group
        """
        if type(obj) == UserProfileModel:
            if obj.account == request.user:
                return True
            return False
        if obj.user.account == request.user:
            return True
        return False


class TodoPermissions(permissions.BasePermission):
    """The Permission class used by TodoItemView."""

    def has_permission(self, request, view):
        """Checks if the user is authenticated and has a valid profile."""
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """Checks if the user has the permissions to see,
        update or delete a todo
        """
        if type(obj) == UserProfileModel:
            if obj.account == request.user:
                return True
            return False

        if type(obj) == TodoGroupModel:
            if obj.user.account == request.user:
                return True
            return False

        if obj.category.user.account == request.user:
            return True
        return False


class TodoAttachmentPermissions(permissions.BasePermission):
    """The Permission class used by TodoAttachmentView."""

    def has_permission(self, request, view):
        """Checks if the user is authenticated and has a valid profile."""
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """Checks if the user has the permissions to
        update or delete a todo
        """
        if type(obj) == TodoModel:
            if obj.category.user.account == request.user:
                return True
            return False

        if obj.todo_item.category.user.account == request.user:
            return True
        return False
