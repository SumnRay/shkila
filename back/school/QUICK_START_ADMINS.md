# 🚀 Быстрый старт: Настройка паролей для двух админов

## 📋 Ваша конфигурация

- **Root Admin**: `kazak_jenya@mail.ru`
- **Второй админ**: `nikitasemenenko3@gmail.com`

---

## ⚡ Самый быстрый способ (рекомендуется)

### Шаг 1: Установите переменные окружения

**Windows PowerShell:**
```powershell
$env:ROOT_ADMIN_PASSWORD="ПарольДляПервогоАдмина123!"
$env:ADMIN2_PASSWORD="ПарольДляВторогоАдмина123!"
```

**Windows CMD:**
```cmd
set ROOT_ADMIN_PASSWORD=ПарольДляПервогоАдмина123!
set ADMIN2_PASSWORD=ПарольДляВторогоАдмина123!
```

**Linux/Mac:**
```bash
export ROOT_ADMIN_PASSWORD="ПарольДляПервогоАдмина123!"
export ADMIN2_PASSWORD="ПарольДляВторогоАдмина123!"
```

### Шаг 2: Выполните миграции

```bash
cd back\school
python manage.py migrate
```

**Результат:**
- ✅ Root Admin создан автоматически с паролем из `ROOT_ADMIN_PASSWORD`
- ✅ Второй админ создан автоматически с паролем из `ADMIN2_PASSWORD` (если лимит не исчерпан)

### Шаг 3: Готово! Войдите в систему

```bash
# Проверка через API
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "kazak_jenya@mail.ru", "password": "ПарольДляПервогоАдмина123!"}'
```

---

## 🔄 Если админы уже созданы - изменить пароли

### Вариант 1: Через скрипт (самый простой)

```bash
cd back\school
python manage_admins.py
```

Выберите опцию:
- `3` - изменить пароли для обоих админов сразу

### Вариант 2: Через Django shell

```bash
python manage.py shell
```

```python
from accounts.models import User

# Изменить пароль первого админа
User.objects.get(email="kazak_jenya@mail.ru").set_password("НовыйПароль1")
User.objects.get(email="kazak_jenya@mail.ru").save()

# Изменить пароль второго админа
User.objects.get(email="nikitasemenenko3@gmail.com").set_password("НовыйПароль2")
User.objects.get(email="nikitasemenenko3@gmail.com").save()
```

---

## 📝 Создание второго админа вручную (если автоматически не создался)

Если второй админ не создался автоматически, используйте API:

```bash
curl -X POST http://localhost:8000/api/auth/admin-login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nikitasemenenko3@gmail.com",
    "password": "ПарольПриСоздании123!"
  }'
```

---

## ✅ Проверка что всё работает

```bash
python manage.py shell
```

```python
from accounts.models import User

# Проверка root admin
root = User.objects.get(email="kazak_jenya@mail.ru")
print(f"Root: {root.email}, role: {root.role}, superuser: {root.is_superuser}")

# Проверка второго админа
admin2 = User.objects.get(email="nikitasemenenko3@gmail.com")
print(f"Admin2: {admin2.email}, role: {admin2.role}, superuser: {admin2.is_superuser}")
```

---

## 🔐 Управление паролями в будущем

### Изменить пароль одного админа:
```bash
python manage_admins.py
# Выберите опцию 1 или 2
```

### Изменить пароли обоих сразу:
```bash
python manage_admins.py
# Выберите опцию 3
```

### Показать список админов:
```bash
python manage_admins.py
# Выберите опцию 5
```

---

## 📚 Подробная документация

См. файл `ADMIN_PASSWORDS_GUIDE.md` для полной документации по всем способам управления паролями.

