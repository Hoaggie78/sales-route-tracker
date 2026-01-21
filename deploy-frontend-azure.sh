#!/bin/bash
# Deploy Frontend to Azure Static Web Apps or App Service
# Usage: ./deploy-frontend-azure.sh

set -e

echo "🚀 Deploying Sales Route Tracker Frontend to Azure"
echo "=================================================="
echo ""

# Configuration
read -p "📝 Enter app name (e.g., sales-route-tracker): " APP_NAME
read -p "📝 Enter resource group name: " RESOURCE_GROUP
read -p "📝 Enter backend URL (e.g., https://sales-route-tracker-backend.azurewebsites.net): " BACKEND_URL

FRONTEND_APP="${APP_NAME}-frontend"

# Check if logged in
az account show > /dev/null || { echo "❌ Not logged into Azure. Run: az login"; exit 1; }

echo "🔨 Building frontend..."
cd frontend

# Install dependencies
npm install

# Build with correct API URL
VITE_API_URL=$BACKEND_URL npm run build

echo "📤 Deploying to Azure..."
# Check if Static Web App exists
if az staticwebapp show --name $FRONTEND_APP --resource-group $RESOURCE_GROUP &>/dev/null; then
    echo "Found Static Web App, deploying..."
    
    # Deploy to Static Web App
    az staticwebapp upload \
      --name $FRONTEND_APP \
      --resource-group $RESOURCE_GROUP \
      --source-path ./dist \
      --dry-run false
else
    echo "Static Web App not found. Creating..."
    
    # Create App Service Plan for frontend
    PLAN_NAME="${APP_NAME}-frontend-plan"
    az appservice plan create \
      --name $PLAN_NAME \
      --resource-group $RESOURCE_GROUP \
      --sku B1 \
      --is-linux
    
    # Create App Service for frontend (Node.js)
    az webapp create \
      --resource-group $RESOURCE_GROUP \
      --plan $PLAN_NAME \
      --name $FRONTEND_APP \
      --runtime "NODE|20-lts"
    
    # Deploy built files
    zip -r frontend-dist.zip dist
    az webapp deployment source config-zip \
      --resource-group $RESOURCE_GROUP \
      --name $FRONTEND_APP \
      --src frontend-dist.zip
    rm frontend-dist.zip
fi

cd ..

echo ""
echo "✅ Frontend deployed successfully!"
echo "   URL: https://${FRONTEND_APP}.azurewebsites.net or https://${FRONTEND_APP}.azurestaticapps.net"
echo ""
echo "📋 To view logs:"
echo "   az webapp log tail --name $FRONTEND_APP --resource-group $RESOURCE_GROUP"
echo ""
