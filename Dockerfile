# Используем базовый образ Python
FROM python:3.9-slim-buster

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта
COPY . .

# Устанавливаем переменную окружения (замените на свой токен)
ENV BOT_TOKEN="YOUR_BOT_TOKEN"

# Команда для запуска бота
CMD ["python", "bot.py"]