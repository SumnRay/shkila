# Очистка сервера от лишних изменений

## Проблема:
На сервере видны изменения в `__pycache__` файлах (кэш Python), которые не должны быть в git.

## Решение:

Выполни на сервере:

```bash
cd /var/www/shkila

# Отменить все изменения в отслеживаемых файлах (включая __pycache__)
git restore .

# Удалить странные файлы, которые случайно появились
rm -f back/school/tall
rm -f "back/school/ystemctl reload nginx"

# Очистить все __pycache__ директории (опционально, но рекомендуется)
find back/school -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true

# Проверить статус - должен быть чистым
git status
```

## Если package-lock.json изменился:

Если `package-lock.json` изменился легитимно (после npm install), можно либо:
1. Игнорировать изменения: `git restore front/package-lock.json`
2. Или обновить его локально и закоммитить

## Результат:
После выполнения этих команд `git status` должен показать:
```
On branch alpha3
Your branch is up to date with 'origin/alpha3'.

nothing to commit, working tree clean
```

