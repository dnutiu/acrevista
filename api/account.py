"""
    This file will handle API functionality related to user Accounts.
"""
import datetime

from django.contrib.auth.models import User
from rest_framework import serializers, status, permissions
from rest_framework.generics import UpdateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from rest_framework.views import APIView
from rest_framework_jwt import authentication

from account.models import Profile
from acrevista import settings
from api.permissions import PublicEndpoint, UserIsEditorInActivePaper


def jwt_response_payload_handler(token, user=None, request=None):
    """ Custom response payload handler.
    This function controls the custom payload after login or token refresh. This data is returned through the web API.
    https://github.com/GetBlimp/django-rest-framework-jwt/issues/145
    """
    return {
        'token': token,
        'id': user.id,
        'profile_pk': user.profile.pk,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_staff': user.is_staff,
        'expiration_date': (datetime.datetime.utcnow() + settings.JWT_AUTH['JWT_EXPIRATION_DELTA']).timestamp()
    }


class UserSerializer(serializers.ModelSerializer):
    """
        Serializer for the User object.
    """
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    is_staff = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['email'],
                                        email=validated_data['email'],
                                        password=validated_data['password'],
                                        first_name=validated_data['first_name'],
                                        last_name=validated_data['last_name'])
        return user

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'is_staff')


class UserCreateView(APIView):
    """
    The UserCreateView creates the user.
    """
    permission_classes = (PublicEndpoint,)

    # TODO: Add some throttling.

    @classmethod
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TestPermissionsView(APIView):
    """
    This is a special view. It's role is to
    test whether an user can access a protected endpoint.
    """

    authentication_classes = (authentication.JSONWebTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @classmethod
    def get(self, request):
        json = {"message": "Da"}
        return Response(json, status=status.HTTP_200_OK)


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ChangePasswordView(UpdateAPIView):
    """
    ChangePasswordView is an endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response("Success.", status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeNameSerializer(serializers.ModelSerializer):
    """
    Serializer for name change
    """
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name')


class ChangeNameView(UpdateAPIView):
    """
    ChangePasswordView is an endpoint for changing the name.
    """
    model = User
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangeNameSerializer(self.object, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(ListAPIView):
    """
        Ensure that list of users that have email address likely similar to the 'email' query param.
        A json object containing many UserSerializer data is returned.
    """
    model = User
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, UserIsEditorInActivePaper)
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        email = request.GET.get('email')
        if email:
            users = self.queryset.filter(email__contains=email)
            serializer = self.serializer_class(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"details": "The GET param email is missing!"}, status=status.HTTP_400_BAD_REQUEST)
