# Azure Deployment Script - Fixed Version
# Corrected Azure CLI commands for 2026

Write-Host "Sales Route Tracker - Azure Deployment Script (FIXED)" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# Set variables from previous run
$APP_NAME = "sales-route-tracker"
$RESOURCE_GROUP = "sales-route-tracker-rg"
$LOCATION = "westus2"
$DB_ADMIN = "dbadmin"
$DB_PASSWORD = "P@ssw0rd123!Sales2026"
$REGISTRY_NAME = "salesroutetracker"
$DB_SERVER = "sales-route-tracker-db"
$DB_NAME = "salesroute"

Write-Host "Step 1: Register required providers..." -ForegroundColor Yellow
az provider register --namespace Microsoft.DBforPostgreSQL
az provider register --namespace Microsoft.Web  
az provider register --namespace Microsoft.ContainerRegistry
Write-Host "SUCCESS: Providers registered" -ForegroundColor Green
Write-Host ""

Write-Host "Step 2: Creating PostgreSQL database (corrected)..." -ForegroundColor Yellow
az postgres flexible-server create `
  --resource-group $RESOURCE_GROUP `
  --name $DB_SERVER `
  --location $LOCATION `
  --admin-user $DB_ADMIN `
  --admin-password $DB_PASSWORD `
  --sku-name Standard_B1ms `
  --tier Burstable `
  --public-access 0.0.0.0 `
  --storage-size 32

Write-Host "SUCCESS: PostgreSQL database created" -ForegroundColor Green
Write-Host ""

Write-Host "Step 3: Creating firewall rules..." -ForegroundColor Yellow
az postgres flexible-server firewall-rule create `
  --resource-group $RESOURCE_GROUP `
  --name $DB_SERVER `
  --rule-name AllowAllAzureIps `
  --start-ip-address 0.0.0.0 `
  --end-ip-address 255.255.255.255

Write-Host "SUCCESS: Firewall rules created" -ForegroundColor Green
Write-Host ""

Write-Host "Step 4: Creating App Service plan..." -ForegroundColor Yellow
$PLAN_NAME = "$APP_NAME-plan"
az appservice plan create `
  --name $PLAN_NAME `
  --resource-group $RESOURCE_GROUP `
  --sku B1 `
  --is-linux

Write-Host "SUCCESS: App Service plan created" -ForegroundColor Green
Write-Host ""

Write-Host "Step 5: Creating backend App Service..." -ForegroundColor Yellow
$BACKEND_APP = "$APP_NAME-backend"
az webapp create `
  --resource-group $RESOURCE_GROUP `
  --plan $PLAN_NAME `
  --name $BACKEND_APP `
  --runtime "PYTHON:3.11"

Write-Host "SUCCESS: Backend App Service created" -ForegroundColor Green
Write-Host "   URL: https://$BACKEND_APP.azurewebsites.net"
Write-Host ""

Write-Host "Step 6: Creating Azure Container Registry..." -ForegroundColor Yellow
az acr create `
  --resource-group $RESOURCE_GROUP `
  --name $REGISTRY_NAME `
  --sku Basic

Write-Host "SUCCESS: Container registry created" -ForegroundColor Green
Write-Host ""

Write-Host "Step 7: Configuring managed identity..." -ForegroundColor Yellow
az webapp identity assign `
  --resource-group $RESOURCE_GROUP `
  --name $BACKEND_APP

Write-Host "SUCCESS: Managed identity configured" -ForegroundColor Green
Write-Host ""

Write-Host "======================================================" -ForegroundColor Green
Write-Host "SUCCESS: All Azure resources created!" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Your resources are ready! Next steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Update .env.production with:" -ForegroundColor White
$connStr = "postgresql://$($DB_ADMIN):$($DB_PASSWORD)@$($DB_SERVER).postgres.database.azure.com:5432/$($DB_NAME)"
Write-Host "   DATABASE_URL=$connStr"
Write-Host ""
Write-Host "2. Get your Microsoft credentials from Azure Portal:" -ForegroundColor White
Write-Host "   - Client ID"
Write-Host "   - Client Secret"
Write-Host "   - Add redirect: https://$BACKEND_APP.azurewebsites.net/auth/callback"
Write-Host ""
Write-Host "3. Then run: .\deploy-backend-azure.ps1" -ForegroundColor White
Write-Host ""
