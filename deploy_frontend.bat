@echo off
REM Скрипт для деплоя фронтенда на TimeWeb
REM Перед использованием: заполни переменные ниже реальными данными

setlocal enabledelayedexpansion

REM ========================================
REM НАСТРОЙКИ - ЗАПОЛНИ ЭТИ ДАННЫЕ!
REM ========================================
set SERVER_USER=your_username
set SERVER_HOST=your-server-ip-or-domain
set SERVER_PATH=/var/www/frontend
set SSH_KEY_PATH=C:\Users\%USERNAME%\.ssh\id_rsa
REM ========================================

echo ========================================
echo Деплой фронтенда на сервер TimeWeb
echo ========================================
echo.

REM Переходим в папку front
cd /d "%~dp0front"

echo [1/4] Проверка зависимостей...
if not exist "node_modules\" (
    echo Установка зависимостей...
    call npm install
) else (
    echo Зависимости уже установлены
)
echo.

echo [2/4] Сборка фронтенда...
call npm run build
if errorlevel 1 (
    echo ОШИБКА: Сборка не удалась!
    pause
    exit /b 1
)
echo Сборка завершена успешно!
echo.

echo [3/4] Проверка папки dist...
if not exist "dist\" (
    echo ОШИБКА: Папка dist не найдена после сборки!
    pause
    exit /b 1
)
echo.

echo [4/4] Загрузка на сервер...
echo Подключение к %SERVER_USER%@%SERVER_HOST%...
echo Путь на сервере: %SERVER_PATH%
echo.
echo ВНИМАНИЕ: Если используешь пароль вместо SSH ключа, введи пароль когда попросит.
echo Если используешь SSH ключ, убедись что ключ находится по пути: %SSH_KEY_PATH%
echo.

REM Проверяем наличие scp (обычно доступен через Git Bash или WSL)
where scp >nul 2>nul
if errorlevel 1 (
    echo.
    echo ОШИБКА: Команда scp не найдена!
    echo.
    echo Варианты решения:
    echo 1. Используй Git Bash (обычно устанавливается с Git для Windows)
    echo 2. Используй WinSCP для загрузки файлов вручную
    echo 3. Запакуй папку dist в ZIP и загрузи через файловый менеджер TimeWeb
    echo.
    echo Открой папку dist для ручной загрузки...
    explorer dist
    pause
    exit /b 1
)

REM Используем scp для загрузки (требует SSH доступ)
echo Загрузка файлов...
scp -r dist/* %SERVER_USER%@%SERVER_HOST%:%SERVER_PATH%/

if errorlevel 1 (
    echo.
    echo ВНИМАНИЕ: Загрузка через scp не удалась!
    echo Это нормально, если у тебя нет настроенного SSH доступа.
    echo.
    echo Варианты:
    echo 1. Используй WinSCP для загрузки файлов вручную
    echo 2. Запакуй папку dist в ZIP и загрузи через файловый менеджер TimeWeb
    echo.
    echo Открываю папку dist для ручной загрузки...
    explorer dist
    pause
    exit /b 1
)

echo.
echo ========================================
echo Деплой завершен успешно!
echo ========================================
echo.
echo Следующие шаги на сервере:
echo 1. Установить права: sudo chown -R www-data:www-data %SERVER_PATH%
echo 2. Установить права: sudo chmod -R 755 %SERVER_PATH%
echo 3. Проверить сайт в браузере
echo.
pause

