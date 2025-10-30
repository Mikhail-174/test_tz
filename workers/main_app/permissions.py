from rest_framework import permissions
from django.contrib.auth.models import Permission, Group

perms = ("main_app.add_position", "main_app.change_position", "main_app.delete_position", "main_app.view_position", "main_app.add_worker", "main_app.change_worker", "main_app.delete_worker", "main_app.view_worker")

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        is_admin = None
        try:
            is_admin = request.user.groups.get(name="Admin")
        except Group.DoesNotExist:
            print(f"{request.user.username} trying to change data with no permissions")
        return is_admin is not None

    # def has_object_permission(self, request, view, obj):
    #     is_admin = None
    #     try:
    #         is_admin = request.user.groups.get(name="Admin")
    #     except Group.DoesNotExist:
    #         print(f"{request.user.username} trying to change data with no permissions")
    #     return is_admin is not None





