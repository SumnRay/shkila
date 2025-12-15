# 🚀 Быстрая инструкция: Деплой Nginx конфига

## На локальной машине:

1. **Открой** `deploy/nginx/shkila.conf`
2. **Замени** `YOUR_DOMAIN.ru` на свой домен (например: `flare-school.ru`)
3. **Закоммить и запушь:**
   ```bash
   git add deploy/nginx/shkila.conf
   git commit -m "Update nginx config with domain"
   git push origin alpha3
   ```

## На сервере:

```bash
# 1. Подключись к серверу
ssh root@5.129.223.109

# 2. Перейди в директорию проекта
cd /var/www/shkila

# 3. Обнови код из Git
git pull origin alpha3

# 4. Скопируй конфиг
cp deploy/nginx/shkila.conf /etc/nginx/sites-available/shkila

# 5. Проверь синтаксис
nginx -t

# 6. Перезагрузи nginx
systemctl reload nginx
```

## Обнови ALLOWED_HOSTS

```bash
nano /var/www/shkila/back/school/.env
```

Измени строку `ALLOWED_HOSTS` (замени `YOUR_DOMAIN.ru` на реальный домен):

```
ALLOWED_HOSTS=YOUR_DOMAIN.ru,www.YOUR_DOMAIN.ru,5.129.223.109,localhost,127.0.0.1
```

Перезапусти Gunicorn:

```bash
systemctl restart shkila
```

## Настрой DNS у регистратора

- A-запись `@` → `5.129.223.109`
- A-запись `www` → `5.129.223.109`

Подожди 5-15 минут и проверь: `http://YOUR_DOMAIN.ru`
