@echo off
REM Скрипт для синхронизации проекта с GitHub (ветка main)
REM Этот скрипт добавит новые файлы и синхронизирует с main веткой

echo ========================================
echo Синхронизация проекта с GitHub
echo ========================================
echo.

echo [1/5] Добавление новых файлов...
git add deploy/ deploy_frontend.md deploy_frontend.bat
if errorlevel 1 (
    echo ОШИБКА при добавлении файлов
    pause
    exit /b 1
)
echo ✅ Файлы добавлены
echo.

echo [2/5] Проверка статуса...
git status
echo.
pause

echo [3/5] Создание коммита...
set /p COMMIT_MSG="Введи сообщение коммита (или нажми Enter для значения по умолчанию): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Добавлены скрипты и инструкции для деплоя фронтенда
git commit -m "%COMMIT_MSG%"
if errorlevel 1 (
    echo Предупреждение: Коммит не создан (возможно, нечего коммитить)
)
echo.

echo [4/5] Переключение на ветку main...
git checkout main
if errorlevel 1 (
    echo ОШИБКА при переключении на main
    pause
    exit /b 1
)
echo.

echo [5/5] Обновление main из GitHub...
git pull origin main
if errorlevel 1 (
    echo Предупреждение: git pull не удался (возможно, нужна настройка)
)
echo.

echo [6/6] Слияние изменений из alpha3 в main...
echo ВНИМАНИЕ: Если будут конфликты, разреши их вручную
git merge alpha3
if errorlevel 1 (
    echo ⚠️  Есть конфликты! Разреши их вручную, затем выполни:
    echo    git add .
    echo    git commit -m "Разрешены конфликты"
)
echo.

echo [7/7] Отправка изменений в GitHub...
git push origin main
if errorlevel 1 (
    echo ОШИБКА при отправке в GitHub
    pause
    exit /b 1
)
echo.

echo ========================================
echo ✅ Синхронизация завершена!
echo ========================================
echo.
echo Теперь на сервере выполни:
echo   cd /var/www/shkila
echo   git pull origin main
echo.
pause

