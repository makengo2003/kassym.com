from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.is_staff


class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated


class NoPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return True
