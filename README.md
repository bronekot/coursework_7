# Habits Tracker

Habits Tracker - это приложение для отслеживания и формирования полезных привычек, разработанное с использованием Django и Django Rest Framework.

## Особенности

- Создание и отслеживание ежедневных привычек
- Интеграция с Telegram для отправки напоминаний
- API с JWT аутентификацией
- Celery для асинхронных задач и периодических напоминаний
- Автоматическая генерация документации API с использованием drf-spectacular
- Управление зависимостями с помощью Poetry

## Требования

- Python 3.12+
- PostgreSQL
- Redis (для Celery)
- Poetry

## Установка

1. Клонируйте репозиторий:

   ```
   git clone https://github.com/your_username/habits-tracker.git
   cd habits-tracker
   ```
2. Установите зависимости проекта с помощью Poetry:

   ```
   poetry install
   ```
3. Активируйте виртуальное окружение:

   ```
   poetry shell
   ```
4. Создайте файл `.env` в корневой директории проекта и добавьте необходимые переменные окружения:

   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   REDIS_URL=redis://localhost:6379
   ```
5. Примените миграции:

   ```
   python manage.py migrate
   ```
6. Создайте суперпользователя:

   ```
   python manage.py createsuperuser
   ```

## Запуск

1. Запустите Redis (если не запущен):

   ```
   redis-server
   ```
2. В отдельном терминале запустите Celery worker:

   ```
   celery -A config worker -l info
   ```
3. В другом терминале запустите Celery beat:

   ```
   celery -A config beat -l info
   ```
4. Запустите сервер разработки Django:

   ```
   python manage.py runserver
   ```
5. Откройте браузер и перейдите по адресу http://localhost:8000/admin/ для доступа к панели администратора.

## Использование API

Полная документация API доступна через Swagger UI и ReDoc:

- Swagger UI: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`

Эти интерфейсы предоставляют подробную информацию о всех доступных эндпоинтах, их параметрах, ожидаемых ответах и примерах использования.

Основные шаги для начала работы с API:

1. Зарегистрируйтесь:

   ```
   POST /api/register/
   {
     "username": "ваше_имя_пользователя",
     "password": "ваш_пароль",
     "email": "ваш@email.com"
   }
   ```
2. Получите токен доступа:

   ```
   POST /api/token/
   {
     "username": "ваше_имя_пользователя",
     "password": "ваш_пароль"
   }
   ```
3. Используйте полученный токен для аутентификации запросов, добавляя заголовок:

   ```
   Authorization: Bearer <ваш_токен_доступа>
   ```
4. Теперь вы можете использовать все эндпоинты API, описанные в документации Swagger UI или ReDoc.

## Структура проекта

```
habits-tracker/
│
├── config/             # Основные настройки проекта
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
│
├── habits/             # Основное приложение
│   ├── models.py       # Модели данных
│   ├── serializers.py  # Сериализаторы для API
│   ├── views.py        # Представления API
│   ├── tasks.py        # Задачи Celery
│   └── signals.py      # Сигналы Django
│
├── tests/              # Тесты
│
├── manage.py           # Скрипт управления Django
├── pyproject.toml      # Конфигурация Poetry и зависимости проекта
└── README.md           # Этот файл
```

## Тестирование

Для запуска тестов используйте команду:

```
python manage.py test
```
