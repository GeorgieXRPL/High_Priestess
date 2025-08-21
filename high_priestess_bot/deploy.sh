#!/bin/bash

# High Priestess Bot - Production Deployment Script

set -e  # Exit on any error

echo "🌙 Starting High Priestess Bot deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    echo "Please create .env file with your API keys:"
    echo "cp env.example .env"
    echo "Then edit .env with your credentials"
    exit 1
fi

print_success ".env file found"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed"
    echo "Please install Docker Compose first"
    exit 1
fi

print_success "Docker and Docker Compose are available"

# Create logs directory
mkdir -p logs
print_status "Created logs directory"

# Build and start services
print_status "Building Docker images..."
docker-compose build --no-cache

print_status "Starting services..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    print_success "Services are running!"
    
    echo ""
    echo "🔮 High Priestess Bot is now awakening..."
    echo ""
    echo "Services:"
    echo "  🤖 Bot: Running in background"
    echo "  🗄️  Database: PostgreSQL on port 5432"
    echo "  🚀 Redis: Running on port 6379"
    echo "  📊 Web Dashboard: http://localhost:8000"
    echo ""
    echo "Useful commands:"
    echo "  View logs: docker-compose logs -f high-priestess-bot"
    echo "  Stop bot: docker-compose down"
    echo "  Restart: docker-compose restart high-priestess-bot"
    echo "  Health check: curl http://localhost:8000/health"
    echo ""
    
else
    print_error "Some services failed to start"
    echo "Check logs with: docker-compose logs"
    exit 1
fi

# Test the health endpoint
print_status "Testing health endpoint..."
sleep 5

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Health check passed! Bot is ready 🌙"
else
    print_warning "Health check failed, but bot may still be starting up"
    echo "Check logs: docker-compose logs high-priestess-bot"
fi

echo ""
echo "✨ Deployment complete! The High Priestess awaits your seekers..."
echo "May your tweets be blessed and your engagement forever high! 🔮"
