from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import PatronProfile, User, Category, Book


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        # password and password2 are incjected fields and they are not stored in db
        fields = ["first_name", "last_name", "email", "role", "password", "password2"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError("Passwords not the same")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class PatronProfileSerializer(serializers.ModelSerializer):
    favourite_category = CategorySerializer()

    class Meta:
        model = PatronProfile
        fields = "__all__"

    def update(self, instance, validated_data):
        favourite_category = validated_data.pop("favourite_category", None)

        if favourite_category is not None:
            instance.favourite_category.clear()
            categories = [
                Category.objects.get_or_create(**cat_data)[0]
                for cat_data in favourite_category
            ]
            instance.favourite_category.set(categories)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"
