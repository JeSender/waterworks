@echo off
echo ========================================
echo  Balilihan Waterworks - Local Testing
echo ========================================
echo.

REM Activate virtual environment
echo [1/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Virtual environment not found!
    echo Please create one with: python -m venv venv
    pause
    exit /b 1
)
echo ✓ Virtual environment activated
echo.

REM Check if dependencies are installed
echo [2/4] Checking dependencies...
python -c "import django" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies!
        pause
        exit /b 1
    )
)
echo ✓ Dependencies installed
echo.

REM Apply migrations
echo [3/4] Applying database migrations...
python manage.py migrate --noinput
if errorlevel 1 (
    echo ERROR: Migration failed!
    pause
    exit /b 1
)
echo ✓ Migrations applied
echo.

REM Collect static files
echo [4/4] Collecting static files...
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo WARNING: Static files collection failed (non-critical)
)
echo ✓ Static files collected
echo.

REM Show access information
echo ========================================
echo  Server Starting...
echo ========================================
echo.
echo 📱 Access the application at:
echo    ► http://127.0.0.1:8000/home/
echo    ► http://localhost:8000/home/
echo.
echo 🔐 Admin Panel:
echo    ► http://127.0.0.1:8000/admin/
echo.
echo 💡 To stop the server: Press CTRL+C
echo ========================================
echo.

REM Start Django development server
python manage.py runserver

pause
