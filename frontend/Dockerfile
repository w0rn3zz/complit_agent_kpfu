FROM node:20-alpine

WORKDIR /app

# Копирование package файлов
COPY package*.json ./

# Установка зависимостей
RUN npm ci

# Копирование кода
COPY . .

# Сборка
RUN npm run build

# Переменные окружения
ENV NODE_ENV=production

# Порт
EXPOSE 3000

# Запуск
CMD ["npm", "start"]
