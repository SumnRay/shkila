# Очистка сервера от лишних изменений

## Проблема:
На сервере видны изменения в `__pycache__` файлах (кэш Python), которые не должны быть в git.

## Решение:

Выполни на сервере:

```bash
cd /var/www/shkila

# Удалить странные файлы, которые случайно появились
rm -f back/school/tall
rm -f "back/school/ystemctl reload nginx"

# Восстановить удаленные __pycache__ файлы (чтобы git не видел их как deleted)
# Это нормально - они будут в .gitignore и не будут мешать
git restore .

# Если после этого все еще видишь deleted файлы, просто игнорируй их:
# Эти файлы должны быть удалены из git (лучше сделать это локально в отдельном коммите)
# Пока просто проверь что нет других изменений
git status --ignored
```

## Если видишь deleted файлы __pycache__:

Это означает, что эти файлы когда-то были добавлены в git (ошибка). Нужно удалить их из репозитория локально:

**Локально (на твоем компьютере):**
```bash
cd c:\shkila
git rm -r --cached back/school/**/__pycache__
git commit -m "Удалены __pycache__ файлы из репозитория (должны быть в .gitignore)"
git push origin alpha3
```

**Затем на сервере:**
```bash
cd /var/www/shkila
git pull origin alpha3
git status  # Теперь должно быть чисто
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

