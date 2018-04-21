"""
    This file will handle API commands related to the Journal functionality of the application.
"""
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response

from api.permissions import PublicEndpoint
from journal.models import Paper


@api_view(['GET'])
@permission_classes((PublicEndpoint,))
def papers_count(request):
    """
    Retrieve the number of submitted papers.
    """
    return Response(Paper.objects.count(), status=status.HTTP_200_OK)
