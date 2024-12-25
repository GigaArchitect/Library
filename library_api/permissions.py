from rest_framework.permissions import BasePermission
from rest_framework.request import Request

class IsAuthor(BasePermission):
    def has_permission(self, request: Request, view):
        return request.user.role == "AUTHOR"
