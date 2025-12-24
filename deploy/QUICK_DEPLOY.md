# Быстрый деплой - команды для копирования

## Если сборка уже выполнена (npm run build уже прошел):

Выполни на сервере:
```bash
cd /var/www/shkila/front
sudo cp -r dist/* /var/www/frontend/
sudo chown -R www-data:www-data /var/www/frontend
sudo chmod -R 755 /var/www/frontend
echo "✅ Файлы скопированы!"
```

## Полный процесс деплоя:

### 1. Настройка git pull (один раз):
```bash
cd /var/www/shkila
git config pull.rebase false
```

### 2. Обновление и деплой:
```bash
cd /var/www/shkila
git pull origin alpha3
cd front
npm install  # только если добавились новые зависимости
npm run build
sudo cp -r dist/* /var/www/frontend/
sudo chown -R www-data:www-data /var/www/frontend
sudo chmod -R 755 /var/www/frontend
```

## Использование скрипта (после настройки):

1. Скопировать скрипт на сервер (если еще не скопирован):
```bash
cd /var/www/shkila
git pull origin main  # чтобы получить обновленный скрипт
chmod +x deploy/deploy_frontend.sh
```

2. Настроить git (один раз):
```bash
cd /var/www/shkila
git config pull.rebase false
```

3. Запускать скрипт каждый раз:
```bash
/var/www/shkila/deploy/deploy_frontend.sh
```

