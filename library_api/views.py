from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from knox.views import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import *
from .mixins import *
from .models import *
from .permissions import IsAuthor
from .serializers import BookSerializer, UserSerializer


class SignUpView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def LoginView(request):
    email = request.data.get("email")
    password = request.data.get("password")

    user = authenticate(request, email=email, password=password)
    if user is not None:
        _, token = AuthToken.objects.create(user)
        update_last_login(User, user)
        return Response({"message": "Successful Login", "token": token})
    else:
        return Response({"message": "Invalid Email or Password"}, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def ListUsers(request):
    if request.method == "GET":
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        data = serializer.data
        # for user in data:
        #     user.pop("password", None)
        #     user.pop("password2", None)
        return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def GetUser(request, id):
    if request.method == "GET":
        try:
            user = User.objects.get(pk=id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except:
            return Response("User Not Found")


class UpdateUser(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request: Request, id):
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)
        if request.user == user:
            try:
                for field, value in request.data.items():
                    if hasattr(user, field) and field != "password":
                        setattr(user, field, value)
                    password = request.data.get("password")
                    if password:
                        user.set_password(password)
                user.save()
                return Response("Updated Successfully", status=status.HTTP_200_OK)
            except:
                return Response(
                    "Can't Update User, Make Sure Data Is Correct",
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                "Can't Modify Other Users Bro !", status=status.HTTP_401_UNAUTHORIZED
            )


class DeleteUser(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request: Request, id):
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)
        try:
            user.delete()
            return Response("Deleted Successfully", status=status.HTTP_200_OK)
        except:
            return Response(
                "Can't Delete User",
                status=status.HTTP_400_BAD_REQUEST,
            )


class ListBook(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = book.objects.all()
    serializer_class = BookSerializer

class CreateBook(CreateAPIView):
    permission_classes = [IsAuthenticated, IsAuthor]
    serializer_class = BookSerializer

class UpdateBook(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsAuthor]
    queryset = book.objects.all()
    serializer_class = BookSerializer

class DeleteBook(DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = book.objects.all()
    serializer_class = BookSerializer
