# School Management System

Система управления школой на Django + Vue.js (Vite)

## 📁 Структура проекта

```
repo/
├─ back/
│  └─ school/          # Django backend
│     ├─ manage.py
│     ├─ requirements.txt
│     ├─ .env.example   # Шаблон переменных окружения
│     └─ school/       # Настройки Django
│
├─ front/              # Vue.js frontend (Vite)
│  ├─ package.json
│  ├─ vite.config.js
│  └─ src/
│
├─ requirements.txt    # Python зависимости (корневой)
└─ README.md
```

---

## 🚀 Локальный запуск

### Требования

- Python 3.8+
- Node.js 16+
- MySQL 5.7+ или 8.0+

### Backend (Django)

1. **Создайте виртуальное окружение:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте переменные окружения:**
   ```bash
   cd back/school
   cp .env.example .env
   # Отредактируйте .env и укажите реальные значения
   ```

4. **Настройте базу данных MySQL:**
   - Создайте базу данных
   - Укажите параметры в `.env`

5. **Выполните миграции:**
   ```bash
   python manage.py migrate
   ```

6. **Создайте суперпользователя (опционально):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Запустите сервер:**
   ```bash
   python manage.py runserver
   ```

   Backend будет доступен на `http://127.0.0.1:8000`

### Frontend (Vue.js)

1. **Установите зависимости:**
   ```bash
   cd front
   npm install
   ```

2. **Настройте API URL (опционально):**
   
   Создайте файл `front/.env`:
   ```
   VITE_API_BASE_URL=http://127.0.0.1:8000
   ```
   
   Или оставьте пустым для использования относительного пути `/api` (рекомендуется для продакшена)

3. **Запустите dev-сервер:**
   ```bash
   npm run dev
   ```

   Frontend будет доступен на `http://localhost:5173`

### Быстрый запуск (Windows)

Используйте скрипт `start_dev.bat` в корне проекта.

---

## 🔐 Переменные окружения

### Backend (.env в `back/school/`)

Скопируйте `.env.example` в `.env` и заполните:

```env
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here

# Allowed Hosts (через запятую, без пробелов)
ALLOWED_HOSTS=yourdomain.ru,www.yourdomain.ru,127.0.0.1

# Database
DB_NAME=flare
DB_USER=flare_user
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=3306

# CORS Origins (через запятую, без пробелов)
CORS_ORIGINS=https://yourdomain.ru,http://localhost:5173

# Admin Configuration
ROOT_ADMIN_EMAIL=admin@example.com
ADMIN_SEED_EMAILS=admin@example.com,second@example.com
```

### Frontend (.env в `front/`)

Опционально, для dev-режима:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

В продакшене оставьте пустым — будет использоваться относительный путь `/api`.

---

## 📦 Деплой на сервер

### Требования на сервере

- Python 3.8+
- Node.js 16+
- MySQL 5.7+ или 8.0+
- Nginx
- Gunicorn (установится через requirements.txt)

### Шаги деплоя

1. **Клонируйте репозиторий:**
   ```bash
   git clone <your-repo-url>
   cd <project-name>
   ```

2. **Настройте Backend:**
   ```bash
   cd back/school
   
   # Создайте виртуальное окружение
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   
   # Установите зависимости
   pip install -r ../../requirements.txt
   
   # Создайте .env из шаблона
   cp .env.example .env
   nano .env  # Отредактируйте с реальными значениями
   
   # Выполните миграции
   python manage.py migrate
   
   # Соберите статические файлы
   python manage.py collectstatic --noinput
   ```

3. **Настройте Frontend:**
   ```bash
   cd ../../front
   
   # Установите зависимости
   npm install
   
   # Соберите для продакшена
   npm run build
   ```
   
   Результат будет в `front/dist/`

4. **Настройте Nginx:**
   
   Пример конфигурации `/etc/nginx/sites-available/yourdomain`:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.ru www.yourdomain.ru;
       
       # Frontend (статичные файлы)
       location / {
           root /path/to/project/front/dist;
           try_files $uri $uri/ /index.html;
       }
       
       # Backend API
       location /api {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
       
       # Django Admin
       location /django-admin {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       # Static files
       location /static {
           alias /path/to/project/back/school/staticfiles;
       }
   }
   ```
   
   Активируйте конфигурацию:
   ```bash
   sudo ln -s /etc/nginx/sites-available/yourdomain /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

5. **Запустите Gunicorn:**
   
   Создайте systemd service `/etc/systemd/system/gunicorn.service`:
   ```ini
   [Unit]
   Description=Gunicorn daemon for Django
   After=network.target
   
   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/project/back/school
   ExecStart=/path/to/project/back/school/venv/bin/gunicorn \
       --access-logfile - \
       --workers 3 \
       --bind 127.0.0.1:8000 \
       school.wsgi:application
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   Запустите:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start gunicorn
   sudo systemctl enable gunicorn
   ```

6. **Проверьте статус:**
   ```bash
   sudo systemctl status gunicorn
   sudo systemctl status nginx
   ```

---

## ✅ Контрольный чек-лист перед деплоем

- [ ] `.env` файл создан и заполнен (НЕ коммитится в git)
- [ ] `.env.example` содержит все необходимые переменные
- [ ] `DEBUG=False` в продакшене
- [ ] `SECRET_KEY` установлен и безопасен
- [ ] `ALLOWED_HOSTS` содержит реальные домены
- [ ] База данных настроена и миграции применены
- [ ] `python manage.py collectstatic` выполнен
- [ ] `npm run build` выполнен для фронтенда
- [ ] Nginx настроен и проксирует `/api` на Gunicorn
- [ ] Gunicorn запущен и работает
- [ ] Проверено, что нет секретов в коде (используйте `grep -r "password" --include="*.py"`)

---

## 🔍 Полезные команды

### Backend

```bash
# Проверка настроек Django
python manage.py check

# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Сбор статических файлов
python manage.py collectstatic

# Создание суперпользователя
python manage.py createsuperuser

# Django shell
python manage.py shell
```

### Frontend

```bash
# Dev-сервер
npm run dev

# Сборка для продакшена
npm run build

# Превью продакшен-сборки
npm run preview
```

---

## 📝 API Endpoints

- `/api/auth/login/` - Вход
- `/api/auth/register/` - Регистрация
- `/api/auth/me/` - Информация о текущем пользователе
- `/api/admin/...` - API для админов
- `/api/manager/...` - API для менеджеров
- `/api/teacher/...` - API для учителей
- `/api/student/...` - API для учеников
- `/api/applicant/...` - API для абитуриентов
- `/django-admin/` - Django Admin панель

---

## 🛠 Технологии

- **Backend:** Django 4.2, Django REST Framework, PyMySQL
- **Frontend:** Vue.js 3, Vite, Pinia, Vue Router
- **Database:** MySQL
- **Authentication:** JWT (djangorestframework-simplejwt)

---

## 📄 Лицензия

[Укажите лицензию]

---

## 👥 Авторы

[Укажите авторов]
