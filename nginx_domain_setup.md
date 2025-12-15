# Настройка Nginx под домен

## 🔧 ШАГ 1: Подключись к серверу

```bash
ssh root@5.129.223.109
```

## 🔧 ШАГ 2: Обнови конфиг в репозитории (ЛОКАЛЬНО)

1. Открой `deploy/nginx/shkila.conf` в проекте
2. Замени `YOUR_DOMAIN.ru` на реальный домен (например: `flare-school.ru`)
3. Закоммить и запушь изменения в Git

## 🔧 ШАГ 3: Скопируй конфиг на сервер

```bash
# После git pull на сервере:
cp /var/www/shkila/deploy/nginx/shkila.conf /etc/nginx/sites-available/shkila
```

**ИЛИ** отредактируй напрямую на сервере (временный вариант):

```nginx
server {
    listen 80 default_server;
    server_name твойдомен.ru www.твойдомен.ru;

    root /var/www/frontend;
    index index.html;

    # FRONTEND (Vue)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # BACKEND API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # DJANGO ADMIN
    location /admin/ {
        proxy_pass http://127.0.0.1:8000/admin/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # STATIC FILES
    location /static/ {
        alias /var/www/shkila/back/school/staticfiles/;
    }
}
```

⚠️ **ВАЖНО:** Замени `YOUR_DOMAIN.ru` на реальный домен (например: `flare-school.ru`)

## 🔧 ШАГ 4: Сохрани файл

В nano:
- `Ctrl + O` → Enter (сохранить)
- `Ctrl + X` (выйти)

## 🔧 ШАГ 5: Проверь конфиг

```bash
nginx -t
```

Должно быть:
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

## 🔧 ШАГ 6: Перезагрузи nginx

```bash
systemctl reload nginx
```

## 🔧 ШАГ 7: Проверь что gunicorn работает

```bash
systemctl status shkila
```

Должно быть: `Active: active (running)`

## 🔧 ШАГ 8: Настрой A-запись домена

У регистратора домена (Timeweb, Reg.ru и т.д.):

1. Зайди в управление DNS домена
2. Добавь/измени A-запись:
   - Имя: `@` (или оставь пустым)
   - Тип: `A`
   - Значение: `5.129.223.109`
   - TTL: 3600

3. Добавь A-запись для www:
   - Имя: `www`
   - Тип: `A`
   - Значение: `5.129.223.109`
   - TTL: 3600

## 🔧 ШАГ 9: Обнови ALLOWED_HOSTS в Django

```bash
nano /var/www/shkila/back/school/.env
```

Найди строку:
```
ALLOWED_HOSTS=...
```

Измени на (подставь свой домен):
```
ALLOWED_HOSTS=YOUR_DOMAIN.ru,www.YOUR_DOMAIN.ru,5.129.223.109,localhost,127.0.0.1
```

⚠️ **Или обнови через git pull**, если добавишь `.env` в репозиторий (не рекомендуется из соображений безопасности, лучше оставить `.env` только на сервере)

Сохрани: `Ctrl+O` → Enter → `Ctrl+X`

## 🔧 ШАГ 10: Перезапусти gunicorn

```bash
systemctl restart shkila
```

## ✅ Проверка

Подожди 5-15 минут пока DNS обновится, затем:

1. Открой в браузере: `http://твойдомен.ru`
2. Проверь что фронт открывается
3. Попробуй залогиниться
4. Проверь в DevTools → Network что запросы идут на `/api/...`

## ⚠️ Если домен не открывается

1. Проверь DNS: `nslookup твойдомен.ru` (должен вернуть `5.129.223.109`)
2. Проверь что nginx слушает порт 80: `netstat -tulpn | grep :80`
3. Проверь логи nginx: `tail -f /var/log/nginx/error.log`
