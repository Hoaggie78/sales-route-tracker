# Azure Deployment - Manual Portal Setup (Step-by-Step)

If you prefer using the Azure Portal UI instead of command-line scripts, follow this guide.

## Step 1: Create Resource Group

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **Create a resource**
3. Search for **Resource Group**
4. Click **Create**
5. Fill in:
   - **Subscription**: Your subscription
   - **Resource group name**: `sales-route-tracker-rg`
   - **Region**: `East US`
6. Click **Review + create** → **Create**

## Step 2: Create PostgreSQL Database

1. Click **Create a resource**
2. Search for **Database for PostgreSQL - Flexible Server**
3. Click **Create**
4. Fill in:
   - **Subscription**: Your subscription
   - **Resource group**: `sales-route-tracker-rg`
   - **Server name**: `sales-route-tracker-db`
   - **Region**: `East US`
   - **PostgreSQL version**: 15
   - **Admin username**: `dbadmin`
   - **Password**: Something strong like `P@ssw0rd123!` (save this!)
   - **Compute + storage**: Burstable (B1ms) - $15/month
   - **Storage size**: 32 GB
5. Click **Review + create** → **Create**

**⏱️ Wait 5-10 minutes for database to be created**

### Configure Database Access

1. Once created, go to the database resource
2. Click **Networking** (left menu)
3. Under **Public access**:
   - Click **+ Add current client IP address**
   - This allows you to connect from your computer
4. Click **+ Add 0.0.0.0 - 255.255.255.255** for Azure services
5. Click **Save**

### Get Connection String

1. Go to the database resource
2. Click **Connection strings** (left menu)
3. Copy the **psycopg2** connection string
4. Replace `{your-password}` with your actual password
5. Replace `{your-username}` with `dbadmin`

Example:
```
postgresql://dbadmin:P@ssw0rd123!@sales-route-tracker-db.postgres.database.azure.com:5432/salesroute
```

Save this - you'll need it later!

## Step 3: Create Container Registry

1. Click **Create a resource**
2. Search for **Container Registry**
3. Click **Create**
4. Fill in:
   - **Subscription**: Your subscription
   - **Resource group**: `sales-route-tracker-rg`
   - **Registry name**: `salesroutetracker` (must be lowercase alphanumeric)
   - **Location**: `East US`
   - **SKU**: Basic ($5/month)
5. Click **Review + create** → **Create**

**⏱️ Wait 1-2 minutes**

## Step 4: Create App Service Plan

1. Click **Create a resource**
2. Search for **App Service Plan**
3. Click **Create**
4. Fill in:
   - **Subscription**: Your subscription
   - **Resource group**: `sales-route-tracker-rg`
   - **Name**: `sales-route-tracker-plan`
   - **Operating System**: Linux
   - **Region**: `East US`
   - **Pricing tier**: B1 (Linux) - $10-15/month
5. Click **Review + create** → **Create**

**⏱️ Wait 1-2 minutes**

## Step 5: Create Backend App Service

1. Click **Create a resource**
2. Search for **App Service**
3. Click **Create**
4. Fill in:
   - **Subscription**: Your subscription
   - **Resource group**: `sales-route-tracker-rg`
   - **Name**: `sales-route-tracker-backend`
   - **Publish**: Docker Container
   - **Operating System**: Linux
   - **Region**: `East US`
   - **App Service Plan**: `sales-route-tracker-plan`
5. Click **Next: Docker**
6. Leave as is for now (we'll update later)
7. Click **Review + create** → **Create**

**⏱️ Wait 2-3 minutes**

## Step 6: Create Frontend App Service

1. Click **Create a resource**
2. Search for **App Service**
3. Click **Create**
4. Fill in:
   - **Subscription**: Your subscription
   - **Resource group**: `sales-route-tracker-rg`
   - **Name**: `sales-route-tracker-frontend`
   - **Publish**: Code
   - **Runtime stack**: Node 20 LTS
   - **Operating System**: Linux
   - **Region**: `East US`
   - **App Service Plan**: `sales-route-tracker-plan`
5. Click **Review + create** → **Create**

**⏱️ Wait 2-3 minutes**

## Step 7: Update Azure App Registration

1. Go to **Azure Active Directory** (search in portal)
2. Click **App registrations**
3. Find your "Sales Route Tracker" app
4. Click **Authentication** (left menu)
5. Under **Redirect URIs**, add:
   - `https://sales-route-tracker-backend.azurewebsites.net/auth/callback`
6. Click **Save**

## Step 8: Configure Backend Environment Variables

1. Go to your **sales-route-tracker-backend** App Service
2. Click **Configuration** (left menu)
3. Click **+ New application setting** and add each:

| Name | Value |
|------|-------|
| `DATABASE_URL` | Your PostgreSQL connection string (from Step 2) |
| `MICROSOFT_CLIENT_ID` | From your Azure App Registration |
| `MICROSOFT_CLIENT_SECRET` | From your Azure App Registration |
| `MICROSOFT_TENANT_ID` | `common` |
| `MICROSOFT_REDIRECT_URI` | `https://sales-route-tracker-backend.azurewebsites.net/auth/callback` |
| `ONEDRIVE_FILE_PATH` | `/Sales/KalebHogelandJanuary19thStart4WeekSalesRoutePlan__1_.xlsx` |
| `SECRET_KEY` | Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` |
| `CORS_ORIGINS` | `["https://sales-route-tracker-frontend.azurewebsites.net"]` |

4. Click **Save**

## Step 9: Configure Frontend Environment Variables

1. Go to your **sales-route-tracker-frontend** App Service
2. Click **Configuration** (left menu)
3. Click **+ New application setting**:

| Name | Value |
|------|-------|
| `VITE_API_URL` | `https://sales-route-tracker-backend.azurewebsites.net` |

4. Click **Save**

## Step 10: Deploy Backend with Docker

### Option A: Using Azure Container Registry

1. Go to your **sales-route-tracker-backend** App Service
2. Click **Deployment** → **Deployment Center** (left menu)
3. **Source**: Azure Container Registry
4. **Registry**: `salesroutetracker`
5. **Image**: `sales-route-tracker-backend`
6. **Tag**: `latest`
7. Click **Save**

### Option B: Build and Push Manually

On your computer:

```powershell
# Login to Azure Container Registry
az acr login --name salesroutetracker

# Build Docker image
docker build -t salesroutetracker.azurecr.io/sales-route-tracker-backend:latest ./backend

# Push to registry
docker push salesroutetracker.azurecr.io/sales-route-tracker-backend:latest

# Then in Azure Portal:
# Go to Backend App Service → Deployment Center
# Select Azure Container Registry
# Configure as shown above
```

## Step 11: Deploy Frontend Code

### Option A: Using Git

1. Make sure your code is in a Git repository
2. In frontend App Service → **Deployment Center**
3. Select **GitHub** (or GitLab/Bitbucket)
4. Connect your repository
5. Select branch: `main`
6. Build option: **GitHub Actions**
7. Click **Save**

### Option B: ZIP Deploy

On your computer:

```powershell
cd frontend

# Build frontend
npm install
npm run build

# Create ZIP file
Compress-Archive -Path dist -DestinationPath ..\frontend-dist.zip

# Deploy from portal:
# Go to Frontend App Service → Deployment → Deployment Center
# Select ZIP → Upload the ZIP file
```

## Step 12: Test Your Deployment

### Check Backend Health

Go to: `https://sales-route-tracker-backend.azurewebsites.net/health`

You should see:
```json
{"status": "healthy"}
```

### Check Frontend

Go to: `https://sales-route-tracker-frontend.azurewebsites.net`

You should see the Sales Route Tracker login screen!

### View Logs (if something breaks)

1. Go to App Service
2. Click **Log stream** (left menu)
3. You'll see real-time logs

## Step 13: Monitor Costs

1. Go to your **Resource Group** (`sales-route-tracker-rg`)
2. Click **Cost Management** (left menu)
3. You'll see all your costs

**Expected monthly cost**: $30-40

## Common Issues

### ❌ Cannot connect to database

1. Check firewall rules in PostgreSQL resource
2. Verify connection string is correct
3. Make sure password doesn't have special characters like `@` (use backslash to escape)

### ❌ Frontend can't reach backend (CORS error)

1. Check CORS_ORIGINS in backend configuration
2. Make sure it exactly matches your frontend URL
3. Restart the backend app

### ❌ "auth/callback not found"

1. Verify redirect URI in Azure App Registration matches exactly
2. Restart backend app service

### ❌ App Service keeps crashing

1. Go to App Service → **Log stream**
2. Look for error messages
3. Check environment variables are all set correctly

## Support

Need help?
- [Azure Support](https://support.microsoft.com/azure)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)

Good luck! 🚀
