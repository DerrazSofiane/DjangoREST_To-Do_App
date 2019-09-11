import os

from django.db.models import F
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from core.models import UserProfileModel, TodoGroupModel, TodoModel, TodoAttachmentModel


@receiver(post_delete, sender=UserProfileModel)
def delete_user_account(sender, **kwargs):
    """The receiver called after a user profile is deleted
    to delete its one_to_one relation"""

    kwargs['instance'].account.delete()


@receiver(pre_save, sender=TodoGroupModel)
def add_sort_to_todo_group(sender, **kwargs):
    """The receiver called before a todo group is saved
    to give it a unique sort"""

    group = kwargs['instance']
    if not group.pk:
        latest_sort = TodoGroupModel.objects.filter(user=group.user).count()
        group.sort = latest_sort + 1


@receiver(pre_save, sender=TodoModel)
def add_sort_to_todo_items(sender, **kwargs):
    """The receiver called before a todo item is saved
    to give it a unique sort"""

    todo = kwargs['instance']
    if not todo.pk:
        latest_sort = TodoModel.objects.filter(category=todo.category).count()
        todo.sort = latest_sort + 1


@receiver(pre_save, sender=TodoAttachmentModel)
def add_sort_to_todo_attachment(sender, **kwargs):
    """The receiver called before a todo attachment is saved
    to give it a unique sort"""

    attachment = kwargs['instance']
    if not attachment.pk:
        latest_sort = TodoAttachmentModel.objects.filter(todo_item=attachment.todo_item).count()
        attachment.sort = latest_sort + 1


@receiver(post_delete, sender=TodoGroupModel)
def resort_todo_groups(sender, **kwargs):
    """The receiver called after a todo group is deleted
    to resort them"""

    group = kwargs['instance']
    group.user.todo_groups.filter(sort__gt=group.sort).update(sort=F('sort') - 1)


@receiver(post_delete, sender=TodoModel)
def resort_todo_items(sender, **kwargs):
    """The receiver called after a Todo item is deleted
    to resort them"""

    todo = kwargs['instance']
    todo.category.todos.filter(sort__gt=todo.sort).update(sort=F('sort') - 1)


@receiver(post_delete, sender=TodoAttachmentModel)
def resort_todo_attachment(sender, **kwargs):
    """The receiver called after a todo attachment is deleted
    to resort them"""

    attachment = kwargs['instance']
    attachment.todo_item.attachments.filter(sort__gt=attachment.sort).update(sort=F('sort') - 1)


@receiver(post_delete, sender=TodoAttachmentModel)
def resort_todo_attachment(sender, **kwargs):
    """The receiver called after a todo attachment is deleted
    to delete the file it pointes to in the filesystem"""

    attachment = kwargs['instance']
    if attachment.file:
        if os.path.isfile(attachment.file.path):
            os.remove(attachment.file.path)
