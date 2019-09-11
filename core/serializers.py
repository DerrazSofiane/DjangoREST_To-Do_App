from django.contrib.auth.models import User
from django.core import exceptions
import django.contrib.auth.password_validation as validators
from rest_framework import serializers

from core.models import UserProfileModel, TodoGroupModel, TodoModel, TodoAttachmentModel


class UserSerializer(serializers.ModelSerializer):
    """The serializer for the django auth user model"""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password')
        extra_kwargs = {
            'first_name': {'allow_blank': False, 'required': True},
            'last_name': {'allow_blank': False, 'required': True},
            'password': {'write_only': True},
        }

    def validate(self, data):
        """Validate user's password using django auth password validators"""

        password = data.get('password', '')
        if password:
            user = User(**data)
            errors = dict()
            try:
                validators.validate_password(password=password, user=user)
            except exceptions.ValidationError as e:
                errors['password'] = list(e.messages)

            if errors:
                raise serializers.ValidationError(errors)

        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """The serializer for the user profile model"""

    account = UserSerializer()

    class Meta:
        model = UserProfileModel
        fields = ('account', 'profile_photo')
        extra_kwargs = {
            'profile_photo': {'required': False},
        }

    def create(self, validated_data):
        """Creates a new user profile from the request's data"""

        account_data = validated_data.pop('account')
        account = User(**account_data)
        account.set_password(account.password)
        account.save()

        user_profile = UserProfileModel.objects.create(account=account, **validated_data)
        return user_profile

    def update(self, instance, validated_data):
        """Updates a certain user profile from the request's data"""

        instance.profile_photo = validated_data.get('profile_photo', instance.profile_photo)
        instance.save()

        account_data = validated_data.pop('account', {})
        account = instance.account
        account.first_name = account_data.get('first_name', account.first_name)
        account.last_name = account_data.get('last_name', account.last_name)
        account.username = account_data.get('username', account.username)
        if account_data.get('password', None) is not None:
            account.set_password(account_data.get('password'))
        account.save()

        return instance


class TodoAttachmentSerializer(serializers.ModelSerializer):
    """The serializer for the todo item attachment model"""

    class Meta:
        model = TodoAttachmentModel
        fields = ('sort', 'file')
        extra_kwargs = {
            'sort': {'read_only': True}
        }


class TodoItemSerializer(serializers.ModelSerializer):
    """The serializer for the todo item model"""

    attachments = TodoAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = TodoModel
        fields = ('sort', 'title', 'status', 'description', 'attachments')
        extra_kwargs = {
            'sort': {'required': False}
        }

    def validate_sort(self, sort):
        """validator for sort field"""

        if not self.instance:
            raise serializers.ValidationError("sort can't be specified before creation")
        if sort > self.instance.category.todos.count() or sort < 1:
            raise serializers.ValidationError("invalid sort number")
        return sort

    def update(self, instance, validated_data):
        """updates a todo item"""

        instance.title = validated_data.get('title', instance.title)
        instance.status = validated_data.get('status', instance.status)
        instance.description = validated_data.get('description', instance.description)

        if validated_data.get('sort', None):
            old_sort = instance.sort
            new_sort = validated_data.get('sort')

            instance.sort = None
            instance.save()

            if new_sort - old_sort > 0:
                todos = instance.category.todos.filter(sort__gt=old_sort,
                                                       sort__lte=new_sort,
                                                       sort__isnull=False)
                for todo in todos:
                    todo.sort -= 1
                    todo.save()

            elif new_sort - old_sort < 0:
                todos = instance.category.todos.filter(sort__lt=old_sort,
                                                       sort__gte=new_sort,
                                                       sort__isnull=False).order_by('-sort')
                for todo in todos:
                    todo.sort += 1
                    todo.save()

            instance.sort = new_sort
            instance.save()

        return instance


class TodoGroupSerializer(serializers.ModelSerializer):
    """The serializer for the todo group model"""

    todos = TodoItemSerializer(many=True, read_only=True)

    class Meta:
        model = TodoGroupModel
        fields = ('sort', 'title', 'todos')
        extra_kwargs = {
            'sort': {'required': False}
        }

    def validate_sort(self, sort):
        """validator for sort field"""

        if not self.instance:
            raise serializers.ValidationError("sort can't be specified before creation")
        if sort > self.instance.user.todo_groups.count() or sort < 1:
            raise serializers.ValidationError("invalid sort number")
        return sort

    def update(self, instance, validated_data):
        """updates a todo group"""

        instance.title = validated_data.get('title', instance.title)

        if validated_data.get('sort', None):
            old_sort = instance.sort
            new_sort = validated_data.get('sort')

            instance.sort = None
            instance.save()

            if new_sort - old_sort > 0:
                groups = instance.user.todo_groups.filter(sort__gt=old_sort,
                                                          sort__lte=new_sort,
                                                          sort__isnull=False)
                for group in groups:
                    group.sort -= 1
                    group.save()

            elif new_sort - old_sort < 0:
                groups = instance.user.todo_groups.filter(sort__lt=old_sort,
                                                          sort__gte=new_sort,
                                                          sort__isnull=False).order_by('-sort')
                for group in groups:
                    group.sort += 1
                    group.save()

            instance.sort = new_sort
            instance.save()

        return instance
