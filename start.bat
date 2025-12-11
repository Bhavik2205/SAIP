@echo off
REM Quick start script for Smart Intel Platform on Windows

echo 🚀 Starting Smart Intel Platform...
echo.

REM Check if Docker is running
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  docker-compose not found, trying 'docker compose'...
    docker compose version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Docker Compose is not available
        pause
        exit /b 1
    )
    set COMPOSE_CMD=docker compose
) else (
    set COMPOSE_CMD=docker-compose
)

echo ✅ Docker environment verified
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env from .env.example...
    copy .env.example .env
    echo ✅ .env created. Update with your credentials if needed.
)

echo.
echo 🔨 Building Docker images...
call %COMPOSE_CMD% build

echo.
echo 🐳 Starting services...
call %COMPOSE_CMD% up -d

echo.
echo ⏳ Waiting for services to be ready...
timeout /t 5 /nobreak

REM Check service status
echo.
echo 📊 Service Status:
call %COMPOSE_CMD% ps

echo.
echo ✅ Smart Intel Platform is running!
echo.
echo 📋 Available Services:
echo    - Crawler: Running in background (check logs with: docker-compose logs crawler)
echo    - Database: localhost:5432
echo    - Processor: Running in background
echo    - UI Dashboard: http://localhost:8501
echo.
echo 🛑 To stop services: docker-compose down
echo 📖 To view logs: docker-compose logs -f [service-name]
echo.
pause
