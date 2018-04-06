import itertools
from django.http import Http404
from rest_framework import serializers, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import Profile
from api.permissions import UserOwnsProfile, PublicEndpoint

# Flatten the tuple choices into a nice set
# ( ('Romania', 'Romania), ...) -> { 'Romania', ...}
PROFILE_VALID_COUNTRIES = set(itertools.chain.from_iterable(Profile.COUNTRY_CHOICES))
PROFILE_VALID_TITLES = set(itertools.chain.from_iterable(Profile.TITLE_CHOICES))


@api_view(['GET'])
@permission_classes((PublicEndpoint,))
def valid_titles(request):
    """
    Retrieve a set of valid titles.
    """
    return Response(PROFILE_VALID_TITLES, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((PublicEndpoint,))
def valid_countries(request):
    """
    Retrieve a set of valid country names.
    """
    return Response(PROFILE_VALID_COUNTRIES, status=status.HTTP_200_OK)


class ProfileSerializer(serializers.ModelSerializer):
    """
        Serializes Profile model data.
    """
    title = serializers.CharField(max_length=64, default='Dr')
    phone = serializers.CharField(max_length=64, default='')
    country = serializers.CharField(max_length=64, default='Romania')
    affiliation = serializers.CharField(max_length=64, default='')

    def validate_title(self, value):
        if value not in PROFILE_VALID_TITLES:
            raise serializers.ValidationError("Invalid profile title!")
        return value

    def validate_country(self, value):
        if value not in PROFILE_VALID_COUNTRIES:
            raise serializers.ValidationError("Invalid country name!")
        return value

    class Meta:
        model = Profile
        fields = ('title', 'phone', 'country', 'affiliation')


class ProfileDetail(APIView):
    """
        Retrieve or update the User's profile.
    """

    permission_classes = (permissions.IsAuthenticated, UserOwnsProfile,)

    def get_object(self, request, pk):
        try:
            obj = Profile.objects.get(pk=pk)
            self.check_object_permissions(request=request, obj=obj)
            return obj
        except Profile.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """
            Retrieves a user's profile based on the primary key.
        """
        profile = self.get_object(request=request, pk=pk)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request, pk):
        """
            Updates the user's profile.
        """
        profile = self.get_object(request, pk)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
