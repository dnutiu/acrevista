import datetime

from django.contrib.auth.models import User
from rest_framework import serializers, status, permissions
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from rest_framework.views import APIView
from rest_framework_jwt import authentication

from account.models import Profile
from acrevista import settings
from api.permissions import PublicEndpoint


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
        Profile.objects.create(user=user)
        return user

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'is_staff')


class UserCreate(APIView):
    """
    Creates the user.
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


class TestPermissions(APIView):
    """
    Test whether an user can access a protected endpoint.
    """

    authentication_classes = (authentication.JSONWebTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @classmethod
    def get(self, request):
        json = {"message": "Da"}
        return Response(json, status=status.HTTP_200_OK)
