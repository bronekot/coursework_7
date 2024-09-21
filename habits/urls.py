from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .auth import RegisterView
from .views import HabitViewSet, PublicHabitListView, set_telegram_chat_id

router = DefaultRouter()
router.register(r"habits", HabitViewSet, basename="habit")

urlpatterns = [
    path("", include(router.urls)),
    path("public-habits/", PublicHabitListView.as_view(), name="public-habits"),
    path("register/", RegisterView.as_view(), name="register"),
    path("set-telegram-chat-id/", set_telegram_chat_id, name="set-telegram-chat-id"),
]
