#!/bin/bash
# Скрипт для деплоя фронтенда на сервере
# Использование: ./deploy_frontend.sh
# 
# Убедись что:
# 1. Проект клонирован в /var/www/shkila
# 2. У тебя есть права на выполнение npm и sudo

set -e  # Остановить при ошибке

echo "=========================================="
echo "Деплой фронтенда"
echo "=========================================="
echo ""

# Переходим в директорию проекта
cd /var/www/shkila || { echo "ОШИБКА: Директория /var/www/shkila не найдена!"; exit 1; }

echo "[1/5] Обновление кода из GitHub..."
# Настраиваем стратегию слияния (merge) для git pull
git config pull.rebase false
# Обновляем из alpha3 (используется на сервере)
git pull origin alpha3 || {
    echo "⚠️  Предупреждение: Не удалось выполнить git pull, но продолжаем..."
}
echo "✅ Код обновлен"
echo ""

echo "[2/5] Переход в папку front..."
cd front || { echo "ОШИБКА: Папка front не найдена!"; exit 1; }
echo ""

echo "[3/5] Установка зависимостей (если нужно)..."
npm install
echo "✅ Зависимости установлены"
echo ""

echo "[4/5] Сборка фронтенда..."
npm run build
if [ ! -d "dist" ]; then
    echo "ОШИБКА: Папка dist не создана после сборки!"
    exit 1
fi
echo "✅ Сборка завершена"
echo ""

echo "[5/5] Копирование файлов в /var/www/frontend..."
sudo rm -rf /var/www/frontend/*
sudo cp -r dist/* /var/www/frontend/
sudo chown -R www-data:www-data /var/www/frontend
sudo chmod -R 755 /var/www/frontend
echo "✅ Файлы скопированы"
echo ""

echo "=========================================="
echo "✅ Деплой завершен успешно!"
echo "=========================================="
echo ""
echo "Проверь сайт в браузере: https://flare-school.ru"
echo ""

