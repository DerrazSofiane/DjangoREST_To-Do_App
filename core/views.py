from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from core.models import UserProfileModel, TodoGroupModel, TodoModel, TodoAttachmentModel
from core.serializers import UserProfileSerializer, TodoGroupSerializer, TodoItemSerializer, TodoAttachmentSerializer


@api_view(['POST'])
def user_login(request):
    """View for logging the users in"""

    if request.user.is_authenticated:
        return Response('User already logged in', status=status.HTTP_401_UNAUTHORIZED)

    username = request.data['username']
    password = request.data['password']

    user = authenticate(username=username, password=password)

    if user and hasattr(user, 'profile'):
        login(request, user)
        return Response('Logged In Successfully')
    else:
        return Response('Wrong Username or Password', status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def user_logout(request):
    """View for logging the users in"""

    if request.user.is_authenticated:
        logout(request)
        return Response('Logged Out Successfully')
    return Response('Your are not logged in', status=status.HTTP_401_UNAUTHORIZED)


class UserProfileView(viewsets.ViewSet):
    """View for the user profile.
    Retrieves, creates, Updates and Deletes a User Profile.
    """

    # permission_classes = (UserProfilePermissions,)
    serializer_class = UserProfileSerializer

    def retrieve(self, request, username=None):
        """Retrieves a user profile by its username
        Checks if a user profile with this username exist,
        if not, returns HTTP 404 Response.
        Arguments:
            request: the request data sent by the user,
                     it is not used here but required by django
            username: the username of the user profile that the user wants info about.
        Returns:
            HTTP 404 Response if user profile is not found,
            if not, returns HTTP 200 Response with the profile's JSON data.
        """
        user_profile = get_object_or_404(UserProfileModel, account__username=username)
        serializer = self.serializer_class(user_profile)
        return Response(serializer.data)

    def create(self, request):
        """Creates A new user profile and Logs it In.
        Checks if user is authenticated if true, return HTTP 401 Response,
        then it Validates the post data if not valid,
        return HTTP 400 Response, then creates the user and logs him in,
        and returns 201 Response.
        Arguments:
            request: the request data sent by the user, it is used
                     to get the post data from it to get validated and created,
                     and to log the user in.
        Returns:
             HTTP 400 Response if data is not valid,
             HTTP 401 Response if user is already logged in,
             HTTP 201 Response with the JSON data of the created profile.
        """

        if not request.user.is_authenticated:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                user_profile = serializer.save()
                login(request, user_profile.account)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, username=None):
        """Completely Updates the user profile.
        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions and get the data
            username: the username of the user profile that will be updated
        Returns:
             HTTP 404 Response if user profile is not found,
             HTTP 400 Response if the data is not
             valid with the errors,
             HTTP 403 Response if the user is not
             authorized to update that profile
             if not returns HTTP 200 Response with the update JSON data.
        """

        user_profile = get_object_or_404(UserProfileModel, account__username=username)
        self.check_object_permissions(request, user_profile)
        serializer = self.serializer_class(user_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            update_session_auth_hash(request, user_profile.account)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, username=None):
        """Partially Updates the user profile.
        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions and get the data
            username: the username of the user profile that will be updated
        Returns:
             HTTP 404 Response if user profile is not found,
             HTTP 400 Response if the data is not valid with the errors,
             HTTP 403 Response if the user is not
             authorized to update that profile,
             if not returns HTTP 200 Response with the update JSON data.
        """

        user_profile = get_object_or_404(UserProfileModel, account__username=username)
        self.check_object_permissions(request, user_profile)
        serializer = self.serializer_class(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            update_session_auth_hash(request, user_profile.account)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, username=None):
        """Deletes the user profile.
        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions
            username: the username of the user profile that will be deleted
        Returns:
            HTTP 404 Response if user profile is not found
            HTTP 403 Response if the user is not authorized
            to update that profile,
            if not returns HTTP 204 Response with no content.
        """

        user_profile = get_object_or_404(UserProfileModel, account__username=username)
        self.check_object_permissions(request, user_profile)
        user_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TodoGroupView(viewsets.ViewSet):
    """View for the user todo groups.
    Creates, Updates and Deletes a todo group.
    """

    # permission_classes = (UserAddressPermissions,)
    serializer_class = TodoGroupSerializer

    def create(self, request, username=None):
        """Creates a new todo group and adds it to the user's list.
        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions and get the data.
            username: the username of the user profile
                      which will be added a new todo group
        Returns:
            HTTP 403 Response if the user is
            not authorized to add a todo group to that user,
            HTTP 404 if user profile is not found,
            HTTP 400 Response if the data is not valid, if not,
            returns HTTP 201 Response with the todo group's JSON data.
        """
        user = get_object_or_404(UserProfileModel, account__username=username)
        self.check_object_permissions(request, user)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, username=None, pk=None):
        """Completely Updates a certain todo group from the user's list.
        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions and get the data.
            username: the username of the user profile
                      whose todo group will be updated
            pk: the id of the todo group that the user wants to change,
                it should by an integer.
        Returns:
            HTTP 403 Response if the user is
            not authorized to update that todo group,
            HTTP 400 Response if the data is not valid with the errors,
            HTTP 404 Response if the todo group is not found
            if not returns HTTP 200 Response with the update JSON data.
        """
        todo_group = get_object_or_404(TodoGroupModel, sort=pk, user__account__username=username)
        self.check_object_permissions(request, todo_group)
        serializer = self.serializer_class(todo_group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, username=None, pk=None):
        """Deletes a certain todo group from the user's list.
        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions
            username: the username of the user profile
                      whose todo group will be deleted
            pk: the id of the todo group that the user wants to delete,
                it should by an integer.
        Returns:
            HTTP 404 Response if the todo group is not found
            HTTP 403 Response if the user is
            not authorized to delete that todo group,
            if not, returns HTTP 204 Response with no content.
        """
        todo_group = get_object_or_404(TodoGroupModel, sort=pk, user__account__username=username)
        self.check_object_permissions(request, todo_group)
        todo_group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TodoView(viewsets.ViewSet):
    """View for the user todo item.
    Lists, Creates, Updates and Deletes a todo item.
    """

    # permission_classes = (UserAddressPermissions,)
    serializer_class = TodoItemSerializer

    def list(self, request, username=None):
        """Lists all todo items the user has.
        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions and in Pagination
            username: the username of the user profile
                      whose todo items will be returned
        Returns:
            HTTP 403 Response if the user is
            not authorized to see that user's todo items,
            HTTP 404 if user profile is not found,
            HTTP 200 Response with all todo items in
            the user's profile in JSON.
        """

        user = get_object_or_404(UserProfileModel, account__username=username)
        self.check_object_permissions(request, user)
        queryset = user.todo_groups.all()

        paginator = LimitOffsetPagination()
        paginator.default_limit = 10
        paginator.max_limit = 100
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = TodoGroupSerializer(paginated_queryset, many=True)

        return Response(data={'limit': paginator.limit, 'offset': paginator.offset,
                              'count': paginator.count, 'todo_groups': serializer.data})

    def retrieve(self, request, username=None, group_sort=None, pk=None):
        """Retrieves a certain todo item from the user's list

        Arguments:
            request: the request data sent by the user, it is used
                     to checks the user's permissions
            username: the username of the user profile
                      whose todo item will be returned
            group_sort: the sort of the todo groups that
                        the requested todo item is in.
            pk: the sort of the todo item that the user want info about,
                it should by an integer.
        Returns:
            HTTP 403 Response if the user is
            not authorized to see that user's todo item,
            HTTP 404 Response if todo item or user are not found, if not,
            returns HTTP 200 Response with the todo item's JSON data.
        """
        todo_item = get_object_or_404(TodoModel, sort=pk, category__sort=group_sort,
                                      category__user__account__username=username)
        self.check_object_permissions(request, todo_item)
        serializer = self.serializer_class(todo_item)
        return Response(serializer.data)

    def create(self, request, group_sort=None, username=None):
        """Creates a new todo item and adds it to the user's list.

        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions and get the data.
            username: the username of the user profile
                      which will be added a new todo item
            group_sort: the sort of the todo groups that
                        the created todo item will be in.
        Returns:
            HTTP 403 Response if the user is
            not authorized to add a todo item to that user,
            HTTP 404 if user profile is not found,
            HTTP 400 Response if the data is not valid, if not,
            returns HTTP 201 Response with the todo item's JSON data.
        """
        todo_group = get_object_or_404(TodoGroupModel, user__account__username=username,
                                       sort=group_sort)
        self.check_object_permissions(request, todo_group)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(category=todo_group)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, username=None, group_sort=None, pk=None):
        """Completely Updates a certain todo item from the user's list.

        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions and get the data.
            username: the username of the user profile
                      whose todo item will be updated
            group_sort: the sort of the todo groups that
                        the created todo item is in.
            pk: the id of the todo item that the user wants to change,
                it should by an integer.
        Returns:
            HTTP 403 Response if the user is
            not authorized to update that todo item,
            HTTP 400 Response if the data is not valid with the errors,
            HTTP 404 Response if the todo item is not found
            if not returns HTTP 200 Response with the update JSON data.
        """
        todo_item = get_object_or_404(TodoModel, sort=pk, category__sort=group_sort,
                                      category__user__account__username=username)
        self.check_object_permissions(request, todo_item)
        serializer = self.serializer_class(todo_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, username=None, group_sort=None, pk=None):
        """Partially Updates a certain todo item from the user's list.

        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions and get the data.
            username: the username of the user profile
                      whose todo item will be updated
            group_sort: the sort of the todo groups that
                        the created todo item is in.
            pk: the id of the todo item that the user wants to change,
                it should by an integer.
        Returns:
            HTTP 403 Response if the user is
            not authorized to update that todo item,
            HTTP 400 Response if the data is not valid with the errors,
            HTTP 404 Response if the todo item is not found
            if not returns HTTP 200 Response with the update JSON data.
        """
        todo_item = get_object_or_404(TodoModel, sort=pk, category__sort=group_sort,
                                      category__user__account__username=username)
        self.check_object_permissions(request, todo_item)
        serializer = self.serializer_class(todo_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, username=None, group_sort=None, pk=None):
        """Deletes a certain todo item from the user's list.
        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions
            username: the username of the user profile
                      whose todo item will be deleted
            group_sort: the sort of the todo groups that
                        the created todo item is in.
            pk: the id of the todo item that the user wants to delete,
                it should by an integer.
        Returns:
            HTTP 404 Response if the todo item is not found
            HTTP 403 Response if the user is
            not authorized to delete that todo item,
            if not, returns HTTP 204 Response with no content.
        """
        todo_item = get_object_or_404(TodoModel, sort=pk, category__sort=group_sort,
                                      category__user__account__username=username)
        self.check_object_permissions(request, todo_item)
        todo_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TodoAttachmentView(viewsets.ViewSet):
    """View for the todo attachment.
    Lists, Creates and Deletes a todo attachment.
    """

    # permission_classes = (UserAddressPermissions,)
    serializer_class = TodoAttachmentSerializer

    def list(self, request, username=None, group_sort=None, item_sort=None):
        """Lists all todo attachment in a todo item.

        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions and in Pagination
            username: the username of the user profile
                      whose todo attachments will be returned
            group_sort: the todo group sort that the todo is in
            item_sort: the todo item sort that the attachments are in
        Returns:
            HTTP 403 Response if the user is
            not authorized to see that todo's attachments,
            HTTP 404 if todo is not found,
            HTTP 200 Response with all todo attachments in JSON.
        """

        todo_item = get_object_or_404(TodoModel, category__user__account__username=username,
                                      category__sort=group_sort, sort=item_sort)
        self.check_object_permissions(request, todo_item)
        queryset = todo_item.attachments.all()

        paginator = LimitOffsetPagination()
        paginator.default_limit = 10
        paginator.max_limit = 100
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(paginated_queryset, many=True)

        return Response(data={'limit': paginator.limit, 'offset': paginator.offset,
                              'count': paginator.count, 'attachments': serializer.data})

    def create(self, request, username=None, group_sort=None, item_sort=None):
        """Creates a new todo attachment and adds it to the item's list.
        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions and get the data.
            username: the username of the user profile
                      which will be added a new todo attachment
            group_sort: the todo group sort that the todo is in
            item_sort: the todo item sort that the attachment will be in
        Returns:
            HTTP 403 Response if the user is
            not authorized to add a todo attachment to that todo item,
            HTTP 404 if todo is not found,
            HTTP 400 Response if the data is not valid, if not,
            returns HTTP 201 Response with the todo attachment's JSON data.
        """
        todo_item = get_object_or_404(TodoModel, category__user__account__username=username,
                                      category__sort=group_sort, sort=item_sort)
        self.check_object_permissions(request, todo_item)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(todo_item=todo_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, username=None, group_sort=None, item_sort=None, pk=None):
        """Deletes a certain todo attachment from the todo's attachments.
        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions
            username: the username of the user profile
                      whose todo attachment will be deleted

            group_sort: the todo group sort that the todo is in
            item_sort: the todo item sort that the attachment is in
            pk: the id of the todo attachment that the user wants to delete,
                it should by an integer.
        Returns:
            HTTP 404 Response if the todo attachment is not found
            HTTP 403 Response if the user is
            not authorized to delete that todo attachment,
            if not, returns HTTP 204 Response with no content.
        """
        attachment = get_object_or_404(TodoAttachmentModel, todo_item__category__user__account__username=username,
                                       todo_item__category__sort=group_sort, todo_item__sort=item_sort, sort=pk)
        self.check_object_permissions(request, attachment)
        attachment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
