from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser


class patron(AbstractBaseUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    id = models.AutoField(primary_key=True, unique=True)
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "id", "email"]


class author(patron):
    pass


class category(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=25)


class books(models.Model):
    authors = models.ManyToManyField(author)
    isbn = models.CharField(max_length=150, primary_key=True, unique=True)
    name = models.CharField(max_length=75)
    year_published = models.DateField()
    category = models.ManyToManyField(category)
    stock_copies = models.IntegerField()
