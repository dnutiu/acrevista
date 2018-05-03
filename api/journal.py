"""
    This file will handle API commands related to the Journal functionality of the application.
"""
import itertools

from rest_framework import status, serializers, generics
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from api.permissions import PublicEndpoint
from api.profile import UserDetailsSerializer
from journal.models import Paper, JOURNAL_PAPER_FILE_VALIDATOR

PAPER__STATUS_CHOICES = set(itertools.chain.from_iterable(Paper.STATUS_CHOICES))


@api_view(['GET'])
@permission_classes((PublicEndpoint,))
def papers_count(request):
    """
    Retrieve the number of submitted papers.
    """
    return Response(Paper.objects.count(), status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated, IsAdminUser))
def set_editor(request, pk):
    """
        Ensure that a staff member can set itself as an editor.
    """
    try:
        paper = Paper.objects.get(id=pk)
        if paper and request.method == 'POST':
            paper.editor = request.user
            paper.save()
            return Response({"message": "set"}, status=status.HTTP_200_OK)
        elif paper and request.method == 'DELETE':
            paper.editor = None
            paper.save()
            return Response({"message": "deleted"}, status=status.HTTP_200_OK)
    except Exception:
        return Response({"details": "Paper not found!"}, status.HTTP_404_NOT_FOUND)


class PaperSerializer(serializers.ModelSerializer):
    """
        Serializer for the Paper model.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    editor = serializers.PrimaryKeyRelatedField(read_only=True)
    title = serializers.CharField(max_length=256, required=True)
    description = serializers.CharField(max_length=2000, required=True)
    authors = serializers.CharField(max_length=4096, required=True)
    status = serializers.CharField(default="processing")
    reviewers = UserDetailsSerializer(read_only=True, many=True)
    manuscript = serializers.FileField(allow_empty_file=False, allow_null=False, required=True,
                                       validators=[JOURNAL_PAPER_FILE_VALIDATOR])
    cover_letter = serializers.FileField(allow_empty_file=False, allow_null=False, required=True,
                                         validators=[JOURNAL_PAPER_FILE_VALIDATOR])
    supplementary_materials = serializers.FileField(allow_null=True, required=False,
                                                    validators=[JOURNAL_PAPER_FILE_VALIDATOR])

    def validate_status(self, value):
        if value not in PAPER__STATUS_CHOICES:
            raise serializers.ValidationError("Invalid paper status!")
        return value

    class Meta:
        model = Paper
        fields = ('id', 'user', 'editor', 'title', 'description', 'authors', 'status',
                  'manuscript', 'cover_letter', 'supplementary_materials', 'reviewers')


class PaperDetail(generics.RetrieveAPIView):
    """
        Retrieve the detail of a single paper.
    """
    serializer_class = PaperSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, *args, **kwargs):
        if self.request.user.is_staff:
            return Paper.objects.all()

        return Paper.objects.all().filter(user=self.request.user)


class PaperListSubmitted(generics.ListCreateAPIView):
    """
        This view lists the papers currently belonging to a user and lets the user submit it's own papers.
    """
    serializer_class = PaperSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, *args, **kwargs):
        return Paper.objects.all().filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = PaperSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaperListAll(generics.ListAPIView):
    """
        This view lists the all the papers.
    """
    queryset = Paper.objects.all()
    serializer_class = PaperSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)


class PaperListEditor(generics.ListAPIView):
    """
        This view lists the papers where the user is an editor.
    """
    queryset = Paper.objects.all()
    serializer_class = PaperSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, *args, **kwargs):
        return Paper.objects.all().filter(editor=self.request.user)


class PaperListNoEditor(generics.ListAPIView):
    """
        This view lists the papers that don't have an editor.
    """
    queryset = Paper.objects.all()
    serializer_class = PaperSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)

    def get_queryset(self, *args, **kwargs):
        return Paper.objects.all().filter(editor=None)
