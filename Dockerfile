FROM python:3.12-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

# Установка Poetry
RUN pip install --no-cache-dir poetry

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock* /app/

# Установка зависимостей проекта
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Копирование проекта
COPY . /app/

# Запуск команды по умолчанию
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]