# Используем базовый образ Python
FROM python:3.9-slim

# Устанавливаем зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем код приложения
COPY . /app

# Устанавливаем рабочую директорию
WORKDIR /app

# Запускаем Telegram бота
CMD ["python", "bot.py"]