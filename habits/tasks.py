import telegram
from celery import shared_task
from django.conf import settings


@shared_task
def send_telegram_notification(chat_id, message):
    bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=chat_id, text=message)


@shared_task
def send_habit_reminders():
    from django.utils import timezone

    from .models import Habit, UserProfile

    current_time = timezone.now().time()
    habits = Habit.objects.filter(
        time__hour=current_time.hour, time__minute=current_time.minute
    )
    for habit in habits:
        profile = UserProfile.objects.filter(user=habit.user).first()
        if profile and profile.telegram_chat_id:
            send_telegram_notification.delay(
                profile.telegram_chat_id,
                f"Напоминание: Время для привычки '{habit.action}'",
            )
