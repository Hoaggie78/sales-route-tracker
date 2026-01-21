#!/bin/bash

echo "🚀 Sales Route Tracker - Quick Start Script"
echo "==========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo ""
    echo "Creating .env from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "📝 Please edit the .env file with your configuration:"
    echo "   1. Add your Microsoft Azure credentials (Client ID, Client Secret)"
    echo "   2. Set your OneDrive file path"
    echo "   3. Generate a secure SECRET_KEY using: openssl rand -hex 32"
    echo ""
    echo "After configuring .env, run this script again."
    exit 0
fi

echo "✅ .env file found"
echo ""

# Check if required environment variables are set
source .env

if [ "$MICROSOFT_CLIENT_ID" = "your_client_id_here" ] || [ -z "$MICROSOFT_CLIENT_ID" ]; then
    echo "❌ MICROSOFT_CLIENT_ID is not configured in .env"
    echo "   Please set your Azure App Client ID"
    exit 1
fi

if [ "$MICROSOFT_CLIENT_SECRET" = "your_client_secret_here" ] || [ -z "$MICROSOFT_CLIENT_SECRET" ]; then
    echo "❌ MICROSOFT_CLIENT_SECRET is not configured in .env"
    echo "   Please set your Azure App Client Secret"
    exit 1
fi

if [ "$ONEDRIVE_FILE_PATH" = "/your/file/path/here.xlsx" ] || [ -z "$ONEDRIVE_FILE_PATH" ]; then
    echo "❌ ONEDRIVE_FILE_PATH is not configured in .env"
    echo "   Please set the path to your Excel file in OneDrive"
    exit 1
fi

if [ "$SECRET_KEY" = "your_very_secure_secret_key_here" ] || [ -z "$SECRET_KEY" ]; then
    echo "❌ SECRET_KEY is not configured in .env"
    echo "   Generate one using: openssl rand -hex 32"
    exit 1
fi

echo "✅ All required environment variables are configured"
echo ""

echo "🔨 Building and starting services..."
echo ""

# Build and start services
docker-compose up -d --build

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ All services are running!"
    echo ""
    echo "📱 Access the application at:"
    echo "   Frontend: http://localhost:5173"
    echo "   Backend API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "📖 Next steps:"
    echo "   1. Open http://localhost:5173 in your browser"
    echo "   2. Click 'Connect to OneDrive'"
    echo "   3. Sign in with your Microsoft account"
    echo "   4. Click 'Sync from OneDrive' to import your route plan"
    echo "   5. Start tracking your visits!"
    echo ""
    echo "📝 View logs: docker-compose logs -f"
    echo "🛑 Stop services: docker-compose down"
else
    echo ""
    echo "❌ Some services failed to start"
    echo "   View logs: docker-compose logs"
    exit 1
fi
