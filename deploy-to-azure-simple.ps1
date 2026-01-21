# Azure Deployment Script - Windows PowerShell Version
# Usage: .\deploy-to-azure-simple.ps1
# (Simplified version without emoji characters for compatibility)

Write-Host "Sales Route Tracker - Azure Deployment Script" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
$azFound = $null -ne (Get-Command az -ErrorAction SilentlyContinue)
$dockerFound = $null -ne (Get-Command docker -ErrorAction SilentlyContinue)

if (-not $azFound) {
    Write-Host "ERROR: Azure CLI not found. Install from: https://learn.microsoft.com/cli/azure/install-azure-cli" -ForegroundColor Red
    exit 1
}
if (-not $dockerFound) {
    Write-Host "ERROR: Docker not found. Install from: https://www.docker.com/products/docker-desktop" -ForegroundColor Red
    exit 1
}
Write-Host "SUCCESS: All prerequisites found" -ForegroundColor Green
Write-Host ""

# Configuration
$APP_NAME = Read-Host "Enter app name (e.g., sales-route-tracker)"
$RESOURCE_GROUP = Read-Host "Enter resource group name"
$LOCATION = Read-Host "Enter Azure region (default: eastus)"
if ([string]::IsNullOrWhiteSpace($LOCATION)) { $LOCATION = "eastus" }

$DB_ADMIN = Read-Host "Enter database admin username (default: dbadmin)"
if ([string]::IsNullOrWhiteSpace($DB_ADMIN)) { $DB_ADMIN = "dbadmin" }

$DB_PASSWORD = Read-Host "Enter strong database password" -AsSecureString
$DB_PASSWORD = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($DB_PASSWORD))

$REGISTRY_NAME = Read-Host "Enter your Azure container registry name (alphanumeric only)"

# Verify login
Write-Host ""
Write-Host "Checking Azure login..." -ForegroundColor Yellow
try {
    az account show | Out-Null
    Write-Host "SUCCESS: Logged into Azure" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Not logged into Azure. Run: az login" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 1: Create Resource Group
Write-Host "Step 1: Creating resource group..." -ForegroundColor Yellow
az group create --name $RESOURCE_GROUP --location $LOCATION
Write-Host "SUCCESS: Resource group created" -ForegroundColor Green
Write-Host ""

# Step 2: Create PostgreSQL Database
Write-Host "Step 2: Creating PostgreSQL database..." -ForegroundColor Yellow
$DB_SERVER = "$APP_NAME-db"
$DB_NAME = "salesroute"

az postgres flexible-server create `
  --resource-group $RESOURCE_GROUP `
  --name $DB_SERVER `
  --location $LOCATION `
  --admin-user $DB_ADMIN `
  --admin-password $DB_PASSWORD `
  --database-name $DB_NAME `
  --sku-name Standard_B1ms `
  --tier Burstable `
  --storage-size 32 `
  --public-access Enabled

$DB_HOST = "$DB_SERVER.postgres.database.azure.com"
$DATABASE_URL = "postgresql://${DB_ADMIN}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}"
Write-Host "SUCCESS: PostgreSQL database created" -ForegroundColor Green
Write-Host "   Database URL: $DATABASE_URL"
Write-Host ""

# Step 3: Create firewall rules
Write-Host "Step 3: Creating firewall rules..." -ForegroundColor Yellow
az postgres flexible-server firewall-rule create `
  --resource-group $RESOURCE_GROUP `
  --name $DB_SERVER `
  --rule-name AllowAzureServices `
  --start-ip-address 0.0.0.0 `
  --end-ip-address 0.0.0.0

Write-Host "SUCCESS: Firewall rules created" -ForegroundColor Green
Write-Host ""

# Step 4: Create App Service Plan
Write-Host "Step 4: Creating App Service plan..." -ForegroundColor Yellow
$PLAN_NAME = "$APP_NAME-plan"
az appservice plan create `
  --name $PLAN_NAME `
  --resource-group $RESOURCE_GROUP `
  --sku B1 `
  --is-linux
Write-Host "SUCCESS: App Service plan created" -ForegroundColor Green
Write-Host ""

# Step 5: Create Backend App Service
Write-Host "Step 5: Creating backend App Service..." -ForegroundColor Yellow
$BACKEND_APP = "$APP_NAME-backend"
az webapp create `
  --resource-group $RESOURCE_GROUP `
  --plan $PLAN_NAME `
  --name $BACKEND_APP `
  --runtime "PYTHON|3.11"
Write-Host "SUCCESS: Backend App Service created" -ForegroundColor Green
Write-Host "   URL: https://$BACKEND_APP.azurewebsites.net"
Write-Host ""

# Step 6: Create Container Registry
Write-Host "Step 6: Creating Azure Container Registry..." -ForegroundColor Yellow
az acr create `
  --resource-group $RESOURCE_GROUP `
  --name $REGISTRY_NAME `
  --sku Basic
Write-Host "SUCCESS: Container registry created" -ForegroundColor Green
Write-Host ""

# Step 7: Enable managed identity for App Service
Write-Host "Step 7: Configuring managed identity..." -ForegroundColor Yellow
az webapp identity assign `
  --resource-group $RESOURCE_GROUP `
  --name $BACKEND_APP
Write-Host "SUCCESS: Managed identity configured" -ForegroundColor Green
Write-Host ""

# Step 8: Summary
Write-Host "=================================================" -ForegroundColor Green
Write-Host "SUCCESS: Azure infrastructure created successfully!" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Update your credentials in .env.production:" -ForegroundColor White
Write-Host "   - DATABASE_URL=$DATABASE_URL"
Write-Host "   - Update MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET"
Write-Host ""
Write-Host "2. Update Azure App Registration in Portal:" -ForegroundColor White
Write-Host "   - Add redirect URI: https://$BACKEND_APP.azurewebsites.net/auth/callback"
Write-Host ""
Write-Host "3. Deploy backend with:" -ForegroundColor White
Write-Host "   .\deploy-backend-azure.ps1"
Write-Host ""
Write-Host "4. Deploy frontend with:" -ForegroundColor White
Write-Host "   .\deploy-frontend-azure.ps1"
Write-Host ""
Write-Host "RESOURCE SUMMARY:" -ForegroundColor Cyan
Write-Host "   - Resource Group: $RESOURCE_GROUP"
Write-Host "   - Database: $DB_SERVER"
Write-Host "   - Backend App: $BACKEND_APP"
Write-Host "   - Registry: $REGISTRY_NAME"
Write-Host ""
Write-Host "Estimated monthly cost: $25-35"
Write-Host ""
