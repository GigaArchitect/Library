from rest_framework.permissions import BasePermission

class IsAuthor(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == "AUTHOR":
            return True
        return False
