#!/bin/bash
# Quick start script for Smart Intel Platform

echo "🚀 Starting Smart Intel Platform..."
echo ""

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  docker-compose not found, trying 'docker compose'..."
    if ! docker compose version &> /dev/null; then
        echo "❌ Docker Compose is not available"
        exit 1
    fi
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo "✅ Docker environment verified"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env created. Update with your credentials if needed."
fi

echo ""
echo "🔨 Building Docker images..."
$COMPOSE_CMD build

echo ""
echo "🐳 Starting services..."
$COMPOSE_CMD up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check service status
echo ""
echo "📊 Service Status:"
$COMPOSE_CMD ps

echo ""
echo "✅ Smart Intel Platform is running!"
echo ""
echo "📋 Available Services:"
echo "   - Crawler: Running in background (check logs with: docker-compose logs crawler)"
echo "   - Database: localhost:5432"
echo "   - Processor: Running in background"
echo "   - UI Dashboard: http://localhost:8501"
echo ""
echo "🛑 To stop services: docker-compose down"
echo "📖 To view logs: docker-compose logs -f [service-name]"
echo ""
