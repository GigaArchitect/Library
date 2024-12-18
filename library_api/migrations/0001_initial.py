# Generated by Django 5.1 on 2024-09-03 00:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AuthorProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="category",
            fields=[
                (
                    "id",
                    models.AutoField(primary_key=True, serialize=False, unique=True),
                ),
                ("name", models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                ("first_name", models.CharField(max_length=30)),
                ("last_name", models.CharField(max_length=30)),
                ("email", models.EmailField(max_length=254)),
                (
                    "role",
                    models.CharField(
                        choices=[("AUTHOR", "Author"), ("PATRON", "Patron")],
                        default="PATRON",
                        max_length=25,
                    ),
                ),
                (
                    "id",
                    models.AutoField(primary_key=True, serialize=False, unique=True),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="books",
            fields=[
                (
                    "isbn",
                    models.CharField(
                        max_length=150, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("name", models.CharField(max_length=75)),
                ("year_published", models.DateField()),
                ("stock_copies", models.IntegerField()),
                ("authors", models.ManyToManyField(to="library_api.authorprofile")),
                ("category", models.ManyToManyField(to="library_api.category")),
            ],
        ),
        migrations.CreateModel(
            name="PatronProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "favourite_category",
                    models.ManyToManyField(to="library_api.category"),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="library_api.user",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="authorprofile",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="library_api.user"
            ),
        ),
        migrations.CreateModel(
            name="Author",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("library_api.user",),
        ),
        migrations.CreateModel(
            name="Patron",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("library_api.user",),
        ),
    ]
