# Используем базовый образ Python
FROM python:3.9-slim

# Устанавливаем зависимости
COPY requirements.txt /app/requirements.txt
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/* 
run pip install psycopg2-binary

# RUN apt-get -y install libpq-dev gcc \ && pip install psycopg2

RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем код приложения
COPY . /app

# Устанавливаем рабочую директорию
WORKDIR /app

# Запускаем Flask сервер
CMD ["python", "app.py"]