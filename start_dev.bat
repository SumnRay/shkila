@echo off
set ROOT=%~dp0
if exist "%ROOT%venv312\Scripts\python.exe" (
    start "Backend" cmd /k "cd /d %ROOT%back\school && %ROOT%venv312\Scripts\python.exe manage.py runserver"
) else if exist "%ROOT%venv\Scripts\python.exe" (
    start "Backend" cmd /k "cd /d %ROOT%back\school && %ROOT%venv\Scripts\python.exe manage.py runserver"
) else if exist "%ROOT%.venv\Scripts\python.exe" (
    start "Backend" cmd /k "cd /d %ROOT%back\school && %ROOT%.venv\Scripts\python.exe manage.py runserver"
) else if exist "%ROOT%back\venv312\Scripts\python.exe" (
    start "Backend" cmd /k "cd /d %ROOT%back\school && %ROOT%back\venv312\Scripts\python.exe manage.py runserver"
) else if exist "%ROOT%back\venv\Scripts\python.exe" (
    start "Backend" cmd /k "cd /d %ROOT%back\school && %ROOT%back\venv\Scripts\python.exe manage.py runserver"
) else if exist "%ROOT%back\.venv\Scripts\python.exe" (
    start "Backend" cmd /k "cd /d %ROOT%back\school && %ROOT%back\.venv\Scripts\python.exe manage.py runserver"
) else (
    start "Backend" cmd /k "cd /d %ROOT%back\school && python manage.py runserver"
)
start "Frontend" cmd /k "cd /d %ROOT%front && npm run dev"
