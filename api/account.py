from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User

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

    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                json = serializer.data
                json['token'] = token.key
                return Response(json, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
