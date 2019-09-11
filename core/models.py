import os
import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


def users_upload(instance, filename):
    """Gives a unique path to the saved user photo in models.
    Arguments:
        instance: the photo itself, it is not used in this
                  function but it's required by django.
        filename: the name of the photo sent by user, it's
                  used here to get the format of the photo.
    Returns:
        The unique path that the photo will be stored in the DB.
    """

    return 'users/{0}.{1}'.format(uuid.uuid4().hex, os.path.splitext(filename))


def attachment_upload(instance, filename):
    """Gives a unique path to the saved attachment file in models.
    Arguments:
        instance: the file itself, it is not used in this
                  function but it's required by django.
        filename: the name of the file sent by user, it's
                  used here to get the format of the file.
    Returns:
        The unique path that the file will be stored in the DB.
    """

    return 'attachments/{0}.{1}'.format(uuid.uuid4().hex, os.path.splitext(filename))


class UserProfileModel(models.Model):
    """The Model of the User Profile."""

    account = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_photo = models.ImageField(upload_to=users_upload, null=True)

    def __str__(self):
        return self.account.username


class TodoGroupModel(models.Model):
    """The Model of the Todo Categories."""

    sort = models.PositiveIntegerField(null=True)
    user = models.ForeignKey(UserProfileModel, on_delete=models.CASCADE, related_name='todo_groups')
    title = models.CharField(max_length=255)

    class Meta:
        ordering = ['sort']
        unique_together = ("user", "sort")

    def __str__(self):
        return self.title


class TodoModel(models.Model):
    """The Model of the Todo item."""

    todo_statuses = (
        ('C', 'Checked'),
        ('U', 'Unchecked')
    )

    sort = models.PositiveIntegerField(null=True)
    category = models.ForeignKey(TodoGroupModel, on_delete=models.CASCADE, related_name='todos')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=1, choices=todo_statuses, default='U')  # whether it's done or not

    class Meta:
        unique_together = ("category", "sort")
        ordering = ['sort']

    def __str__(self):
        return self.title


def filesize(value):
    """Model Validator for file size limit"""
    limit = 2 * 1000 * 1000
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 2 MB.')


class TodoAttachmentModel(models.Model):
    """an alias to filefield to enable
    having multiple file attachments in a todo items"""

    sort = models.PositiveIntegerField(null=True)
    todo_item = models.ForeignKey(TodoModel, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=attachment_upload, validators=[filesize])

    class Meta:
        unique_together = ("todo_item", "sort")
        ordering = ['sort']
