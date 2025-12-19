FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем проект
COPY . .

# Создаем необходимые директории
RUN mkdir -p /app/static /app/media /app/celery_data

# Меняем права на созданные директории
RUN chmod -R 755 /app/static /app/media /app/celery_data

# Создаем пользователя с UID 1000 (обычно это первый пользователь в системе)
RUN useradd -m -u 1000 -s /bin/bash appuser

# Меняем владельца
RUN chown -R appuser:appuser /app

# Переключаемся на пользователя
USER appuser

EXPOSE 8000
