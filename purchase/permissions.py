from rest_framework import permissions


class IsBuyer(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "buyer") or hasattr(request.user, "super_admin")
