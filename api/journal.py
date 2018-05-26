"""
    This file will handle API commands related to the Journal functionality of the application.
"""
import itertools

from django.contrib.auth.models import User
from rest_framework import status, serializers, generics
from rest_framework.decorators import permission_classes, api_view
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from api.permissions import PublicEndpoint, UserIsReviewer
from api.profile import UserDetailsSerializer
from journal.models import Paper, JOURNAL_PAPER_FILE_VALIDATOR, Review

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
    # TODO: Needs refactoring. See AddRemoveReviewer class view, should be similar.
    """
        Ensure that a staff member can set itself as an editor.
    """
    try:
        paper = Paper.objects.get(id=pk)
        if paper and request.method == 'POST':
            paper.editor = request.user
            paper.save()
            return Response({"details": "set"}, status=status.HTTP_200_OK)
        elif paper and request.method == 'DELETE':
            paper.editor = None
            paper.save()
            return Response({"details": "deleted"}, status=status.HTTP_200_OK)
    except Paper.DoesNotExist:
        return Response({"details": "Paper not found!"}, status.HTTP_404_NOT_FOUND)


class PaperSerializer(serializers.ModelSerializer):
    """
        Serializer for the Paper model.
    """
    user = UserDetailsSerializer(read_only=True)
    editor = UserDetailsSerializer(read_only=True)
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


class PaperSerializerPeer(serializers.ModelSerializer):
    """
        Serializer to facilitate adding and removing reviewers and the editor.
        This should be used by views that have admin level permissions only.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    editor = serializers.PrimaryKeyRelatedField(read_only=True)
    reviewers = UserDetailsSerializer(many=True)

    class Meta:
        model = Paper
        fields = ('id', 'user', 'editor', 'reviewers')


class AddRemoveReviewer(generics.RetrieveUpdateDestroyAPIView):
    """
        Ensure that a reviewer can be added an removed to a paper.
    """
    permission_classes = (IsAuthenticated, IsAdminUser)
    serializer_class = PaperSerializerPeer

    def get_object(self, pk=None):
        try:
            paper = Paper.objects.get(pk=pk)
        except Paper.DoesNotExist:
            paper = None
        return paper

    def get_user(self, request):
        try:
            pk = request.data["user_pk"]
            user = User.objects.get(pk=pk)
        except Exception:
            user = None
        return user

    def get(self, request, pk=None, *args, **kwargs):
        paper = self.get_object(pk)
        if paper:
            serializer = self.serializer_class(paper)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"details": "Paper not found!"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None, *args, **kwargs):
        paper = self.get_object(pk)
        user = self.get_user(request)
        if paper and user:
            paper.reviewers.add(user)
            serializer = self.serializer_class(paper)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"details": "Paper or User not found!"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None, *args, **kwargs):
        paper = self.get_object(pk)
        user = self.get_user(request)
        if paper and user:
            paper.reviewers.remove(user)
            serializer = self.serializer_class(paper)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"details": "Paper or User not found!"}, status=status.HTTP_400_BAD_REQUEST)


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
    serializer_class = PaperSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, *args, **kwargs):
        return Paper.objects.all().filter(editor=self.request.user)


class PaperListReviewer(generics.ListAPIView):
    """
        This view lists the papers where the user is a reviewer.
    """
    serializer_class = PaperSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, *args, **kwargs):
        return Paper.objects.all().filter(reviewers=self.request.user)


class PaperListNoEditor(generics.ListAPIView):
    """
        This view lists the papers that don't have an editor.
    """
    serializer_class = PaperSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)

    def get_queryset(self, *args, **kwargs):
        return Paper.objects.all().filter(editor=None)


class ReviewSerializer(serializers.ModelSerializer):
    """
        Serializer for the Review model.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    paper = serializers.PrimaryKeyRelatedField(queryset=Paper.objects.all(), required=True)
    editor_review = serializers.BooleanField(read_only=True)
    appropriate = serializers.CharField(required=True)
    recommendation = serializers.CharField(required=True)
    comment = serializers.CharField(required=True)

    class Meta:
        model = Review
        fields = ('id', 'user', 'paper', 'editor_review', 'created', 'appropriate', 'recommendation', 'comment')


class ReviewAddView(generics.CreateAPIView):
    """
        Ensure that a review can be created.
    """
    permission_classes = (IsAuthenticated, UserIsReviewer)
    queryset = Review.objects.all()
    paper_queryset = Paper.objects.all()

    def check_if_user_is_reviewer(self, request=None, pk=None):
        obj = get_object_or_404(self.paper_queryset, pk=pk)
        self.check_object_permissions(request=request, obj=obj)
        return obj

    def post(self, request, pk=None, *args, **kwargs):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            paper = self.check_if_user_is_reviewer(request=request, pk=request.data['paper'])
            is_editor_review = paper.editor == request.user
            serializer.save(user=request.user, editor_review=is_editor_review)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
