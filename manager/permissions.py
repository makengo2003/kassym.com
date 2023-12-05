from rest_framework import permissions


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "manager") or hasattr(request.user, "super_admin")
