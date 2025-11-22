# Multi-stage build для уменьшения размера образа
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim as builder

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY pyproject.toml ./

# Установка зависимостей через uv (БЫСТРО!)
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
RUN uv pip install --system --no-cache -e .

# Финальный образ
FROM python:3.11-slim

WORKDIR /app

# Копирование установленных пакетов из builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копирование исходного кода
COPY . .

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

# Запуск приложения
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
