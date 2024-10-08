# Generated by Django 5.1.1 on 2024-09-21 09:25

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Habit",
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
                ("place", models.CharField(max_length=100)),
                ("time", models.TimeField()),
                ("action", models.CharField(max_length=255)),
                ("is_pleasant", models.BooleanField(default=False)),
                (
                    "frequency",
                    models.PositiveIntegerField(
                        default=1,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(7),
                        ],
                    ),
                ),
                ("reward", models.CharField(blank=True, max_length=255)),
                (
                    "duration",
                    models.PositiveIntegerField(
                        help_text="Duration in seconds",
                        validators=[django.core.validators.MaxValueValidator(120)],
                    ),
                ),
                ("is_public", models.BooleanField(default=False)),
                (
                    "related_habit",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="habits.habit",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="habits",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserProfile",
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
                    "telegram_chat_id",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
