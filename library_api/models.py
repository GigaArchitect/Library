from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class category(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=25)


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, first_name, password, **extra_fields)

    def get_by_natural_key(self, username):
        """
        Look up a user by their natural key (email in this case).
        """
        return self.get(email=username)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        AUTHOR = ("AUTHOR",)
        PATRON = "PATRON"

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    role = models.CharField(choices=Role.choices, max_length=25, default=Role.PATRON)
    id = models.AutoField(primary_key=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    objects = UserManager()


class Author(User):
    role = User.Role.AUTHOR

    class Meta:
        proxy = True


class AuthorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


@receiver(post_save, sender=Author)
def create_author_profile(sender, instance, created, **kwargs):
    if created and instance.role == User.Role.AUTHOR:
        AuthorProfile.objects.create(user=instance)


class Patron(User):
    role = User.Role.PATRON

    class Meta:
        proxy = True


class PatronProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favourite_category = models.ManyToManyField(category)


@receiver(post_save, sender=Patron)
def create_patron_profile(sender, instance, created, **kwargs):
    if created and instance.role == User.Role.PATRON:
        PatronProfile.objects.create(user=instance)


class book(models.Model):
    authors = models.ManyToManyField(AuthorProfile)
    isbn = models.CharField(max_length=150, primary_key=True, unique=True)
    name = models.CharField(max_length=75)
    year_published = models.DateField()
    category = models.ManyToManyField(category)
    stock_copies = models.IntegerField()
