from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "role"
        )


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm):
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
        )
