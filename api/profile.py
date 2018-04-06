from django.http import Http404
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import Profile
from api.permissions import PublicEndpoint, UserOwnsProfile


class ProfileSerializer(serializers.ModelSerializer):
    """
        Serializes Profile model data.
    """
    class Meta:
        model = Profile
        fields = "__all__"


class ProfileDetail(APIView):
    """
        Retrieve or update the User's profile.
    """

    permission_classes = (PublicEndpoint, UserOwnsProfile,)

    def get_object(self, request, pk):
        try:
            object = Profile.objects.get(pk=pk)
            self.check_object_permissions(request=request, obj=object)
            return object
        except Profile.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        profile = self.get_object(request=request, pk=pk)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)