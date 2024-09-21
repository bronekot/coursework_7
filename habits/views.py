from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Habit, UserProfile
from .serializers import HabitSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Пользовательское разрешение, позволяющее только владельцам объекта редактировать его.

    Неаутентифицированные пользователи могут только читать.
    Аутентифицированные пользователи могут читать все, но редактировать только свои объекты.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем GET, HEAD или OPTIONS запросы
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешаем изменение только владельцу привычки
        return obj.user == request.user


@extend_schema(
    description="Установка Telegram chat ID для пользователя",
    request={"application/json": {"chat_id": "string"}},
    responses={
        200: {"description": "Telegram chat ID успешно установлен"},
        400: {"description": "Отсутствует chat_id в запросе"},
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def set_telegram_chat_id(request):
    """
    Устанавливает Telegram chat ID для текущего пользователя.

    Требует аутентификации.
    """
    chat_id = request.data.get("chat_id")
    if chat_id:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.telegram_chat_id = chat_id
        profile.save()
        return Response(
            {"status": "telegram chat ID установлен"}, status=status.HTTP_200_OK
        )
    return Response(
        {"error": "Пожалуйста, предоставьте chat_id"},
        status=status.HTTP_400_BAD_REQUEST,
    )


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user).order_by("id")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="Список привычек",
        description="Возвращает список привычек текущего пользователя.",
        parameters=[
            OpenApiParameter(
                name="page", description="Номер страницы", required=False, type=int
            ),
            OpenApiParameter(
                name="page_size",
                description="Количество элементов на странице",
                required=False,
                type=int,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        """
        Возвращает список привычек текущего пользователя.
        Поддерживает пагинацию.
        """
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Создание привычки",
        description="Создает новую привычку для текущего пользователя.",
    )
    def create(self, request, *args, **kwargs):
        """
        Создает новую привычку для текущего пользователя.
        """
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Детали привычки",
        description="Возвращает детальную информацию о конкретной привычке.",
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Возвращает детальную информацию о конкретной привычке.
        """
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Полное обновление привычки",
        description="Полностью обновляет информацию о конкретной привычке.",
    )
    def update(self, request, *args, **kwargs):
        """
        Полностью обновляет информацию о конкретной привычке.
        """
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Частичное обновление привычки",
        description="Частично обновляет информацию о конкретной привычке.",
    )
    def partial_update(self, request, *args, **kwargs):
        """
        Частично обновляет информацию о конкретной привычке.
        """
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Удаление привычки", description="Удаляет конкретную привычку."
    )
    def destroy(self, request, *args, **kwargs):
        """
        Удаляет конкретную привычку.
        """
        return super().destroy(request, *args, **kwargs)


class PublicHabitListView(generics.ListAPIView):
    """
    API endpoint для просмотра публичных привычек.

    Не требует аутентификации.
    """

    queryset = Habit.objects.filter(is_public=True)
    serializer_class = HabitSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="page", description="Номер страницы", required=False, type=int
            ),
            OpenApiParameter(
                name="page_size",
                description="Количество элементов на странице",
                required=False,
                type=int,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Возвращает список публичных привычек.

        Поддерживает пагинацию.
        """
        return super().get(request, *args, **kwargs)
