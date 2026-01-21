#!/bin/bash
# Azure Deployment Script - Automated Setup
# Usage: ./deploy-to-azure.sh

set -e

echo "🚀 Sales Route Tracker - Azure Deployment Script"
echo "=================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."
command -v az >/dev/null 2>&1 || { echo -e "${RED}❌ Azure CLI not found. Install from: https://learn.microsoft.com/cli/azure/install-azure-cli${NC}"; exit 1; }
command -v git >/dev/null 2>&1 || { echo -e "${RED}❌ Git not found${NC}"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo -e "${RED}❌ Docker not found${NC}"; exit 1; }
echo -e "${GREEN}✅ All prerequisites found${NC}"
echo ""

# Configuration
read -p "📝 Enter app name (e.g., sales-route-tracker): " APP_NAME
read -p "📝 Enter resource group name: " RESOURCE_GROUP
read -p "📝 Enter Azure region (default: eastus): " LOCATION
LOCATION=${LOCATION:-eastus}

read -p "🔐 Enter database admin username (default: dbadmin): " DB_ADMIN
DB_ADMIN=${DB_ADMIN:-dbadmin}

read -sp "🔐 Enter strong database password: " DB_PASSWORD
echo ""

read -p "📝 Enter your Azure container registry name (alphanumeric only): " REGISTRY_NAME

# Verify login
echo ""
echo "🔑 Checking Azure login..."
az account show > /dev/null || { echo -e "${RED}❌ Not logged into Azure. Run: az login${NC}"; exit 1; }
echo -e "${GREEN}✅ Logged into Azure${NC}"
echo ""

# Step 1: Create Resource Group
echo "📦 Step 1: Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION
echo -e "${GREEN}✅ Resource group created${NC}"
echo ""

# Step 2: Create PostgreSQL Database
echo "🗄️  Step 2: Creating PostgreSQL database..."
DB_SERVER="${APP_NAME}-db"
DB_NAME="salesroute"

az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER \
  --location $LOCATION \
  --admin-user $DB_ADMIN \
  --admin-password "$DB_PASSWORD" \
  --database-name $DB_NAME \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --public-access Enabled

DB_HOST="${DB_SERVER}.postgres.database.azure.com"
DATABASE_URL="postgresql://${DB_ADMIN}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}"
echo -e "${GREEN}✅ PostgreSQL database created${NC}"
echo "   Database URL: $DATABASE_URL"
echo ""

# Step 3: Create firewall rules
echo "🔥 Step 3: Creating firewall rules..."
az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

echo -e "${GREEN}✅ Firewall rules created${NC}"
echo ""

# Step 4: Create App Service Plan
echo "📱 Step 4: Creating App Service plan..."
PLAN_NAME="${APP_NAME}-plan"
az appservice plan create \
  --name $PLAN_NAME \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux
echo -e "${GREEN}✅ App Service plan created${NC}"
echo ""

# Step 5: Create Backend App Service
echo "🖥️  Step 5: Creating backend App Service..."
BACKEND_APP="${APP_NAME}-backend"
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN_NAME \
  --name $BACKEND_APP \
  --runtime "PYTHON|3.11"
echo -e "${GREEN}✅ Backend App Service created${NC}"
echo "   URL: https://${BACKEND_APP}.azurewebsites.net"
echo ""

# Step 6: Create Container Registry
echo "🐳 Step 6: Creating Azure Container Registry..."
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $REGISTRY_NAME \
  --sku Basic
echo -e "${GREEN}✅ Container registry created${NC}"
echo ""

# Step 7: Enable managed identity for App Service
echo "🔑 Step 7: Configuring managed identity..."
az webapp identity assign \
  --resource-group $RESOURCE_GROUP \
  --name $BACKEND_APP
echo -e "${GREEN}✅ Managed identity configured${NC}"
echo ""

# Step 8: Summary
echo "=================================================="
echo -e "${GREEN}✅ Azure infrastructure created successfully!${NC}"
echo "=================================================="
echo ""
echo "📌 Next Steps:"
echo ""
echo "1️⃣  Update your credentials in .env.production:"
echo "   - DATABASE_URL=$DATABASE_URL"
echo "   - Update MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET"
echo ""
echo "2️⃣  Update Azure App Registration in Portal:"
echo "   - Add redirect URI: https://${BACKEND_APP}.azurewebsites.net/auth/callback"
echo ""
echo "3️⃣  Deploy backend with:"
echo "   ./deploy-backend-azure.sh"
echo ""
echo "4️⃣  Deploy frontend with:"
echo "   ./deploy-frontend-azure.sh"
echo ""
echo "📊 Resource Summary:"
echo "   - Resource Group: $RESOURCE_GROUP"
echo "   - Database: $DB_SERVER"
echo "   - Backend App: $BACKEND_APP"
echo "   - Registry: $REGISTRY_NAME"
echo ""
echo "💰 Estimated monthly cost: \$25-35"
echo ""
