# 🚀 Azure Deployment - Quick Start Guide

## What You Need

1. **Azure Account** (free tier) - [Sign up here](https://azure.microsoft.com/free)
2. **Azure CLI** - [Download](https://learn.microsoft.com/cli/azure/install-azure-cli)
3. **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop)
4. **Your Microsoft App Registration credentials** (from earlier setup)

## 5-Minute Quickstart (Windows PowerShell)

### 1. Login to Azure

```powershell
az login
```

This will open a browser. Sign in with your Azure account.

### 2. Run the Deployment Script

```powershell
cd c:\WorkSpaceStuff\SalesRouteTracker\sales-route-tracker

# Make scripts executable
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run setup
.\deploy-to-azure.ps1
```

The script will ask you for:
- **App name**: `sales-route-tracker` (or your choice)
- **Resource group**: `sales-route-tracker-rg`
- **Region**: `eastus`
- **Database password**: Something strong like `P@ssw0rd123!`
- **Registry name**: `salesroutetracker` (alphanumeric only)

**⏱️ This takes 10-15 minutes**

### 3. Update Configuration

After the script completes:

1. Open `.env.production`
2. Update these values:
   ```env
   # Copy the DATABASE_URL from the script output
   DATABASE_URL=postgresql://dbadmin:...@sales-route-tracker-db.postgres.database.azure.com:5432/salesroute
   
   # From your Azure App Registration
   MICROSOFT_CLIENT_ID=your_id_from_azure
   MICROSOFT_CLIENT_SECRET=your_secret_from_azure
   
   # Generate a secret key:
   # Run in PowerShell: [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).ToString())) | Select-Object -First 32
   SECRET_KEY=your_generated_key
   ```

3. Save the file

### 4. Update Azure App Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. **Azure Active Directory** → **App registrations** → Your app
3. **Authentication** tab
4. Add new Redirect URI:
   - `https://sales-route-tracker-backend.azurewebsites.net/auth/callback`
5. **Save**

### 5. Deploy Backend

```powershell
.\deploy-backend-azure.ps1
```

Enter:
- App name: `sales-route-tracker`
- Resource group: `sales-route-tracker-rg`
- Registry name: (same as before)

**⏱️ This takes 3-5 minutes**

### 6. Deploy Frontend

```powershell
.\deploy-frontend-azure.ps1
```

Enter:
- App name: `sales-route-tracker`
- Resource group: `sales-route-tracker-rg`
- Backend URL: `https://sales-route-tracker-backend.azurewebsites.net`

**⏱️ This takes 2-3 minutes**

### 7. Test It

Open your phone or browser:
```
https://sales-route-tracker-frontend.azurewebsites.net
```

You should see the Sales Route Tracker login screen!

---

## Bash Version (Mac/Linux)

Instead of PowerShell scripts, use:

```bash
cd ~/path/to/sales-route-tracker

# Make scripts executable
chmod +x deploy-to-azure.sh
chmod +x deploy-backend-azure.sh
chmod +x deploy-frontend-azure.sh

# Run setup
./deploy-to-azure.sh

# Then deploy backend
./deploy-backend-azure.sh

# Then deploy frontend
./deploy-frontend-azure.sh
```

---

## Troubleshooting

### ❌ "az: command not found"
- Install Azure CLI: https://learn.microsoft.com/cli/azure/install-azure-cli

### ❌ "docker: command not found"
- Install Docker Desktop: https://www.docker.com/products/docker-desktop

### ❌ "Not logged into Azure"
```powershell
az login
```

### ❌ Database Connection Error
```powershell
# Check if database is running
az postgres flexible-server show --name sales-route-tracker-db --resource-group sales-route-tracker-rg

# Check firewall rules
az postgres flexible-server firewall-rule list --name sales-route-tracker-db --resource-group sales-route-tracker-rg
```

### ❌ Deployment fails
```powershell
# View detailed logs
az webapp log tail --name sales-route-tracker-backend --resource-group sales-route-tracker-rg

# Or for frontend
az webapp log tail --name sales-route-tracker-frontend --resource-group sales-route-tracker-rg
```

### ❌ "CORS error" or "Cannot reach backend"
- Check that CORS_ORIGINS in `.env.production` includes your frontend URL
- Make sure backend is deployed and running
- Verify VITE_API_URL points to correct backend URL

---

## URLs After Deployment

| Service | URL |
|---------|-----|
| Frontend | `https://sales-route-tracker-frontend.azurewebsites.net` |
| Backend API | `https://sales-route-tracker-backend.azurewebsites.net` |
| API Docs | `https://sales-route-tracker-backend.azurewebsites.net/docs` |
| Health Check | `https://sales-route-tracker-backend.azurewebsites.net/health` |

---

## Monthly Cost Estimate

| Service | Cost |
|---------|------|
| PostgreSQL (B1ms tier) | $15-20/month |
| App Service (B1 tier) | $10-15/month |
| Container Registry | $5/month |
| **Total** | **~$30-40/month** |

Use Azure's [Free Tier](https://azure.microsoft.com/free) to start - you get:
- $200 free credits for 30 days
- 12 months of free services
- Always-free services

---

## Next: Access from Your Phone

1. Go to `https://sales-route-tracker-frontend.azurewebsites.net` on your phone
2. Click "Connect to OneDrive"
3. Sign in with your Microsoft account
4. Grant permissions
5. Click "Sync from OneDrive"
6. Start tracking your sales!

---

## Support

For issues:
- Check Azure Portal: https://portal.azure.com
- View logs: `az webapp log tail --name {app-name} --resource-group {resource-group}`
- Read full guide: See `AZURE_DEPLOYMENT_GUIDE.md`

Good luck! 🚀
