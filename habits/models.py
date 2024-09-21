from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="habits")
    place = models.CharField(max_length=100)
    time = models.TimeField()
    action = models.CharField(max_length=255)
    is_pleasant = models.BooleanField(default=False)
    related_habit = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    frequency = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(7)]
    )
    reward = models.CharField(max_length=255, blank=True)
    duration = models.PositiveIntegerField(
        validators=[MaxValueValidator(120)], help_text="Duration in seconds"
    )
    is_public = models.BooleanField(default=False)

    def clean(self):
        if self.reward and self.related_habit:
            raise ValidationError("Cannot have both reward and related habit.")
        if self.is_pleasant and (self.reward or self.related_habit):
            raise ValidationError(
                "Pleasant habits cannot have rewards or related habits."
            )
        if self.frequency > 7:
            raise ValidationError(
                "Cannot perform habit less often than once every 7 days."
            )
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.action} at {self.time} in {self.place}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    telegram_chat_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
