from rest_framework import permissions


class UserOwnsProfile(permissions.BasePermission):
    """
        Ensure that the user owns the Profile it was to get or that the user is a staff member.
    """

    def has_object_permission(self, request, view, obj):
        is_owner = obj.pk == request.user.profile.pk
        is_admin = request.user.is_staff
        return is_owner or is_admin


class PublicEndpoint(permissions.BasePermission):
    def has_permission(self, request, view):
        return True


class UserCanReview(permissions.BasePermission):
    """
        Ensure that a user can submit a review by fulfilling the following conditions:
            - User is listed as a reviewer for the selected paper.
            - User is an editor for the selected paper.
            - User is a staff member.
    """

    def has_object_permission(self, request, view, obj):
        is_reviewer = obj.reviewers.filter(id=request.user.id).exists()
        is_admin = request.user.is_staff
        is_editor = obj.editor == request.user
        return is_reviewer or is_admin or is_editor


class UserIsEditor(permissions.BasePermission):
    """
        Ensure that a user is assigned as an editor.
    """

    def has_object_permission(self, request, view, obj):
        is_admin = request.user.is_staff
        is_editor = obj.editor == request.user
        return is_admin or is_editor


class UserIsEditorInActivePaper(permissions.BasePermission):
    """
         Ensure that the user is editor to a paper that is's current status is under review.
    """

    def has_permission(self, request, view):
        from journal.models import Paper
        paper_exists = Paper.objects.filter(editor=request.user, status=Paper.STATUS_CHOICES[1][0]).exists()
        return paper_exists
