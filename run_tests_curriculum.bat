@echo off
cd /d "%~dp0"
call ..\venv\Scripts\activate.bat

echo Running Curriculum Tests...
python manage.py test curriculum --verbosity=2

echo.
echo Coverage Report:
python -m coverage run --source=curriculum manage.py test curriculum
python -m coverage report -m

pause