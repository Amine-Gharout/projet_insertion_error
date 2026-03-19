@echo off
cd /d "%~dp0"
call ..\venv\Scripts\activate.bat

echo Running Periode Tests...
python manage.py test periode --verbosity=2

echo.
echo Coverage Report:
python -m coverage run --source=periode manage.py test periode
python -m coverage report -m

pause