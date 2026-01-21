# 📚 Deployment Files & Documentation

This directory contains everything you need to deploy to Azure. Here's what each file does:

## 🚀 Quick Start (Recommended)

**Start here if you're in a hurry:**

- **[AZURE_QUICKSTART.md](AZURE_QUICKSTART.md)** - 5-minute setup guide with all steps

## 📖 Detailed Guides

Choose one based on your preference:

### For Command-Line Users (Fastest)

- **[AZURE_DEPLOYMENT_GUIDE.md](AZURE_DEPLOYMENT_GUIDE.md)** - Complete Azure CLI reference guide with all commands

### For Azure Portal Users (Visual)

- **[AZURE_MANUAL_SETUP.md](AZURE_MANUAL_SETUP.md)** - Step-by-step guide using Azure Portal UI

## 🛠️ Automation Scripts

These scripts automate the deployment process:

### PowerShell Scripts (Windows)

```powershell
# 1. Create all Azure resources (database, app service, registry, etc.)
.\deploy-to-azure.ps1

# 2. Build and deploy backend to App Service
.\deploy-backend-azure.ps1

# 3. Build and deploy frontend to App Service
.\deploy-frontend-azure.ps1
```

### Bash Scripts (Mac/Linux)

```bash
# 1. Create all Azure resources
./deploy-to-azure.sh

# 2. Build and deploy backend
./deploy-backend-azure.sh

# 3. Build and deploy frontend
./deploy-frontend-azure.sh
```

## 📄 Configuration Files

- **[.env.production](.env.production)** - Template for production environment variables
- **[.env.example](.env.example)** - Template for local development

## 📊 File Reference

| File | Purpose | Platform |
|------|---------|----------|
| AZURE_QUICKSTART.md | Quick start guide (5 minutes) | All |
| AZURE_DEPLOYMENT_GUIDE.md | Complete CLI reference | All (CLI) |
| AZURE_MANUAL_SETUP.md | Step-by-step Portal guide | All (Browser) |
| deploy-to-azure.ps1 | Create Azure resources | Windows |
| deploy-to-azure.sh | Create Azure resources | Mac/Linux |
| deploy-backend-azure.ps1 | Deploy backend container | Windows |
| deploy-backend-azure.sh | Deploy backend container | Mac/Linux |
| deploy-frontend-azure.ps1 | Deploy frontend app | Windows |
| deploy-frontend-azure.sh | Deploy frontend app | Mac/Linux |
| .env.production | Production config template | All |

## 🎯 Recommended Path

### If you're new to Azure:
1. Read [AZURE_QUICKSTART.md](AZURE_QUICKSTART.md)
2. Run the PowerShell scripts (or Bash if on Mac/Linux)
3. Follow the prompts

### If you want to understand everything:
1. Read [AZURE_DEPLOYMENT_GUIDE.md](AZURE_DEPLOYMENT_GUIDE.md) for all details
2. Choose to use CLI commands or Portal
3. Adapt as needed for your setup

### If you prefer UI over command-line:
1. Read [AZURE_MANUAL_SETUP.md](AZURE_MANUAL_SETUP.md)
2. Go through each step in Azure Portal
3. Deploy manually via Portal

## 💡 What Each Script Does

### deploy-to-azure.ps1 (or .sh)

Creates all the basic infrastructure:
- ✅ Resource Group (container for all resources)
- ✅ PostgreSQL Database (data storage)
- ✅ App Service Plan (compute plan)
- ✅ Backend App Service (where your API runs)
- ✅ Container Registry (stores Docker images)
- ✅ Managed Identity (secure authentication)

**Time**: 10-15 minutes
**Cost**: Starts using your Azure quota

### deploy-backend-azure.ps1 (or .sh)

Deploys your backend API:
- ✅ Builds Docker image from your code
- ✅ Pushes to Container Registry
- ✅ Configures App Service to use the image
- ✅ Starts the application

**Time**: 3-5 minutes
**Requires**: Docker, Azure CLI login, created resources from Step 1

### deploy-frontend-azure.ps1 (or .sh)

Deploys your React frontend:
- ✅ Installs npm dependencies
- ✅ Builds optimized production build
- ✅ Uploads to App Service
- ✅ Application becomes accessible

**Time**: 2-3 minutes
**Requires**: Node.js, created resources from Step 1

## 🔐 Security Notes

- Never commit `.env` file to Git - it contains secrets
- Use `.env.production` as a template only
- Keep CLIENT_SECRET safe - don't share it
- Use strong database password (20+ characters recommended)
- Firewall rules restrict database access by default
- All communication uses HTTPS in cloud deployment

## 💰 Cost Estimate

| Service | Monthly Cost | Notes |
|---------|--------------|-------|
| PostgreSQL DB (B1ms) | $15-20 | Flexible server, always-free tier available |
| App Service (B1) | $10-15 | Linux, can stop to reduce costs |
| Container Registry | $5 | Basic tier |
| Static Web Apps | $0-5 | If using free tier |
| **Total** | **~$30-40** | First month may be free with Azure credits |

**Money-saving tips:**
- Use Azure free tier ($200 credits for 30 days)
- Get 12 months of free services
- Stop app services when not in use
- Delete resources you don't need

## 🆘 Troubleshooting

### Scripts not running
```powershell
# Windows: Allow scripts to run
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Command not found errors
- Install Azure CLI: https://learn.microsoft.com/cli/azure/install-azure-cli
- Install Docker: https://www.docker.com/products/docker-desktop
- Install Node.js: https://nodejs.org/

### Not logged into Azure
```powershell
az login
```

### Resource already exists
Each resource name must be unique. If you get "already exists" error:
- Use a different name in the scripts
- Or delete the existing resource and try again

## 📞 Next Steps After Deployment

1. ✅ Your app is live!
2. 🌐 Access from phone: `https://sales-route-tracker-frontend.azurewebsites.net`
3. 🔑 Sign in with Microsoft account
4. 📊 Sync your Excel file from OneDrive
5. 📱 Start tracking sales from anywhere!

## 📖 Additional Resources

- [Azure Documentation](https://learn.microsoft.com/azure/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Azure CLI Reference](https://learn.microsoft.com/cli/azure/reference-index)

---

**Questions?** Check the troubleshooting section in each guide or see [AZURE_DEPLOYMENT_GUIDE.md](AZURE_DEPLOYMENT_GUIDE.md)

Good luck! 🚀
