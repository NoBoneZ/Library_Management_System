from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStaffOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        return request.method in SAFE_METHODS
