@echo off
echo Starting Django Backend...
cd backend
call venv\Scripts\activate
python manage.py runserver
pause