# Azure Deployment Guide - Sales Route Tracker

## Prerequisites

- Azure Account (create free at https://azure.microsoft.com/free)
- Azure CLI installed (https://learn.microsoft.com/cli/azure/install-azure-cli)
- Git installed
- Docker installed (for local testing)

## Step 1: Create Azure Resources

### 1.1 Create a Resource Group

```bash
# Set variables
RESOURCE_GROUP="sales-route-tracker-rg"
LOCATION="eastus"
APP_NAME="sales-route-tracker"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION
```

### 1.2 Create Azure PostgreSQL Database

```bash
# Set database variables
DB_SERVER="${APP_NAME}-db"
DB_ADMIN="dbadmin"
DB_PASSWORD="YourSecurePassword123!"  # Change this!
DB_NAME="salesroute"

# Create PostgreSQL server (Flexible Server - recommended)
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER \
  --location $LOCATION \
  --admin-user $DB_ADMIN \
  --admin-password $DB_PASSWORD \
  --database-name $DB_NAME \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32
```

After creation, note:
- Server name: `{DB_SERVER}.postgres.database.azure.com`
- Database URL: `postgresql://{DB_ADMIN}:{DB_PASSWORD}@{DB_SERVER}.postgres.database.azure.com:5432/{DB_NAME}`

### 1.3 Allow Connections to Database

```bash
# Allow Azure services and local machine
az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Allow your local IP (find it with: curl https://checkip.amazonaws.com)
az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER \
  --rule-name AllowLocalIP \
  --start-ip-address YOUR_IP_ADDRESS \
  --end-ip-address YOUR_IP_ADDRESS
```

### 1.4 Create Azure App Service for Backend

```bash
# Create App Service Plan
PLAN_NAME="${APP_NAME}-plan"
az appservice plan create \
  --name $PLAN_NAME \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux

# Create App Service (Backend)
BACKEND_APP="${APP_NAME}-backend"
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN_NAME \
  --name $BACKEND_APP \
  --runtime "PYTHON|3.11"
```

### 1.5 Create Azure Static Web Apps for Frontend

```bash
# Create Static Web App
FRONTEND_APP="${APP_NAME}-frontend"
az staticwebapp create \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --source https://github.com/YOUR_USERNAME/sales-route-tracker \
  --branch main \
  --app-location "frontend" \
  --api-location "" \
  --output-location "dist"
```

**Note**: If you don't have a GitHub repo yet, create one first or deploy manually later.

## Step 2: Update Azure App Registration

Go to [Azure Portal](https://portal.azure.com) and update your OAuth app:

1. Navigate to **Azure Active Directory** → **App registrations** → Select your app
2. Go to **Authentication**
3. Add new Redirect URIs:
   - `https://{BACKEND_APP}.azurewebsites.net/auth/callback`
   - `https://{FRONTEND_APP}.azurestaticapps.net`
   - Keep: `http://localhost:8000/auth/callback` (for local development)

## Step 3: Configure Environment Variables

Create `.env.production` in the root directory:

```env
# Database (from Azure PostgreSQL)
POSTGRES_USER=dbadmin
POSTGRES_PASSWORD=YourSecurePassword123!
POSTGRES_DB=salesroute
DATABASE_URL=postgresql://dbadmin:YourSecurePassword123!@{DB_SERVER}.postgres.database.azure.com:5432/salesroute

# Microsoft Graph API (from your Azure App Registration)
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
MICROSOFT_TENANT_ID=common
MICROSOFT_REDIRECT_URI=https://{BACKEND_APP}.azurewebsites.net/auth/callback

# OneDrive File Path
ONEDRIVE_FILE_PATH=/Sales/KalebHogelandJanuary19thStart4WeekSalesRoutePlan__1_.xlsx

# Backend Security (generate new: openssl rand -hex 32)
SECRET_KEY=your_generated_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Frontend
VITE_API_URL=https://{BACKEND_APP}.azurewebsites.net
CORS_ORIGINS=["https://{FRONTEND_APP}.azurestaticapps.net"]
```

## Step 4: Deploy Backend to Azure App Service

### 4.1 Configure App Service Settings

```bash
# Set environment variables in App Service
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $BACKEND_APP \
  --settings \
    DATABASE_URL="postgresql://..." \
    MICROSOFT_CLIENT_ID="..." \
    MICROSOFT_CLIENT_SECRET="..." \
    MICROSOFT_TENANT_ID="common" \
    MICROSOFT_REDIRECT_URI="https://{BACKEND_APP}.azurewebsites.net/auth/callback" \
    ONEDRIVE_FILE_PATH="/Sales/KalebHogelandJanuary19thStart4WeekSalesRoutePlan__1_.xlsx" \
    SECRET_KEY="..." \
    ALGORITHM="HS256" \
    ACCESS_TOKEN_EXPIRE_MINUTES="10080" \
    CORS_ORIGINS='["https://{FRONTEND_APP}.azurestaticapps.net"]'
```

### 4.2 Deploy Backend Code

**Option A: Using Git (Recommended)**

```bash
# Initialize git in backend directory
cd backend
git init
git add .
git commit -m "Initial commit"

# Create local git remote to Azure
az webapp deployment source config-zip \
  --resource-group $RESOURCE_GROUP \
  --name $BACKEND_APP \
  --src backend.zip
```

**Option B: Using Docker**

```bash
# Enable Docker deployment
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $BACKEND_APP \
  --linux-fx-version "DOCKER|{DOCKER_IMAGE}"
```

**Option C: Using Azure Container Registry (Better)**

```bash
# Create Azure Container Registry
REGISTRY_NAME="${APP_NAME}acr"
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $REGISTRY_NAME \
  --sku Basic

# Build and push Docker image
az acr build \
  --registry $REGISTRY_NAME \
  --image sales-route-tracker-backend:latest \
  ./backend

# Deploy from registry
az webapp config container set \
  --resource-group $RESOURCE_GROUP \
  --name $BACKEND_APP \
  --docker-custom-image-name ${REGISTRY_NAME}.azurecr.io/sales-route-tracker-backend:latest \
  --docker-registry-server-url https://${REGISTRY_NAME}.azurecr.io \
  --docker-registry-server-user <username> \
  --docker-registry-server-password <password>
```

## Step 5: Deploy Frontend to Static Web Apps

The frontend was already created with GitHub integration. If you used manual deployment:

```bash
# Build the frontend
cd frontend
npm install
npm run build

# Deploy to Static Web Apps
az staticwebapp upload \
  --resource-group $RESOURCE_GROUP \
  --name $FRONTEND_APP \
  --source-path ./dist
```

## Step 6: Verify Deployment

### Check Backend Health

```bash
curl https://{BACKEND_APP}.azurewebsites.net/health
```

Should return:
```json
{"status": "healthy"}
```

### Check Frontend Access

Visit: `https://{FRONTEND_APP}.azurestaticapps.net`

## Step 7: Monitor and Troubleshoot

### View Logs

```bash
# Stream backend logs
az webapp log tail \
  --resource-group $RESOURCE_GROUP \
  --name $BACKEND_APP

# View Application Insights
az monitor app-insights app show \
  --resource-group $RESOURCE_GROUP \
  --app $BACKEND_APP
```

### Common Issues

**Issue: Database connection timeout**
- Check firewall rules allow your IP
- Verify DATABASE_URL is correct
- Ensure PostgreSQL is running

**Issue: Auth redirect fails**
- Verify MICROSOFT_REDIRECT_URI in Azure App Registration
- Check CORS_ORIGINS includes your frontend URL

**Issue: CORS errors in frontend**
- Add frontend URL to CORS_ORIGINS
- Ensure VITE_API_URL points to correct backend

## Step 8: Custom Domain (Optional)

```bash
# Create custom domain
az webapp config hostname add \
  --resource-group $RESOURCE_GROUP \
  --webapp-name $BACKEND_APP \
  --hostname api.yourdomain.com

# Add SSL certificate
az webapp config ssl bind \
  --resource-group $RESOURCE_GROUP \
  --webapp-name $BACKEND_APP \
  --certificate-thumbprint <thumbprint> \
  --ssl-type SNI
```

## Cost Estimate

- **PostgreSQL Flexible Server (B1ms)**: ~$15-20/month
- **App Service Plan (B1)**: ~$10-15/month
- **Static Web Apps**: Free tier available
- **Total**: ~$25-35/month for small usage

## Next Steps

1. Replace placeholder values with your actual credentials
2. Run Azure CLI commands to create resources
3. Deploy backend and frontend
4. Test from your phone
5. Set up monitoring and alerts

## Support

For issues with Azure:
- Azure Portal: https://portal.azure.com
- Azure CLI Docs: https://learn.microsoft.com/cli/azure/
- App Service Docs: https://learn.microsoft.com/azure/app-service/
