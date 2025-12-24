# Синхронизация проекта с GitHub

## ⚠️ Важно: База данных будет сохранена!

- База данных использует MySQL (не SQLite), она на сервере и НЕ затрагивается
- `.env` файлы в `.gitignore`, они НЕ попадут в репозиторий
- `db.sqlite3` тоже в `.gitignore` (если бы использовался)

## Процесс синхронизации:

### Синхронизация через ветку alpha3 (используется на сервере) ✅

**1. Добавить новые файлы в git:**
```bash
git add deploy/ deploy_frontend.md deploy_frontend.bat sync_with_github.md sync_to_main.bat
```

**2. Закоммитить изменения:**
```bash
git commit -m "Добавлены скрипты и инструкции для деплоя фронтенда"
```

**3. Запушить в alpha3:**
```bash
git push origin alpha3
```

**4. На сервере обновить:**
```bash
cd /var/www/shkila
git config pull.rebase false  # Настроить один раз
git checkout alpha3  # Убедиться что на правильной ветке
git pull origin alpha3
```

## Быстрая команда для синхронизации (после первого раза):

**Локально:**
```bash
git add .
git commit -m "Описание изменений"
git push origin alpha3
```

**На сервере:**
```bash
cd /var/www/shkila
git pull origin alpha3
```

## Проверка что база данных не затронута:

База данных MySQL на сервере использует настройки из `.env` файла:
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

Файл `.env` в `.gitignore`, поэтому он:
- ✅ НЕ попадет в репозиторий
- ✅ НЕ будет перезаписан при git pull
- ✅ База данных останется нетронутой

