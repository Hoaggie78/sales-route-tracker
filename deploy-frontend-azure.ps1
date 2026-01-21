# Azure Deployment - Frontend Deployment Script (PowerShell)
# Usage: .\deploy-frontend-azure.ps1

Write-Host "🚀 Deploying Sales Route Tracker Frontend to Azure" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$APP_NAME = Read-Host "📝 Enter app name (e.g., sales-route-tracker)"
$RESOURCE_GROUP = Read-Host "📝 Enter resource group name"
$BACKEND_URL = Read-Host "📝 Enter backend URL (e.g., https://sales-route-tracker-backend.azurewebsites.net)"

$FRONTEND_APP = "$APP_NAME-frontend"

# Check if logged in
try {
    az account show | Out-Null
} catch {
    Write-Host "❌ Not logged into Azure. Run: az login" -ForegroundColor Red
    exit 1
}

Write-Host "🔨 Building frontend..." -ForegroundColor Yellow
Set-Location frontend

# Install dependencies
npm install

# Build with correct API URL
$env:VITE_API_URL = $BACKEND_URL
npm run build

Write-Host "📤 Deploying to Azure..." -ForegroundColor Yellow

# Check if app exists
$appExists = az webapp show --name $FRONTEND_APP --resource-group $RESOURCE_GROUP 2>$null
if ($appExists) {
    Write-Host "Found App Service, deploying..." -ForegroundColor Green
    
    # Create zip file of dist folder
    Compress-Archive -Path dist -DestinationPath ..\frontend-dist.zip -Force
    
    # Deploy
    az webapp deployment source config-zip `
      --resource-group $RESOURCE_GROUP `
      --name $FRONTEND_APP `
      --src ..\frontend-dist.zip
    
    Remove-Item ..\frontend-dist.zip
} else {
    Write-Host "App Service not found. Creating..." -ForegroundColor Yellow
    
    Set-Location ..
    
    # Create App Service Plan
    $PLAN_NAME = "$APP_NAME-frontend-plan"
    az appservice plan create `
      --name $PLAN_NAME `
      --resource-group $RESOURCE_GROUP `
      --sku B1 `
      --is-linux
    
    # Create App Service
    az webapp create `
      --resource-group $RESOURCE_GROUP `
      --plan $PLAN_NAME `
      --name $FRONTEND_APP `
      --runtime "NODE|20-lts"
    
    # Deploy built files
    Set-Location frontend
    Compress-Archive -Path dist -DestinationPath ..\frontend-dist.zip -Force
    Set-Location ..
    
    az webapp deployment source config-zip `
      --resource-group $RESOURCE_GROUP `
      --name $FRONTEND_APP `
      --src frontend-dist.zip
    
    Remove-Item frontend-dist.zip
}

Set-Location ..

Write-Host ""
Write-Host "✅ Frontend deployed successfully!" -ForegroundColor Green
Write-Host "   URL: https://$FRONTEND_APP.azurewebsites.net"
Write-Host ""
Write-Host "📋 To view logs:" -ForegroundColor Yellow
Write-Host "   az webapp log tail --name $FRONTEND_APP --resource-group $RESOURCE_GROUP"
Write-Host ""
