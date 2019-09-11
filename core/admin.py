from django.contrib import admin
from django.contrib.auth.models import Group

from core.models import UserProfileModel, TodoGroupModel, TodoModel, TodoAttachmentModel

admin.site.unregister(Group)
admin.site.register(UserProfileModel)
admin.site.register(TodoGroupModel)
admin.site.register(TodoModel)
admin.site.register(TodoAttachmentModel)
