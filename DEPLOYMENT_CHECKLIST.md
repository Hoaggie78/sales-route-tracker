# ✅ Azure Deployment Checklist

Use this checklist to track your progress through the deployment.

## 📋 Pre-Deployment (Before Starting)

- [ ] Azure account created (free.microsoft.com/azure)
- [ ] Azure CLI installed (`az --version` works)
- [ ] Docker Desktop installed (`docker --version` works)
- [ ] Git installed (`git --version` works)
- [ ] Node.js installed (`node --version` works)
- [ ] Azure App Registration created with credentials saved
- [ ] Excel file uploaded to OneDrive
- [ ] Workspace cloned/downloaded to your computer

## 🔧 Step 1: Create Azure Resources

Choose your method:

### Method A: Using PowerShell Script (Easiest)

- [ ] Opened PowerShell
- [ ] Ran: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- [ ] Navigated to: `c:\WorkSpaceStuff\SalesRouteTracker\sales-route-tracker`
- [ ] Ran: `.\deploy-to-azure.ps1`
- [ ] Logged into Azure when browser appeared
- [ ] Entered all required information:
  - [ ] App name: `sales-route-tracker` (or your choice)
  - [ ] Resource group: `sales-route-tracker-rg`
  - [ ] Region: `eastus`
  - [ ] Database password: (strong password saved somewhere!)
  - [ ] Registry name: `salesroutetracker`
- [ ] Script completed successfully
- [ ] **Saved the output** with resource names and URLs

### Method B: Using Azure Portal (Visual)

- [ ] Opened [Azure Portal](https://portal.azure.com)
- [ ] Created Resource Group: `sales-route-tracker-rg`
- [ ] Created PostgreSQL Database: `sales-route-tracker-db`
- [ ] Created Container Registry: `salesroutetracker`
- [ ] Created App Service Plan: `sales-route-tracker-plan`
- [ ] Created Backend App Service: `sales-route-tracker-backend`
- [ ] Created Frontend App Service: `sales-route-tracker-frontend`
- [ ] **Noted down all resource names**

## 🔑 Step 2: Update Configuration

- [ ] Copied database connection string
- [ ] Opened `.env.production` file
- [ ] Updated `DATABASE_URL` with actual connection string
- [ ] Updated `MICROSOFT_CLIENT_ID` (from Azure App Registration)
- [ ] Updated `MICROSOFT_CLIENT_SECRET` (from Azure App Registration)
- [ ] Generated new `SECRET_KEY` using: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] Updated `SECRET_KEY` in `.env.production`
- [ ] Updated CORS_ORIGINS with frontend URL
- [ ] Saved `.env.production`

## 🌐 Step 3: Update Azure App Registration

- [ ] Opened [Azure Portal](https://portal.azure.com)
- [ ] Navigated to Azure Active Directory → App registrations
- [ ] Selected your app
- [ ] Clicked Authentication
- [ ] Added new Redirect URI: `https://sales-route-tracker-backend.azurewebsites.net/auth/callback`
- [ ] Clicked Save

## 🐳 Step 4: Deploy Backend

Choose your method:

### Method A: Using PowerShell Script

- [ ] Ran: `.\deploy-backend-azure.ps1`
- [ ] Entered app name, resource group, registry name when prompted
- [ ] Script completed successfully
- [ ] Saw message: "✅ Backend deployed successfully!"

### Method B: Using Commands

```powershell
az acr login --name salesroutetracker
docker build -t salesroutetracker.azurecr.io/sales-route-tracker-backend:latest ./backend
docker push salesroutetracker.azurecr.io/sales-route-tracker-backend:latest
```

- [ ] Docker build succeeded
- [ ] Image pushed to registry
- [ ] Went to Backend App Service → Deployment Center
- [ ] Configured to use Container Registry image
- [ ] App is now running

## ✅ Step 5: Verify Backend

- [ ] Opened browser to: `https://sales-route-tracker-backend.azurewebsites.net/health`
- [ ] Saw response: `{"status": "healthy"}`
- [ ] Backend is working! ✅

## 🖥️ Step 6: Deploy Frontend

Choose your method:

### Method A: Using PowerShell Script

- [ ] Ran: `.\deploy-frontend-azure.ps1`
- [ ] Entered app name, resource group, backend URL when prompted
- [ ] Script completed successfully
- [ ] Saw message: "✅ Frontend deployed successfully!"

### Method B: Manual Deployment

```powershell
cd frontend
npm install
npm run build
```

- [ ] Build completed without errors
- [ ] Zipped the `dist` folder
- [ ] Went to Frontend App Service → Deployment Center
- [ ] Uploaded ZIP file
- [ ] App is now running

## 📱 Step 7: Access Your App

- [ ] Opened browser to: `https://sales-route-tracker-frontend.azurewebsites.net`
- [ ] Saw Sales Route Tracker login screen
- [ ] Logged in or clicked "Connect to OneDrive"
- [ ] Microsoft login page appeared (good sign!)

## 🎯 Step 8: Test from Phone

- [ ] Connected phone to same internet (or just any internet)
- [ ] Opened: `https://sales-route-tracker-frontend.azurewebsites.net` on phone
- [ ] App loaded successfully
- [ ] Can see all features
- [ ] Login works
- [ ] Can view routes
- [ ] **It works from anywhere!** ✅

## 📊 Step 9: First Time Setup

- [ ] Clicked "Connect to OneDrive"
- [ ] Signed in with Microsoft account
- [ ] Granted permissions to app
- [ ] Went back to app
- [ ] Clicked "Sync from OneDrive"
- [ ] Excel file was imported successfully
- [ ] Can see your 4-week route plan
- [ ] Can see your customers by week/day

## 💰 Step 10: Monitor Costs

- [ ] Opened [Azure Portal](https://portal.azure.com)
- [ ] Went to Resource Group → Cost Management
- [ ] Noted expected monthly cost (~$30-40)
- [ ] Set up cost alerts if needed (optional)

## 🎉 Deployment Complete!

Congratulations! Your Sales Route Tracker is now:

- ✅ Deployed to Azure
- ✅ Accessible from your phone
- ✅ Synced with your OneDrive Excel file
- ✅ Ready for production use

## 📝 Next Steps

1. **Tell your team** about the new app
2. **Start tracking** your sales from the field
3. **Monitor logs** if any issues: 
   ```powershell
   az webapp log tail --name sales-route-tracker-backend --resource-group sales-route-tracker-rg
   ```
4. **Share feedback** for improvements
5. **Celebrate** 🎉 - You've successfully deployed a production app!

## 🆘 If Something Goes Wrong

### Check Backend Logs
```powershell
az webapp log tail --name sales-route-tracker-backend --resource-group sales-route-tracker-rg
```

### Check Frontend Logs
```powershell
az webapp log tail --name sales-route-tracker-frontend --resource-group sales-route-tracker-rg
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "Cannot reach backend" | Check CORS_ORIGINS in backend config |
| "Database connection failed" | Verify DATABASE_URL and firewall rules |
| "Auth fails" | Check redirect URI in Azure App Registration |
| "Frontend 404" | Check that frontend was deployed |

### Get Help

1. Check [AZURE_QUICKSTART.md](AZURE_QUICKSTART.md) troubleshooting
2. Check [AZURE_DEPLOYMENT_GUIDE.md](AZURE_DEPLOYMENT_GUIDE.md) for details
3. View [Azure Documentation](https://learn.microsoft.com/azure/)
4. Check app logs in Azure Portal

---

**Total deployment time**: ~30-45 minutes (first time)
**Cost**: ~$30-40/month
**Result**: Production-ready sales tracking app accessible from your phone! 📱✅

---

## 📞 After Deployment Support

### URLs to Remember

| Service | URL |
|---------|-----|
| Your App | `https://sales-route-tracker-frontend.azurewebsites.net` |
| API Docs | `https://sales-route-tracker-backend.azurewebsites.net/docs` |
| Health | `https://sales-route-tracker-backend.azurewebsites.net/health` |
| Portal | `https://portal.azure.com` |

### Important Files

- `.env.production` - Your configuration (keep secure!)
- Database password - Stored somewhere safe?
- Client secret - From Azure App Registration
- Connection string - For emergency database access

### Keep Secure

🔒 Never share:
- Database password
- CLIENT_SECRET
- Connection strings
- API keys

---

**Date Deployed**: _______________

**Deployed By**: _______________

**Notes**: _________________________________

---

Good luck! You've got this! 🚀
