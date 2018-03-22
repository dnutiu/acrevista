from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status, permissions
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from rest_framework_jwt import authentication

from account.models import Profile
from api.permissions import PublicEndpoint


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(min_length=8, write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['email'],
                                        email=validated_data['email'],
                                        password=validated_data['password'])
        return user

    class Meta:
        model = User
        fields = ('id', 'email', 'password')


class UserCreate(APIView):
    """
    Creates the user.
    """
    permission_classes = (PublicEndpoint,)
    # TODO: Add some throttling.

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                Profile.objects.create(user=user)
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TestPermissions(APIView):
    """
    Test whether an user can access a protected endpoint.
    """

    authentication_classes = (authentication.JSONWebTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        json = {"message": "Da"}
        return Response(json, status=status.HTTP_200_OK)