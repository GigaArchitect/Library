from django.contrib.auth import authenticate
from django.http import request
from knox.models import AuthToken
from knox.views import IsAuthenticated
from knox.views import LoginView as KnoxLoginView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .forms import *
from .mixins import *
from .models import *
from .serializers import UserSerializer


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

        for user in data:
            user.pop("password", None)
            user.pop("password2", None)

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
