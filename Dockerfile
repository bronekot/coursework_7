FROM python:3.12-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

COPY . /app/

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]