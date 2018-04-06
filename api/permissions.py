from rest_framework import permissions


class UserOwnsProfile(permissions.BasePermission):
    """
    Makes sure that the user owns the Profile it was to get or that the user is a staff member.
    """
    def has_object_permission(self, request, view, obj):
        is_owner = obj.pk == request.user.profile.pk
        is_admin = request.user.is_staff
        return is_owner or is_admin


class PublicEndpoint(permissions.BasePermission):
    def has_permission(self, request, view):
        return True
