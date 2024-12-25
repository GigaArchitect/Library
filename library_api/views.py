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
from .serializers import BookSerializer, CategorySerializer, UserSerializer


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
        return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def GetUser(request, id):
    if request.method == "GET":
        try:
            user = User.objects.get(pk=id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)


class UpdateUser(APIView):
    permission_classes = [IsAuthenticated]
    ALLOWED_FIELDS = ["first_name", "last_name", "email"]

    def put(self, request: Request, id):
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)
        if request.user == user:
            try:
                password = request.data.pop("password", None)
                if password:
                    user.set_password(password)
                for field, value in request.data.items():
                    if field in self.ALLOWED_FIELDS and hasattr(user, field):
                        setattr(user, field, value)
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

######## Books #########################################################
class ListBook(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class CreateBook(CreateAPIView):
    permission_classes = [IsAuthenticated, IsAuthor]
    serializer_class = BookSerializer

class UpdateBook(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsAuthor]
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class DeleteBook(DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Book.objects.all()
    serializer_class = BookSerializer

###### Categories ######################################################
class ListCategory(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CreateCategory(CreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = CategorySerializer

class UpdateCategory(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class DeleteCategory(DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def BorrowBook(request, pk):

    try:
        to_borrow = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return Response("Book Not Found !", status=status.HTTP_404_NOT_FOUND)

    try:
        profile = PatronProfile.objects.get(user=request.user)
    except PatronProfile.DoesNotExist:
        return Response("Something Is Wrong With Your Profile, Contact The Admin !", status=status.HTTP_404_NOT_FOUND)

    if to_borrow.borrowed_by.filter(user=request.user).exists() :
        return Response("You Already Borrowed This Book !", status=status.HTTP_400_BAD_REQUEST)

    if to_borrow.stock_copies <= 0:
        return Response("Not Enough Copies Exist !", status=status.HTTP_400_BAD_REQUEST)

    to_borrow.stock_copies -= 1
    to_borrow.borrowed_by.add(profile)
    to_borrow.save()

    return Response("Added to your List !", status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ReturnBook(request, pk):

    try:
        to_return = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return Response("Book Doesn't Exist On Database, Please Return Manually !", status=status.HTTP_404_NOT_FOUND)

    try:
        profile = PatronProfile.objects.get(user=request.user)
    except PatronProfile.DoesNotExist:
        return Response("Something Is Wrong With Your Profile, Contact The Admin !", status=status.HTTP_404_NOT_FOUND)

    if not to_return.borrowed_by.filter(user=request.user).exists():
        return Response("You Don't Own a Copy Of This Book", status=status.HTTP_400_BAD_REQUEST)

    to_return.stock_copies += 1
    to_return.borrowed_by.remove(profile)
    to_return.save()

    return Response("Removed from your List !", status=status.HTTP_200_OK)
