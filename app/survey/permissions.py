from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission: Only allow owners of an object to edit/delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Read-only permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write/delete permissions are only allowed to the owner
        return obj.created_by == request.user

class IsResearcher(permissions.BasePermission):
    """
    Allows access only to users with role 'researcher'.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and request.user.profile.role == 'researcher'
        )
