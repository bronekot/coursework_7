from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Habit.
    """

    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ("user",)

    def validate(self, data):
        """
        Проверяет валидность данных привычки.

        - Нельзя одновременно указывать связанную привычку и вознаграждение.
        - Приятные привычки не могут иметь вознаграждения или связанных привычек.
        - Связанная привычка должна быть приятной.
        - Нельзя выполнять привычку реже, чем раз в 7 дней.
        """
        if data.get("reward") and data.get("related_habit"):
            raise serializers.ValidationError(
                "Нельзя одновременно указывать вознаграждение и связанную привычку."
            )
        if data.get("is_pleasant") and (
            data.get("reward") or data.get("related_habit")
        ):
            raise serializers.ValidationError(
                "Приятные привычки не могут иметь вознаграждения или связанных привычек."
            )
        if data.get("related_habit") and not data["related_habit"].is_pleasant:
            raise serializers.ValidationError(
                "Связанная привычка должна быть приятной."
            )
        if data.get("frequency", 1) > 7:
            raise serializers.ValidationError(
                "Нельзя выполнять привычку реже, чем раз в 7 дней."
            )
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "password", "email")

    def create(self, validated_data):
        """
        Создает нового пользователя с зашифрованным паролем.
        """
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user
