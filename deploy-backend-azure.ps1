# Azure Deployment - Backend Deployment Script (PowerShell)
# Usage: .\deploy-backend-azure.ps1

Write-Host "🚀 Deploying Sales Route Tracker Backend to Azure" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$APP_NAME = Read-Host "📝 Enter app name (e.g., sales-route-tracker)"
$RESOURCE_GROUP = Read-Host "📝 Enter resource group name"
$REGISTRY_NAME = Read-Host "📝 Enter container registry name"

$BACKEND_APP = "$APP_NAME-backend"
$REGISTRY_URL = "$REGISTRY_NAME.azurecr.io"
$IMAGE_NAME = "sales-route-tracker-backend"

# Check if logged in
try {
    az account show | Out-Null
} catch {
    Write-Host "❌ Not logged into Azure. Run: az login" -ForegroundColor Red
    exit 1
}

Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
docker build -t "$REGISTRY_URL/$IMAGE_NAME:latest" ./backend

Write-Host "🔑 Logging into container registry..." -ForegroundColor Yellow
az acr login --name $REGISTRY_NAME

Write-Host "📤 Pushing image to registry..." -ForegroundColor Yellow
docker push "$REGISTRY_URL/$IMAGE_NAME:latest"

Write-Host "⚙️  Configuring App Service..." -ForegroundColor Yellow
# Get registry credentials
$REGISTRY_USERNAME = az acr credential show --name $REGISTRY_NAME --query username -o tsv
$REGISTRY_PASSWORD = az acr credential show --name $REGISTRY_NAME --query 'passwords[0].value' -o tsv

# Update App Service
az webapp config container set `
  --name $BACKEND_APP `
  --resource-group $RESOURCE_GROUP `
  --docker-custom-image-name "$REGISTRY_URL/$IMAGE_NAME:latest" `
  --docker-registry-server-url "https://$REGISTRY_URL" `
  --docker-registry-server-user $REGISTRY_USERNAME `
  --docker-registry-server-password $REGISTRY_PASSWORD

Write-Host ""
Write-Host "✅ Backend deployed successfully!" -ForegroundColor Green
Write-Host "   URL: https://$BACKEND_APP.azurewebsites.net"
Write-Host "   Health check: https://$BACKEND_APP.azurewebsites.net/health"
Write-Host ""
Write-Host "📋 To view logs:" -ForegroundColor Yellow
Write-Host "   az webapp log tail --name $BACKEND_APP --resource-group $RESOURCE_GROUP"
Write-Host ""
