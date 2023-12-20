from rest_framework import permissions


class IsSupplierOrCardManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "supplier") or request.user.is_superuser


class IsAdminOrSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "super_admin") or request.user.is_superuser
