from unittest.mock import patch

from django.contrib.auth.models import User
from django.forms import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Habit, UserProfile
from .serializers import HabitSerializer, UserSerializer
from .tasks import send_habit_reminders, send_telegram_notification

# Настройки для тестирования Celery
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=CELERY_TASK_ALWAYS_EAGER,
    CELERY_TASK_EAGER_PROPAGATES=CELERY_TASK_EAGER_PROPAGATES,
)
class CeleryTestCase(TestCase):
    pass


# Используйте CeleryTestCase вместо TestCase для классов, которые тестируют Celery задачи


class CeleryTaskTests(CeleryTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.user.profile.telegram_chat_id = "123456789"
        self.user.profile.save()
        self.habit = Habit.objects.create(
            user=self.user,
            place="Home",
            time=timezone.now().time(),
            action="Read a book",
            duration=60,
        )

    @patch("habits.tasks.send_telegram_notification.delay")
    def test_send_habit_reminders(self, mock_send_notification):
        send_habit_reminders()
        mock_send_notification.assert_called_once_with(
            "123456789", "Напоминание: Время для привычки 'Read a book'"
        )

    @patch("habits.tasks.send_telegram_notification.delay")
    def test_send_habit_reminders_no_matching_time(self, mock_send_notification):
        self.habit.time = (timezone.now() - timezone.timedelta(hours=1)).time()
        self.habit.save()
        send_habit_reminders()
        mock_send_notification.assert_not_called()


class TelegramTests(CeleryTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.habit = Habit.objects.create(
            user=self.user,
            place="Home",
            time="12:00:00",
            action="Read a book",
            duration=60,
        )
        self.user.profile.telegram_chat_id = "123456789"
        self.user.profile.save()

    @patch("habits.tasks.telegram.Bot.send_message")
    def test_send_telegram_notification(self, mock_send_message):
        send_telegram_notification(self.user.profile.telegram_chat_id, "Test message")
        mock_send_message.assert_called_once_with(
            chat_id="123456789", text="Test message"
        )


class AuthTests(APITestCase):
    def test_register_user(self):
        url = reverse("register")
        data = {
            "username": "newuser",
            "password": "newpassword123",
            "email": "newuser@example.com",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, "newuser")


class SerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.habit_data = {
            "user": self.user,
            "place": "Home",
            "time": "12:00:00",
            "action": "Read a book",
            "duration": 60,
            "is_pleasant": False,
        }

    def test_habit_serializer_validation(self):
        serializer = HabitSerializer(data=self.habit_data)
        self.assertTrue(serializer.is_valid())

    def test_habit_serializer_validation_fail(self):
        invalid_data = self.habit_data.copy()
        invalid_data["duration"] = 150
        serializer = HabitSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

    def test_user_serializer(self):
        data = {
            "username": "newuser",
            "password": "newpassword123",
            "email": "newuser@example.com",
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "newuser")

    def test_habit_serializer_validate_related_habit(self):
        pleasant_habit = Habit.objects.create(
            user=self.user,
            place="Home",
            time="12:00:00",
            action="Relax",
            duration=30,
            is_pleasant=True,
        )
        data = self.habit_data.copy()
        data["related_habit"] = pleasant_habit.id
        serializer = HabitSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        not_pleasant_habit = Habit.objects.create(
            user=self.user, place="Home", time="12:00:00", action="Work", duration=60
        )
        data["related_habit"] = not_pleasant_habit.id
        serializer = HabitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertIn(
            "Связанная привычка должна быть приятной.",
            str(serializer.errors["non_field_errors"]),
        )

    def test_habit_serializer_validate_frequency(self):
        data = self.habit_data.copy()
        data["frequency"] = 8
        serializer = HabitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("frequency", serializer.errors)


class ViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.force_authenticate(user=self.user)
        self.habit = Habit.objects.create(
            user=self.user,
            place="Home",
            time="12:00:00",
            action="Read a book",
            duration=60,
        )

    def test_set_telegram_chat_id(self):
        url = reverse("set-telegram-chat-id")
        data = {"chat_id": "123456789"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.telegram_chat_id, "123456789")

    def test_public_habit_list(self):
        _ = Habit.objects.create(
            user=self.user,
            place="Park",
            time="18:00:00",
            action="Go for a walk",
            duration=30,
            is_public=True,
        )
        url = reverse("public-habits")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["action"], "Go for a walk")

    def test_habit_viewset_perform_create(self):
        url = reverse("habit-list")
        data = {
            "place": "Office",
            "time": "09:00:00",
            "action": "Check emails",
            "duration": 30,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 2)
        new_habit = Habit.objects.latest("id")
        self.assertEqual(new_habit.user, self.user)


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")

    def test_user_profile_creation(self):
        self.assertIsInstance(self.user.profile, UserProfile)

    def test_habit_str_method(self):
        habit = Habit.objects.create(
            user=self.user,
            place="Home",
            time="12:00:00",
            action="Read a book",
            duration=60,
        )
        self.assertEqual(str(habit), "Read a book at 12:00:00 in Home")

    def test_habit_clean_method(self):
        habit = Habit(
            user=self.user,
            place="Home",
            time="12:00:00",
            action="Read a book",
            duration=60,
            reward="Cookie",
            related_habit=None,
        )
        habit.clean()  # This should not raise any exception

        habit.related_habit = habit  # This should raise a ValidationError
        with self.assertRaises(ValidationError):
            habit.clean()


class HabitModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.habit = Habit.objects.create(
            user=self.user,
            place="Home",
            time="12:00:00",
            action="Read a book",
            duration=60,
        )

    def test_habit_creation(self):
        self.assertTrue(isinstance(self.habit, Habit))
        self.assertEqual(self.habit.__str__(), "Read a book at 12:00:00 in Home")

    def test_habit_validation(self):
        invalid_habit = Habit(
            user=self.user,
            place="Home",
            time="12:00:00",
            action="Invalid habit",
            duration=150,  # Превышает максимальную продолжительность
        )
        with self.assertRaises(ValidationError):
            invalid_habit.full_clean()

    def test_habit_clean_method_with_reward_and_related_habit(self):
        related_habit = Habit.objects.create(
            user=self.user,
            place="Home",
            time="12:00:00",
            action="Relax",
            duration=30,
            is_pleasant=True,
        )
        habit = Habit(
            user=self.user,
            place="Home",
            time="12:00:00",
            action="Work",
            duration=60,
            reward="Cookie",
            related_habit=related_habit,
        )
        with self.assertRaises(ValidationError):
            habit.clean()

    def test_habit_clean_method_with_pleasant_habit_and_reward(self):
        habit = Habit(
            user=self.user,
            place="Home",
            time="12:00:00",
            action="Relax",
            duration=30,
            is_pleasant=True,
            reward="Cookie",
        )
        with self.assertRaises(ValidationError):
            habit.clean()

    def test_habit_clean_method_with_high_frequency(self):
        habit = Habit(
            user=self.user,
            place="Home",
            time="12:00:00",
            action="Work",
            duration=60,
            frequency=8,
        )
        with self.assertRaises(ValidationError):
            habit.clean()


class HabitViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.force_authenticate(user=self.user)
        self.habit = Habit.objects.create(
            user=self.user,
            place="Home",
            time="12:00:00",
            action="Read a book",
            duration=60,
        )

    def test_get_all_habits(self):
        response = self.client.get("/api/habits/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_habit(self):
        data = {
            "place": "Office",
            "time": "09:00:00",
            "action": "Check emails",
            "duration": 30,
        }
        response = self.client.post("/api/habits/", data)
        self.assertEqual(response.status_code, 201)

    def test_update_habit(self):
        data = {
            "place": "Park",
            "time": "18:00:00",
            "action": "Go for a walk",
            "duration": 30,
        }
        response = self.client.put(f"/api/habits/{self.habit.id}/", data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Habit.objects.get(id=self.habit.id).place, "Park")

    def test_delete_habit(self):
        response = self.client.delete(f"/api/habits/{self.habit.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Habit.objects.count(), 0)
