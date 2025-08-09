# Используем официальный образ Python
FROM python:3.10-slim
# Устанавливаем зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
# Создаем рабочую директорию
WORKDIR /app
# Копируем зависимости
COPY requirements.txt .
# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt
# Копируем исходный код
COPY . .
# Указываем точку входа
CMD ["python", "main.py"]