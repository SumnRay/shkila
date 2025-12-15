# Инструкция по пересборке фронта на сервере

## Проблема
На сервере используется старая сборка фронта с путями `/api/...`, что приводит к дублированию: `/api/api/...`

## Решение

### 1. На сервере подключись по SSH
```bash
ssh root@5.129.223.109
```

### 2. Перейди в директорию фронта
```bash
cd /var/www/shkila/front
```

### 3. Обнови код из репозитория (если нужно)
```bash
git pull
```

### 4. Пересобери фронт
```bash
npm run build
```

### 5. Обнови файлы для nginx
```bash
rm -rf /var/www/frontend/*
cp -r dist/* /var/www/frontend/
systemctl reload nginx
```

### 6. Проверь в браузере
Открой `http://5.129.223.109` и проверь в DevTools → Network, что запросы идут на `/api/...` (один раз), а не `/api/api/...`

## Проверка

После пересборки все запросы должны выглядеть так:
- ✅ `GET /api/auth/me/`
- ✅ `GET /api/admin/lessons/`
- ✅ `GET /api/applicant/courses/public/`
- ✅ `GET /api/applicant/balance/`

А НЕ так:
- ❌ `GET /api/api/auth/me/`
- ❌ `GET /api/api/admin/lessons/`
- ❌ `GET /api/api/applicant/courses/public/`
