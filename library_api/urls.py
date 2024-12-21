from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from knox import views as kx
from rest_framework import permissions

from .views import *

app_name = "library_api"

schema_view = get_schema_view(
    openapi.Info(
        title="Library",
        default_version="v1",
        description="My API Desgin For Libraries",
        contact=openapi.Contact(email="consumedprince@gmail.com"),
        license=openapi.License(name="GPLv2"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("swagger/", schema_view.with_ui("swagger"), name="swagger-ui"),
    path("signup", SignUpView.as_view(), name="signup"),
    path("login", LoginView, name="login"),
    path("logout", kx.LogoutView.as_view(), name="logout"),
    path("logoutall", kx.LogoutAllView.as_view(), name="logoutall"),
    path("users", ListUsers, name="users"),
    path("user/<int:id>", GetUser, name="user"),
    path("user/<int:id>/update", UpdateUser.as_view(), name="update-user"),
    path("user/<int:id>/delete", DeleteUser.as_view(), name="update-user"),
    path("books", ListBook.as_view(), name="list-books"),
    path("books/<int:pk>", ListBook.as_view(), name="list-book"),
    path("books/create", CreateBook.as_view(), name="create-book"),
    path("books/<int:pk>/update", UpdateBook.as_view(), name="update-book"),
    path("books/<int:pk>/delete", DeleteBook.as_view(), name="delete-book")
]
