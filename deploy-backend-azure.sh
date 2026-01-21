#!/bin/bash
# Deploy Backend to Azure App Service
# Usage: ./deploy-backend-azure.sh

set -e

echo "🚀 Deploying Sales Route Tracker Backend to Azure"
echo "=================================================="
echo ""

# Configuration
read -p "📝 Enter app name (e.g., sales-route-tracker): " APP_NAME
read -p "📝 Enter resource group name: " RESOURCE_GROUP
read -p "📝 Enter container registry name: " REGISTRY_NAME

BACKEND_APP="${APP_NAME}-backend"
REGISTRY_URL="${REGISTRY_NAME}.azurecr.io"
IMAGE_NAME="sales-route-tracker-backend"

# Check if logged in
az account show > /dev/null || { echo "❌ Not logged into Azure. Run: az login"; exit 1; }

echo "🔨 Building Docker image..."
# Build Docker image
docker build -t ${REGISTRY_URL}/${IMAGE_NAME}:latest ./backend

echo "🔑 Logging into container registry..."
# Get ACR credentials and login
az acr login --name $REGISTRY_NAME

echo "📤 Pushing image to registry..."
# Push to registry
docker push ${REGISTRY_URL}/${IMAGE_NAME}:latest

echo "⚙️  Configuring App Service..."
# Get registry credentials for App Service
REGISTRY_USERNAME=$(az acr credential show --name $REGISTRY_NAME --query username -o tsv)
REGISTRY_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --query 'passwords[0].value' -o tsv)

# Update App Service to use container
az webapp config container set \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --docker-custom-image-name ${REGISTRY_URL}/${IMAGE_NAME}:latest \
  --docker-registry-server-url https://${REGISTRY_URL} \
  --docker-registry-server-user $REGISTRY_USERNAME \
  --docker-registry-server-password "$REGISTRY_PASSWORD"

echo ""
echo "✅ Backend deployed successfully!"
echo "   URL: https://${BACKEND_APP}.azurewebsites.net"
echo "   Health check: https://${BACKEND_APP}.azurewebsites.net/health"
echo ""
echo "📋 To view logs:"
echo "   az webapp log tail --name $BACKEND_APP --resource-group $RESOURCE_GROUP"
echo ""
